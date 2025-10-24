1. [test_clubs_get_user_club.py](test_clubs_get_user_club.py)
   - `test_get_user_club_returns_owned_club`: ensures `_get_user_club` returns the club owned by the user.
   - `test_get_user_club_returns_none_when_user_has_no_club`: confirms the helper yields `None` when the user is not attached to any club.

2. [test_signup_flow.py](test_signup_flow.py)
   - `test_signup_creates_user_with_email`: verifies the HTML signup form creates the user and logs them in.
   - `test_api_signup_creates_user_via_json`: checks the JSON signup endpoint creates the user and opens the session.
   - `test_api_create_club_generates_club`: confirms the club-creation endpoint persists the club and seeds the initial roster.

3. [test_extract_player_id.py](test_extract_player_id.py)
   - `test_extract_player_id_supported_inputs`: validates that `extract_player_id` handles all supported payload formats.
   - `test_extract_player_id_handles_bad_data`: asserts that `extract_player_id` falls back to `None` on noisy data.

4. [test_club_services.py](test_club_services.py)
   - `test_generate_initial_players_creates_expected_roster`: exercises `generate_initial_players`.
     * creates exactly 16 players bound to the club;
     * guarantees every `(first_name, last_name)` pair is unique;
     * matches the position distribution template (2 GK, 3 CB, 4 CM, etc.);
     * verifies each player has class 4 and age 17.

5. [test_player_utils.py](test_player_utils.py)
   - `test_generate_player_stats_structure`: проверяет набор полей и диапазон значений для вратаря и нападающего.
   - `test_generate_player_stats_position_modifiers`: сравнивает модификаторы для защитника и нападающего.
   - `test_generate_player_stats_class_modifier`: убеждается, что класс игрока влияет на средний уровень характеристик.

6. [test_player_models.py](test_player_models.py)
   - `test_get_player_line`: проверяет, что `get_player_line` корректно классифицирует игрока по линии (GK/DEF/MID/FWD) для популярных и fallback‑позиций.

7. [test_training_logic.py](test_training_logic.py)
   - `test_calculate_training_points`: проверяет, как `calculate_training_points` учитывает возрастной модификатор, бонус bloom и нижнюю границу набора очков.
