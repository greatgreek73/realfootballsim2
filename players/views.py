from django.views.generic import DetailView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import random

from .models import Player


class PlayerDetailView(DetailView):
    model = Player
    template_name = 'players/player_detail.html'


@login_required
def boost_player(request, player_id):
    """
    Повышает характеристики игрока за токены. 
    1-я тренировка бесплатная, вторая — 1 токен, третья — 2, затем 4, 8 и т.д.
    
    Логика:
      - Пользователь в POST-запросе указывает 'group' (одну из групп FIELD_PLAYER_GROUPS или GOALKEEPER_GROUPS)
      - Проверяем, хватает ли токенов у пользователя (request.user.tokens)
      - Списываем токены
      - +3 очка к выбранной группе
      - +2 очка рандомно к другим характеристикам
      - Увеличиваем счётчик boost_count
    """
    # Получаем игрока или 404
    player = get_object_or_404(Player, pk=player_id)
    user = request.user  # Предположим, CustomUser имеет поле 'tokens'

    # Разрешаем операцию только при POST-запросе
    if request.method == 'POST':
        # Получаем из формы группу характеристик
        group_name = request.POST.get('group', '').strip()
        if not group_name:
            messages.error(request, "Не выбрана группа характеристик для улучшения.")
            return redirect('player_detail', pk=player_id)

        # Определяем текущую стоимость
        cost = player.get_boost_cost()  # из модели Player

        # Проверяем баланс токенов
        if user.tokens < cost:
            messages.error(request, f"Недостаточно токенов. Нужно {cost}, а у вас {user.tokens}.")
            return redirect('player_detail', pk=player_id)

        # Определяем, какую «группу словарей» использовать — вратарская / полевые
        if player.is_goalkeeper:
            group_dict = Player.GOALKEEPER_GROUPS
        else:
            group_dict = Player.FIELD_PLAYER_GROUPS

        # Проверяем, есть ли такая группа в словаре
        if group_name not in group_dict:
            messages.error(request, "Некорректная группа характеристик.")
            return redirect('player_detail', pk=player_id)

        # Списываем токены
        user.tokens -= cost
        user.save()

        # Основная группа для +3 очков
        attrs_in_group = group_dict[group_name]

        # Простейший вариант: +1 к каждому атрибуту в группе, если их ровно 3
        for attr_name in attrs_in_group:
            current_val = getattr(player, attr_name, 0)
            setattr(player, attr_name, current_val + 1)

        # Альтернативно (раскомментируйте, если хотите случайного распределения 3 очков):
        """
        import random
        for _ in range(3):
            rand_attr = random.choice(attrs_in_group)
            current_val = getattr(player, rand_attr, 0)
            setattr(player, rand_attr, current_val + 1)
        """

        # +2 очка к другим характеристикам
        if player.is_goalkeeper:
            all_attrs = list(set(sum(Player.GOALKEEPER_GROUPS.values(), ())))
        else:
            all_attrs = list(set(sum(Player.FIELD_PLAYER_GROUPS.values(), ())))

        # Исключаем те, что входят в выбранную группу
        other_attrs = [a for a in all_attrs if a not in attrs_in_group]

        for _ in range(2):
            rand_attr = random.choice(other_attrs)
            current_val = getattr(player, rand_attr, 0)
            setattr(player, rand_attr, current_val + 1)

        # Увеличиваем счётчик тренировок
        player.boost_count += 1

        # Сохраняем изменения
        player.save()

        messages.success(request,
                         f"Характеристики игрока успешно улучшены! "
                         f"Стоимость этой тренировки: {cost} токенов.")
        return redirect('player_detail', pk=player_id)

    # Если не POST-запрос — редиректим обратно на детальную страницу
    return redirect('player_detail', pk=player_id)
