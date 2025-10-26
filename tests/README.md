1. [test_clubs_get_user_club.py](test_clubs_get_user_club.py)
   - `test_get_user_club_returns_owned_club`: проверяет, что `_get_user_club` возвращает клуб, принадлежащий пользователю.
   - `test_get_user_club_returns_none_when_user_has_no_club`: подтверждает, что помощник возвращает `None`, если у пользователя нет клуба.

2. [test_signup_flow.py](test_signup_flow.py)
   - `test_signup_creates_user_with_email`: проверяет, что HTML-форма регистрации создает пользователя и тут же авторизует его.
   - `test_api_signup_creates_user_via_json`: удостоверяется, что JSON-эндпоинт регистрации создает пользователя и открывает сессию.
   - `test_api_create_club_generates_club`: подтверждает, что эндпоинт создания клуба сохраняет клуб и генерирует стартовый состав.

3. [test_extract_player_id.py](test_extract_player_id.py)
   - `test_extract_player_id_supported_inputs`: проверяет, что `extract_player_id` поддерживает все форматы полезной нагрузки.
   - `test_extract_player_id_handles_bad_data`: убеждается, что `extract_player_id` возвращает `None` при шумных данных.

4. [test_club_services.py](test_club_services.py)
   - `test_generate_initial_players_creates_expected_roster`: проверяет `generate_initial_players`.
     * создает ровно 16 игроков, привязанных к клубу;
     * гарантирует уникальность каждой пары `(first_name, last_name)`;
     * совпадает с шаблоном распределения позиций (2 GK, 3 CB, 4 CM и т.д.);
     * убеждается, что каждый игрок имеет класс 4 и возраст 17.

5. [test_player_utils.py](test_player_utils.py)
   - `test_generate_player_stats_structure`: проверяет, что блок сгенерированных характеристик содержит все ожидаемые категории и атрибуты.
   - `test_generate_player_stats_position_modifiers`: подтверждает, что позиционные модификаторы применяются к базовым характеристикам.
   - `test_generate_player_stats_class_modifier`: убеждается, что модификатор класса корректирует итоговые значения атрибутов.

6. [test_player_models.py](test_player_models.py)
   - `test_get_player_line`: проверяет, что `get_player_line` правильно относит игрока к линиям GK/DEF/MID/FWD и использует ожидаемый запасной вариант.

7. [test_training_logic.py](test_training_logic.py)
   - `test_get_or_create_training_settings_creates_and_reuses_instance`: проверяет, что при первом обращении создаются настройки тренировки и последующие вызовы возвращают ту же запись.
   - `test_conduct_player_training_returns_summary`: убеждается, что персональная тренировка возвращает сводку, включает запуск bloom и фиксирует изменения атрибутов.
   - `test_calculate_training_points`: проверяет, что `calculate_training_points` рассчитывает суммарные очки с учетом bloom и возрастного модификатора.
   - `test_distribute_training_points_field_player`: подтверждает, что `distribute_training_points` распределяет очки между заданными группами полевого игрока.
   - `test_apply_training_to_player_increases_attributes`: удостоверяется, что `apply_training_to_player` повышает отслеживаемые атрибуты и сохраняет изменения.
   - `test_apply_training_to_player_may_reduce_for_older_players`: демонстрирует, что у возрастных игроков тренировка при штрафах может уменьшать характеристики.

8. [test_player_tasks.py](test_player_tasks.py)
   - `test_is_training_day`: проверяет, что `is_training_day` возвращает `True` для понедельника/среды/пятницы и `False` для остальных дней.
9. [test_accounts_api.py](test_accounts_api.py)
   - `test_password_reset_serializer_requires_existing_email`: проверяет, что сериализатор сброса пароля принимает только существующие адреса и отклоняет неизвестные.
   - `test_password_reset_confirm_serializer_validates_token`: подтверждает, что сериализатор проверки пароля валидирует пару uid/token и возвращает пользователя; `test_password_reset_confirm_serializer_rejects_mismatched` ловит несовпадение паролей.
   - `test_password_reset_view_sends_email`: удостоверяется, что API сброса отправляет письмо с рабочей ссылкой; `test_password_reset_view_returns_reset_url_in_debug` показывает возврат URL при ошибке отправки в DEBUG.
   - `test_password_reset_confirm_view_updates_password`: проверяет, что подтверждение сброса действительно меняет пароль пользователя.
   - `test_password_reset_validate_token_endpoint`: дергает проверку токена через API и сравнивает ответы для корректного и некорректного ввода.
   - `test_user_serializer_has_club_flag`: убеждается, что `UserSerializer` верно расставляет флаг наличия клуба.
   - `test_register_serializer_*`: показывает, что сериализатор регистрации блокирует дубли email, ловит несостыковку паролей и создаёт пользователя с хешированным паролем.
   - `test_login_allows_email_and_returns_user_payload`: проверяет вход по email и наличие пользовательского payload в ответе с JWT.
   - `test_register_view_returns_errors_for_invalid_payload`: подтверждает ответ 400 при некорректной нагрузке в API регистрации.
   - `test_logout_view_handles_missing_and_invalid_refresh`: демонстрирует требование refresh-токена, отказ для битого значения и успешный блэклист валидного токена.
   - `test_user_view_returns_current_user_data`: убеждается, что профиль возвращает данные авторизованного пользователя.

