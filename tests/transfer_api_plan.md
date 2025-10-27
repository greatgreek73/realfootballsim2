## Transfer API & Frontend DTO Plan

### Общие принципы
- Базовый префикс: `/api/transfers/…`. Все ручки требуют аутентификации и возвращают JSON.
- Ошибки оформляются через `detail`/`errors` (401, 403, 404, 422) и переиспользуют бизнес-логику моделей (`TransferListing.time_remaining`, `get_highest_offer`, `TransferOffer.accept` и т.д.).
- Структуры данных синхронизируются с текущими Django-шаблонами (`transfers/templates/transfers/*.html`) — игрок, клуб, таймер, статистика по офферам и роли пользователя.

### 1. Рынок трансферов
- `GET /api/transfers/listings/`
  - Параметры: `page`, `page_size`, `ordering` (`expires_at`, `-expires_at`, `asking_price`, `-asking_price`), фильтры (`position`, `min_age`, `max_age`, `min_price`, `max_price`, `club_id`, `status` = active|completed|cancelled|expired).
  - Ответ:
    ```json
    {
      "results": [
        {
          "id": 12,
          "status": "active",
          "asking_price": 250,
          "highest_bid": 275,
          "listed_at": "2025-10-26T18:00:00Z",
          "expires_at": "2025-10-26T18:30:00Z",
          "time_remaining": 524.8,
          "player": {
            "id": 91,
            "full_name": "John Doe",
            "age": 23,
            "position": "Center Forward",
            "overall_rating": 78,
            "nationality": "GB"
          },
          "club": {
            "id": 5,
            "name": "Seller FC",
            "crest_url": null
          },
          "summary": {
            "offers_count": 3,
            "is_owner": false,
            "can_bid": true
          }
        }
      ],
      "count": 42,
      "page": 1,
      "page_size": 30,
      "total_pages": 2
    }
    ```

### 2. Деталка листинга
- `GET /api/transfers/listings/<listing_id>/`
  - Возвращает расширенный объект листинга, связанный список офферов и блок `permissions` для текущего пользователя.
  - Пример:
    ```json
    {
      "listing": {
        "id": 12,
        "status": "active",
        "asking_price": 250,
        "description": "Ready to move",
        "duration": 30,
        "expires_at": "2025-10-26T18:30:00Z",
        "time_remaining": 524.8,
        "player": {...},
        "club": {...},
        "summary": {
          "offers_count": 3,
          "highest_bid": 275,
          "is_owner": false,
          "can_bid": true
        }
      },
      "offers": [
        {
          "id": 310,
          "bid_amount": 275,
          "status": "pending",
          "created_at": "2025-10-26T18:05:00Z",
          "bidding_club": {"id": 8, "name": "Buyer FC"},
          "is_own_offer": true,
          "is_highest": true,
          "can_cancel": true
        }
      ],
      "permissions": {
        "is_owner": false,
        "can_bid": true,
        "can_cancel_listing": false,
        "can_accept_offers": false
      }
    }
    ```

### 3. Управление листингами
- `POST /api/transfers/listings/`
  - Тело: `{"player_id": 91, "asking_price": 250, "duration": 30, "description": "…optional…"}`.
  - Переиспользует валидацию `TransferListingForm` (принадлежность игрока клубу, минимальная стоимость, выбор длительности).
- `POST /api/transfers/listings/<listing_id>/cancel/`
  - Доступно владельцу активного листинга. Возвращает обновлённый объект.
- `POST /api/transfers/listings/<listing_id>/expire/`
  - Повторяет текущую логику `expire_transfer_listing`: автоматически применяет максимальную ставку либо завершает листинг статусом `expired`.

### 4. Офферы
- `POST /api/transfers/listings/<listing_id>/offers/`
  - Тело: `{"bid_amount": 275, "message": "optional"}`. Использует `TransferOfferForm` для проверки минимальной суммы и бюджета клуба.
  - Ответ: созданный оффер и актуальный `listing.summary`.
- `POST /api/transfers/offers/<offer_id>/cancel/`
- `POST /api/transfers/offers/<offer_id>/reject/`
- `POST /api/transfers/offers/<offer_id>/accept/`
  - При `accept` выполняется перевод денег между владельцами, смена клуба у игрока и создание записи `TransferHistory`.

### 5. История трансферов
- `GET /api/transfers/history/`
  - Параметры: `season_id`, `club_id`, `player_id`, `page`, `page_size`, `ordering` (`-transfer_date` по умолчанию).
  - Ответ:
    ```json
    {
      "results": [
        {
          "id": 481,
          "player": {"id": 91, "full_name": "John Doe", "position": "Center Forward"},
          "from_club": {"id": 5, "name": "Seller FC"},
          "to_club": {"id": 8, "name": "Buyer FC"},
          "transfer_fee": 275,
          "transfer_date": "2025-10-26T18:07:00Z",
          "season": {"id": 3, "name": "2025/26"}
        }
      ],
      "count": 18,
      "page": 1,
      "page_size": 20,
      "total_pages": 1
    }
    ```

