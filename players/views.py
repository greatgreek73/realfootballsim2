from django.views.generic import DetailView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random

from .models import Player


class PlayerDetailView(DetailView):
    """
    Отображение детальной информации об игроке.
    Шаблон: players/player_detail.html
    """
    model = Player
    template_name = 'players/player_detail.html'


@login_required
def boost_player(request, player_id):
    """
    Повышает характеристики игрока за токены.
    1-я тренировка бесплатная, 2-я — 1 токен, 3-я — 2, 4-я — 4, и т. д.

    Шаги:
      - Проверяем, что запрос POST (иначе редиректим обратно).
      - Из POST берем 'group' — выбранную группу характеристик.
      - Узнаём стоимость (cost = player.get_boost_cost()).
      - Если user.tokens < cost, выходим с ошибкой.
      - Иначе списываем токены (user.tokens -= cost).
      - +3 очка к выбранной группе (либо +1 каждому атрибуту, 
        либо рандомно распределённые 3 очка).
      - +2 очка к другим характеристикам (исключая выбранную группу).
      - player.boost_count += 1, сохраняем.
    """
    player = get_object_or_404(Player, pk=player_id)
    user = request.user  # Предполагается, что у CustomUser есть поле 'tokens'

    # Только POST-запрос должен обрабатывать логику
    if request.method == 'POST':
        group_name = request.POST.get('group', '').strip()
        if not group_name:
            messages.error(request, "Не выбрана группа характеристик для улучшения.")
            return redirect('players:player_detail', pk=player_id)

        # Цена следующей тренировки
        cost = player.get_boost_cost()

        # Проверяем, хватает ли токенов
        if user.tokens < cost:
            messages.error(request, f"Недостаточно токенов. Нужно {cost}, а у вас {user.tokens}.")
            return redirect('players:player_detail', pk=player_id)

        # Определяем нужный словарь групп (вратарь / полевой)
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

        # +3 очка к атрибутам выбранной группы
        attrs_in_group = group_dict[group_name]

        # Простой вариант: +1 ко всем атрибутам в группе (если там ровно 3 атрибута)
        for attr_name in attrs_in_group:
            current_val = getattr(player, attr_name, 0)
            setattr(player, attr_name, current_val + 1)

        # Если хотите рандомно распределить 3 очка по группе, используйте такой вариант:
        """
        for _ in range(3):
            rand_attr = random.choice(attrs_in_group)
            cur_val = getattr(player, rand_attr, 0)
            setattr(player, rand_attr, cur_val + 1)
        """

        # +2 очка к другим характеристикам
        if player.is_goalkeeper:
            all_attrs = list(set(sum(Player.GOALKEEPER_GROUPS.values(), ())))
        else:
            all_attrs = list(set(sum(Player.FIELD_PLAYER_GROUPS.values(), ())))

        other_attrs = [a for a in all_attrs if a not in attrs_in_group]

        for _ in range(2):
            rand_attr = random.choice(other_attrs)
            cur_val = getattr(player, rand_attr, 0)
            setattr(player, rand_attr, cur_val + 1)

        # Увеличиваем счётчик тренировок
        player.boost_count += 1
        player.save()

        messages.success(request,
                         f"Характеристики игрока успешно улучшены! "
                         f"Тренировка стоила {cost} токенов.")
        # Возвращаемся на страницу игрока (с namespace='players')
        return redirect('players:player_detail', pk=player_id)

    # Не POST => просто редиректим на детальную страницу игрока
    return redirect('players:player_detail', pk=player_id)