10. [test_accounts_management.py](test_accounts_management.py)
    - `test_create_test_user_creates_account`: проверяет, что management-команда создаёт тестового пользователя с ожидаемыми полями и паролем.
    - `test_create_test_user_updates_existing_account`: подтверждает, что команда обновляет существующую запись и сбрасывает пароль, tokens и money до дефолтов.
11. [test_transfers_forms.py](test_transfers_forms.py)
    - `test_transfer_listing_form_rejects_price_below_player_value`: проверяет, что форма листинга не пропускает цену ниже базовой стоимости игрока.
    - `test_transfer_listing_form_accepts_valid_payload`: удостоверяется, что корректные данные сохраняются и привязываются к игроку.
    - `test_transfer_offer_form_requires_listing_and_club`: проверяет, что форма ставки требует контекст аукциона (листинг и клуб).
    - `test_transfer_offer_form_validates_bid_amount_and_balance`: убеждается, что ставка не может быть ниже запрошенной цены и проходит при достаточном балансе.
    - `test_transfer_offer_form_flags_insufficient_funds`: фиксирует ошибку при нехватке средств у клуба-покупателя.

12. [test_transfers_models.py](test_transfers_models.py)
    - `test_transfer_listing_*`: покрывает ключевые сценарии листинга (создание срока, отмена/завершение/истечение, выбор лучшей ставки).
    - `test_transfer_offer_save_triggers_extend_for_new_pending_offer`: проверяет автопродление аукциона при новой ставке.
    - `test_transfer_offer_extend_auction_if_needed_extends_when_under_threshold`: убеждается, что срок продлевается только при малом остатке времени.
    - `test_transfer_offer_accept_success_flow`: проверяет успешный трансфер игрока, движение средств и запись истории.
    - `test_transfer_offer_accept_fails_when_insufficient_funds` и `test_transfer_offer_reject_and_cancel`: контролируют отказ и отмену ставки.

13. [test_transfers_views.py](test_transfers_views.py)
    - `test_transfer_market_lists_active_offers`: проверяет фильтрацию активных листингов на рынке.
    - `test_transfer_listing_detail_*`: покрывает экран деталей как для продавца, так и для покупателя.
    - `test_create_transfer_listing_get_and_post`: удостоверяется, что форма рендерится и создаёт листинг.
    - `test_club_transfers_view_context`: контролирует состав данных дашборда клуба.
    - `test_cancel_transfer_listing_redirects`, `test_cancel_transfer_offer_redirects`, `test_accept_transfer_offer_redirects`: проверяют информационные редиректы.
    - `test_reject_transfer_offer_requires_seller`: проверяет права и смену статуса при отклонении ставки.
    - `test_transfer_history_filters`: убеждается, что фильтрация по сезону/клубу отрабатывает без ошибок.
    - `test_expire_transfer_listing_requires_expired_active_listing`: прогоняет API завершения аукциона с победителем и без него.
    - `test_get_listing_info_returns_expected_payload`: проверяет выдачу таймера и ставки для активного/неактивного листинга.

14. [test_transfers_template_tags.py](test_transfers_template_tags.py)
    - `test_get_item_returns_value_or_none`: убеждается, что шаблонный фильтр безопасно достаёт значения из словаря.
15. [test_tournaments_season.py](test_tournaments_season.py)
    - `test_season_clean_requires_first_day_of_month`: проверяет, что дата начала сезона строго первый день месяца.
    - `test_season_clean_requires_month_end`: убеждается, что дата окончания совпадает с последним числом месяца.
    - `test_season_clean_passes_for_valid_dates`: подтверждает отсутствие ошибок при корректных границах.
    - `test_season_february_helpers`: покрывает свойства `is_february` и `needs_double_matchday`.
    - `test_season_get_double_matchday_dates_returns_expected_values`: проверяет даты двойных туров.
    - `test_season_save_assigns_name_if_missing`: убеждается, что `save` автогенерирует название.
    - `test_create_next_season_increments_number_and_uses_date_provider`: тестирует `create_next_season` с заглушкой календаря.