### 6. Общие DTO для фронтенда
- `TransferPlayer`: `id`, `full_name`, `position`, `age`, `overall_rating`, `nationality`, `club_id`.
- `TransferClub`: `id`, `name`, `crest_url?`, `owner_id?`.
- `TransferListing`: объединяет `player`, `club`, цену, тайминги, статус и краткую статистику (`highest_bid`, `offers_count`, `permissions`).
- `TransferOffer`: `id`, `bid_amount`, `status`, `created_at`, `bidding_club`, `is_own_offer`, `is_highest`, `can_cancel`.
- `TransferHistoryEntry`: игрок, исходный/новый клуб, сумма, дата, сезон.
- Эти структуры рассчитаны на MUI-компоненты (таблицы, карточки, панели действий) по аналогии со страницами игроков и клуба.


### 7. Backend Test Plan
1. **Аутентификация и 401** — провал запросов без авторизации ко всем эндпоинтам (`listings` list/detail/create/cancel/expire, ручки офферов, `history`) с JSON-ответом `{"detail": "Authentication required"}`.
2. **GET `/api/transfers/listings/`** — базовый сценарий отдаёт активные листинги; отдельные тесты для фильтров (`position`, возраст, цена, `club_id`, `status`), пагинации (`page`, `page_size`) и сортировки (`ordering`). Проверка отсутствия неактивных записей по умолчанию.
3. **GET `/api/transfers/listings/<id>/`** — различие контекста продавца/покупателя (поле `permissions`, видимость офферов), контроль `time_remaining` и `offers_count`, 404 для несуществующего ID.
4. **POST `/api/transfers/listings/`** — успешное создание (валидация минимальной цены и принадлежности игрока), ошибки: чужой игрок, цена ниже `get_purchase_cost`, повторный листинг, некорректная длительность. Ожидается код 422 с детальными ошибками формы.
5. **POST `/api/transfers/listings/<id>/cancel/`** — продавец отменяет активный листинг (статус `cancelled`, pending-офферы → `cancelled`), повторное обращение даёт 400/422, чужой листинг — 403.
6. **POST `/api/transfers/listings/<id>/expire/`** — без офферов статус `expired`; с наивысшей ставкой — проверка, что `TransferOffer.accept` переводит игрока, обновляет деньги владельцев и создаёт `TransferHistory`. Дополнительно — сценарий продления аукциона (вызов `extend_auction_if_needed` при `time_remaining < 30`).
7. **POST `/api/transfers/listings/<id>/offers/`** — успешная ставка другого клуба, ошибки: ставка ниже `asking_price`, недостаточно средств у владельца, попытка продавца сделать ставку, неактивный листинг. Проверка, что ответ обновляет `listing.summary.highest_bid`.
8. **POST `/api/transfers/offers/<id>/cancel/`** — владелец pending-оффера отменяет его; повтор или чужой оффер → 403; завершённый оффер → 400/422.
9. **POST `/api/transfers/offers/<id>/reject/`** — продавец отклоняет pending; несоблюдение прав либо неверный статус возвращает 403/422.
10. **POST `/api/transfers/offers/<id>/accept/`** — продавец принимает pending: проверка статусов (`accepted`, `completed`), переводов, блокировки остальных офферов, записи в `TransferHistory`, обработка недостатка средств (422). Повторное принятие и чужие запросы → 403/422.
11. **GET `/api/transfers/history/`** — выдаёт отсортированную историю, фильтры `season_id`/`club_id`/`player_id`, корректная сериализация поля `season`. Подтверждает, что импорт `Season` во вьюхе оформлен корректно (больше не нужно патчить в тестах).
12. **Модельные проверки** — расширить `tests/test_transfers_models.py`: отдельные кейсы для `TransferOffer.extend_auction_if_needed`, автозаполнения `TransferListing.expires_at`, консистентности `time_remaining`.
13. **Фикстуры** — обновить `tests/conftest.py`: фабрики клубов/игроков с балансами владельцев, активный сезон, вспомогательный `api_client` для авторизованных запросов.


