import json
import random

from django.views.generic import DetailView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import models
from decimal import Decimal

from .models import Player, TrainingSettings
from matches.models import CharacterEvolution, PlayerRivalry, TeamChemistry, NarrativeEvent


class PlayerDetailView(DetailView):
    """
    Отображение детальной информации об игроке.
    Шаблон: players/player_detail.html
    """
    model = Player
    template_name = 'players/player_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = self.object
        
        # Check if personality engine is enabled
        from django.conf import settings
        context['personality_engine_enabled'] = getattr(settings, 'USE_PERSONALITY_ENGINE', False)
        
        if context['personality_engine_enabled'] and player.personality_traits:
            # Character Evolution History
            context['character_evolutions'] = CharacterEvolution.objects.filter(
                player=player
            ).select_related('match').order_by('-timestamp')[:10]
            
            # Active Rivalries
            context['rivalries'] = PlayerRivalry.objects.filter(
                models.Q(player1=player) | models.Q(player2=player)
            ).select_related('player1', 'player2')
            
            # Team Chemistry Connections
            context['chemistry_connections'] = TeamChemistry.objects.filter(
                models.Q(player1=player) | models.Q(player2=player)
            ).select_related('player1', 'player2')
            
            # Recent Narrative Events
            context['narrative_events'] = NarrativeEvent.objects.filter(
                models.Q(primary_player=player) | models.Q(secondary_player=player)
            ).select_related('match').order_by('-timestamp')[:10]
        
        return context


@login_required
def boost_player(request, player_id):
    """
    (Старый метод) Повышает характеристики игрока за токены (через обычный POST).
    Делает redirect обратно на страницу игрока.
    """
    player = get_object_or_404(Player, pk=player_id)
    user = request.user

    # Проверяем, является ли пользователь владельцем клуба
    if player.club and player.club.owner != user:
        messages.error(request, "У вас нет прав на улучшение этого игрока.")
        return redirect('players:player_detail', pk=player_id)

    if request.method == 'POST':
        group_name = request.POST.get('group', '').strip()
        if not group_name:
            messages.error(request, "Не выбрана группа характеристик для улучшения.")
            return redirect('players:player_detail', pk=player_id)

        cost = player.get_boost_cost()
        if user.tokens < cost:
            messages.error(request, f"Недостаточно токенов. Нужно {cost}, а у вас {user.tokens}.")
            return redirect('players:player_detail', pk=player_id)

        # Определяем нужный словарь групп
        if player.is_goalkeeper:
            group_dict = Player.GOALKEEPER_GROUPS
        else:
            group_dict = Player.FIELD_PLAYER_GROUPS

        if group_name not in group_dict:
            messages.error(request, "Некорректная группа характеристик.")
            return redirect('players:player_detail', pk=player_id)

        # Списываем токены
        user.tokens -= cost
        user.save()

        # +3 очка к выбранной группе
        attrs_in_group = group_dict[group_name]
        for attr_name in attrs_in_group:
            current_val = getattr(player, attr_name, 0)
            setattr(player, attr_name, current_val + 1)

        # +2 очка к другим атрибутам
        if player.is_goalkeeper:
            all_attrs = list(set(sum(Player.GOALKEEPER_GROUPS.values(), ())))
        else:
            all_attrs = list(set(sum(Player.FIELD_PLAYER_GROUPS.values(), ())))

        other_attrs = [a for a in all_attrs if a not in attrs_in_group]
        for _ in range(2):
            rand_attr = random.choice(other_attrs)
            cur_val = getattr(player, rand_attr, 0)
            setattr(player, rand_attr, cur_val + 1)

        player.boost_count += 1
        player.save()

        messages.success(request,
                         f"Характеристики игрока успешно улучшены! "
                         f"Тренировка стоила {cost} токенов.")
        return redirect('players:player_detail', pk=player_id)

    # Не POST => просто редиректим на детальную страницу
    return redirect('players:player_detail', pk=player_id)


