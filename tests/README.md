1. [test_clubs_get_user_club.py](test_clubs_get_user_club.py)
   - `test_get_user_club_returns_owned_club`: проверяет, что `_get_user_club` возвращает клуб владельца.
   - `test_get_user_club_returns_none_when_user_has_no_club`: убеждается, что при отсутствии клуба функция отдаёт `None`.

2. [test_signup_flow.py](test_signup_flow.py)
   - `test_signup_creates_user_with_email`: HTML-форма регистрации создаёт пользователя и логинит его.
   - `test_api_signup_creates_user_via_json`: JSON API регистрации создаёт пользователя и авторизует сессию.
   - `test_api_create_club_generates_club`: API создания клуба записывает клуб и стартовый состав.

3. [test_extract_player_id.py](test_extract_player_id.py)
   - `test_extract_player_id_supported_inputs`: `extract_player_id` корректно обрабатывает поддерживаемые форматы.
   - `test_extract_player_id_handles_bad_data`: `extract_player_id` возвращает `None` для шумовых значений.