### 8. Frontend Implementation Plan
1. **API-клиент и типы** — создать `frontend/src/api/transfers.ts` по образцу `matches.ts`: функции `fetchTransferListings`, `fetchTransferListing`, `createTransferListing`, `cancelTransferListing`, `expireTransferListing`, `createTransferOffer`, `cancelTransferOffer`, `rejectTransferOffer`, `acceptTransferOffer`, `fetchTransferHistory`. Определить типы DTO (`TransferListingSummary`, `TransferListingDetail`, `TransferOffer`, `TransferHistoryEntry`) и вынести общие интерфейсы в `frontend/src/types/transfers.ts`.
2. **Вспомогательные утилиты** — добавить форматеры времени и статусов (таймер обратного отсчёта, бейджи статусов/ролей) в `frontend/src/utils/transfers.ts`, переиспользовать существующие функции форматирования дат из `pages/app/my-club`.
3. **Страница рынка** — создать `frontend/src/pages/app/transfers/page.tsx`:
   - Заголовок, блок фильтров (позиция/возраст/цена/клуб) с контролируемыми компонентами MUI.
   - Таблица/карточки листингов с колонками игрока, клуба, статуса, цен, времени до окончания, кнопкой перехода к деталке.
   - Индикаторы своих листингов/ставок (значки, подсказки).
   - Пагинация через MUI `Pagination`, состояние URL-селектора фильтров (`useSearchParams`).
4. **Деталка листинга** — `frontend/src/pages/app/transfers/[listingId]/page.tsx` (динамический сегмент `:listingId`):
   - Левый блок: карточка игрока (имя, позиция, возраст, клуб, рейтинг) и информация о листинге.
   - Правый блок: список офферов (таблица с суммой, клубом, временем, статусом).
   - Кнопки действий по ролям (`Make Offer`, `Cancel Listing`, `Accept/Reject`, `Cancel Offer`).
   - Тосты/Alert для ошибок API, обновление данных после мутаций.
5. **Управление клубом** — интегрировать виджет на страницу `my-club`: добавить карточку со списком активных листингов клубa и быстрыми ссылками `Create Listing`/`View Market`; возможно вынести в `sections/club-actions.tsx`. Выделить отдельную страницу `frontend/src/pages/app/my-club/transfers/page.tsx` (если требуется детальное управление) с табами (`Active`, `Pending Offers`, `History`).
6. **Создание листинга** — предусмотреть модальное окно/страницу `frontend/src/pages/app/transfers/create/page.tsx` с формой (использовать MUI `Dialog` или отдельный маршрут). Поля: выбор игрока (select с игроками текущего клуба), цена, длительность, описание. Перенести логики в кастомный хук `useTransferForm`.
7. **История трансферов** — страница `frontend/src/pages/app/transfers/history/page.tsx` с фильтрами по сезону/клубу/игроку и таблицей истории (аналог отчётов матчей).
8. **Роуты и меню** — обновить `frontend/src/routes.tsx` (маршруты `/transfers`, `/transfers/create`, `/transfers/history`, `/transfers/:listingId`), добавить пункт в левое меню (`menu-items.ts`) рядом с Matches, используя иконку `NiRepeat` или схожую. Убедиться, что редиректы и `lazyLoad` поддерживают новые пути.
9. **Состояние/загрузки** — предусмотреть индикаторы загрузки (`CircularProgress`), устойчивость к ошибкам (Alert), автоматический рефетч после действий (использовать `useEffect` и `Promise.all`). Рассмотреть использование React Query? Если нельзя, оставить ручное управление состоянием.
10. **Тесты** — React Testing Library для ключевых компонентов: а) рендер списка листингов с фильтрами; б) деталка показывает действия в зависимости от роли; в) форма создания листинга валидирует поля; г) обработка ошибок API. Добавить Mock Service Worker или заглушки fetch.
11. **Стили и повторное использование** — задействовать существующие стили карточек и секций (как в `player/overview` и `my-club`), вынести повторные блоки (например, `TransferListingCard`) в `frontend/src/components/transfers/`.
12. **Документация** — обновить README фронтенда (описание новых команд) и `tests/README.md` (добавить перечень тестов для трансферов).


### 9. Execution & Verification Roadmap
1. **Backend groundwork** — создать API в `transfers/api_views.py` и `api_urls.py`, подключить их в `realfootballsim/urls.py`, добавить сериализаторы/DTO-хелперы.
2. **Бэкенд тесты** — реализовать/расширить pytest-кейсы согласно пункту 7, убедиться, что все старые тесты проходят (`python -m pytest tests/test_transfers_*.py`).
3. **Frontend API слой** — добавить `frontend/src/api/transfers.ts`, типы и утилиты; прогнать `yarn lint`/`yarn typecheck` при наличии.
4. **Front-end pages** — последовательно внедрить страницы: рынок → деталка → история → управление клубом/создание. После каждого шага запускать `yarn test` для соответствующих компонентов.
5. **Интеграция и навигация** — обновить меню/роуты, проверить переходы вручную (dev-сервером `yarn dev`).
6. **Системное тестирование** — энд-ту-энд сценарии: создание листинга, ставка, принятие, истечение; использовать как минимум ручную проверку против dev-сервера и, при возможности, playwright/e2e.
7. **Документация** — освежить README (backend/frontend/tests) с инструкциями по запуску новых тестов и сценариев.
8. **Финальная проверка** — единый прогон `python -m pytest` и `yarn test`, сборка `yarn build` (если применимо), подготовка кода к ревью/коммиту.