16. [test_tournaments_tasks.py](test_tournaments_tasks.py)
    - test_check_season_end_creates_new_season, test_check_season_end_skips_if_not_ready, test_check_season_end_creates_initial_if_none: покрывают Celery-задачу завершения сезона.
    - test_extract_player_ids_from_lineup_handles_values: извлекает идентификаторы игроков из различных форматов лайнапа.
    - test_complete_lineup_*: дополняют состав клуба и обрабатывают нехватку игроков.
    - test_start_scheduled_matches_*: убеждаются, что матчи переходят в in_progress или пропускаются при неполных составах.
    - test_advance_match_minutes_*: контролируют обновление минуты, создание событий и реакцию при отсутствии матчей.
17. [test_clubs_lineup.py](test_clubs_lineup.py)
    - `test_save_team_lineup_persists_lineup`: проверяет успешное сохранение состава через API.
    - `test_save_team_lineup_rejects_more_than_eleven`: удостоверяется, что сервер не принимает более 11 игроков.
    - `test_save_team_lineup_requires_goalkeeper`: требует наличие вратаря в составе.
    - `test_save_team_lineup_rejects_foreign_player`: отклоняет игроков чужих клубов.
    - `test_get_team_lineup_returns_players`: возвращает сохранённый состав с данными игроков.
    - `test_get_team_lineup_denies_foreign_user`: запрещает доступ к данным чужого клуба.

18. [test_matches_lineup.py](test_matches_lineup.py)
    - `test_get_lineup_from_club_returns_full_lineup`: проверяет чтение сохранённого состава клуба.
    - `test_get_lineup_from_club_returns_none_for_invalid`: удостоверяется, что неполные данные игнорируются.
    - `test_auto_select_lineup_produces_442`: тестирует автоматическое формирование схемы 4-4-2.
    - `test_extract_player_id_handles_multiple_formats`: покрывает универсальный извлекатель ID.

19. [test_match_simulation_utils.py](test_match_simulation_utils.py)
    - `test_clamp*`: проверяет ограничение значений clamp/clamp_int.
    - `test_zone_prefix_and_side`, `test_mirror_side`, `test_make_zone_handles_goalkeeper`: фиксируют логику разбора и зеркалирования зон.
    - `test_random_adjacent_zone_*`, `test_forward_dribble_zone_*`, `test_next_zone`: гарантируют корректные переходы между зонами поля.
    - `test_mirrored_zone`, `test_zone_conditions_mapping`: проверяют зеркальные зоны и фильтрацию игроков по позициям.

20. [test_match_simulation_probabilities.py](test_match_simulation_probabilities.py)
    - `test_pass_success_probability_*`: показывает рост шанса паса и особый случай GK->DEF.
    - `test_shot_success_probability_respects_goalkeeper`, `test_long_shot_probability_lower_than_regular`: сопоставляют эффективность ударов.
    - `test_foul_probability_*`, `test_dribble_success_probability_*`: фиксируют границы и монотонность фолов и дриблинга.

21. [test_match_simulation_morale.py](test_match_simulation_morale.py)
    - `test_*_multiplier`, `test_calculate_morale_change_*`: проверяют мультипликаторы времени/счёта/зоны и клампы ±15.
    - `test_apply_*_morale_change`, `test_recover_morale_gradually_moves_towards_base`: подтверждают корректное изменение и восстановление морали.
    - `test_apply_team_morale_effect_*`: проверяют применение событий ко всей команде (dict/строка).
    - `test_update_and_get_team_momentum`: гарантирует обновление моментума.

22. [test_match_simulation_lineups.py](test_match_simulation_lineups.py)
    - `test_choose_player*`, `test_choose_players_respects_exclude`: покрывают выбор игрока из лайнапа (строка/словарь) с учётом веса positioning.
    - `test_ensure_match_lineup_set_*`: подтверждают дописывание состава и отказ при невозможности complete_lineup.
    - `test_auto_select_lineup_*`: документируют работу auto_select_lineup и обработку исключений.
    - `test_send_update_*`: фиксируют контракт WebSocket (payload, st_possessions, отсутствие channel layer).

23. [test_match_simulation_actions.py](test_match_simulation_actions.py)
    - `test_simulate_one_action_*`: интеграционные сценарии — старт от GK, гол, промах, пас, перехват, дриблинг, отсутствие получателя, длинный пас, дальний удар.
    - `test_simulate_active_matches_smoke`: дымовая проверка фоновой задачи simulate_active_matches.
    - `test_get_opponent_team_returns_home_when_missing`: подтверждает fallback helper-а.

24. [test_tournaments_utils.py](test_tournaments_utils.py)
    - `test_check_consecutive_matches`, `test_get_team_matches_returns_sorted_rounds`, `test_validate_schedule_balance_counts_home_and_away`: проверяют базовые утилиты расписания.
    - `test_generate_league_schedule_*`: утверждают структуру двойного круга и ограничение на 16 команд.
    - `test_create_championship_matches_*`: проверяют генерацию матчей, очистку и сдвиг времени для второго дивизиона.
    - `test_validate_championship_schedule_*`: покрывают валидатор для корректного и нарушенного расписания.