@login_required
def boost_player_ajax(request, player_id):
    """
    Повышает характеристики игрока за токены (AJAX).
    Возвращает JSON с информацией об изменённых характеристиках.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

    player = get_object_or_404(Player, pk=player_id)
    user = request.user

    # Проверяем, является ли пользователь владельцем клуба
    if player.club and player.club.owner != user:
        return JsonResponse({
            'success': False,
            'message': "У вас нет прав на улучшение этого игрока."
        }, status=403)

    try:
        data = json.loads(request.body)
        group_name = data.get('group', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

    if not group_name:
        return JsonResponse({'success': False, 'message': 'No group selected'}, status=400)

    cost = player.get_boost_cost()
    if user.tokens < cost:
        return JsonResponse({
            'success': False,
            'message': f"Недостаточно токенов. Нужно {cost}, а у вас {user.tokens}."
        }, status=400)

    # Определяем нужный словарь групп
    if player.is_goalkeeper:
        group_dict = Player.GOALKEEPER_GROUPS
    else:
        group_dict = Player.FIELD_PLAYER_GROUPS

    if group_name not in group_dict:
        return JsonResponse({'success': False, 'message': 'Некорректная группа'}, status=400)

    # Сохраняем "старые" значения, чтобы вернуть их в ответе
    if player.is_goalkeeper:
        all_attrs = list(set(sum(Player.GOALKEEPER_GROUPS.values(), ())))
    else:
        all_attrs = list(set(sum(Player.FIELD_PLAYER_GROUPS.values(), ())))

    old_values = {}
    for a in all_attrs:
        old_values[a] = getattr(player, a, 0)

    # Списываем токены
    user.tokens -= cost
    user.save()

    # +3 очка в выбранную группу
    attrs_in_group = group_dict[group_name]
    all_changed_attrs = set()
    for attr_name in attrs_in_group:
        cur_val = getattr(player, attr_name, 0)
        setattr(player, attr_name, cur_val + 1)
        all_changed_attrs.add(attr_name)

    # +2 к другим атрибутам
    other_attrs = [a for a in all_attrs if a not in attrs_in_group]
    for _ in range(2):
        rand_attr = random.choice(other_attrs)
        cur_val = getattr(player, rand_attr, 0)
        setattr(player, rand_attr, cur_val + 1)
        all_changed_attrs.add(rand_attr)

    player.boost_count += 1
    player.save()

    changes = {}
    for attr_name in all_changed_attrs:
        old_val = old_values[attr_name]
        new_val = getattr(player, attr_name, 0)
        changes[attr_name] = {
            'old': old_val,
            'new': new_val
        }

    return JsonResponse({
        'success': True,
        'message': f"Характеристики улучшены! Тренировка стоила {cost} токенов.",
        'changes': changes,
        'next_cost': player.get_boost_cost(),
        'tokens_left': user.tokens
    })


@login_required
def delete_player(request, player_id):
    """
    Удаление игрока с подтверждением.
    """
    player = get_object_or_404(Player, pk=player_id)
    # Проверяем, является ли пользователь владельцем клуба
    if player.club and player.club.owner != request.user:
        messages.error(request, "У вас нет прав на удаление этого игрока.")
        return redirect('players:player_detail', pk=player_id)

    if request.method == 'POST':
        club_id = player.club.id if player.club else None
        player_name = f"{player.first_name} {player.last_name}"
        player.delete()

        messages.success(request, f"Игрок {player_name} успешно удалён.")
        
        if club_id:
            return redirect('clubs:club_detail', pk=club_id)
        else:
            # Если вдруг нет клуба, возвращаем на главную
            return redirect('core:home')

    # Если GET – показываем страницу подтверждения
    return render(request, 'players/player_confirm_delete.html', {'player': player})


@login_required
def training_settings(request, player_id):
    """
    Страница настройки тренировок для игрока.
    """
    player = get_object_or_404(Player, pk=player_id)
    
    # Проверяем, является ли пользователь владельцем клуба
    if player.club and player.club.owner != request.user:
        messages.error(request, "У вас нет прав на настройку тренировок этого игрока.")
        return redirect('players:player_detail', pk=player_id)
    
    # Получаем или создаем настройки тренировок
    settings, created = TrainingSettings.objects.get_or_create(
        player=player
    )
    
    context = {
        'player': player,
        'settings': settings,
        'is_goalkeeper': player.is_goalkeeper,
    }
    
    return render(request, 'players/training_settings.html', context)


@login_required
def update_training_settings(request, player_id):
    """
    AJAX обновление настроек тренировок игрока.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

    player = get_object_or_404(Player, pk=player_id)
    
    # Проверяем права доступа
    if player.club and player.club.owner != request.user:
        return JsonResponse({
            'success': False,
            'message': "У вас нет прав на настройку тренировок этого игрока."
        }, status=403)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

    # Получаем или создаем настройки
    settings, created = TrainingSettings.objects.get_or_create(
        player=player
    )

    try:
        if player.is_goalkeeper:
            # Обновляем настройки для вратаря
            settings.gk_physical_weight = Decimal(str(data.get('physical', 33.33)))
            settings.gk_core_skills_weight = Decimal(str(data.get('core_gk_skills', 33.33)))
            settings.gk_additional_skills_weight = Decimal(str(data.get('additional_gk_skills', 33.34)))
            
            # Проверяем сумму
            total = (settings.gk_physical_weight + 
                    settings.gk_core_skills_weight + 
                    settings.gk_additional_skills_weight)
        else:
            # Обновляем настройки для полевого игрока
            settings.physical_weight = Decimal(str(data.get('physical', 16.67)))
            settings.defensive_weight = Decimal(str(data.get('defensive', 16.67)))
            settings.attacking_weight = Decimal(str(data.get('attacking', 16.67)))
            settings.mental_weight = Decimal(str(data.get('mental', 16.67)))
            settings.technical_weight = Decimal(str(data.get('technical', 16.67)))
            settings.tactical_weight = Decimal(str(data.get('tactical', 16.67)))
            
            # Проверяем сумму
            total = (settings.physical_weight + settings.defensive_weight + 
                    settings.attacking_weight + settings.mental_weight + 
                    settings.technical_weight + settings.tactical_weight)

        # Проверяем, что сумма близка к 100%
        if abs(float(total) - 100.0) > 0.1:
            return JsonResponse({
                'success': False,
                'message': f'Сумма процентов должна равняться 100%. Текущая сумма: {total}%'
            }, status=400)

        settings.save()

        return JsonResponse({
            'success': True,
            'message': 'Настройки тренировок успешно обновлены!',
            'total': float(total)
        })

    except (ValueError, TypeError) as e:
        return JsonResponse({
            'success': False,
            'message': f'Неверные данные: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка при сохранении: {str(e)}'
        }, status=500)
