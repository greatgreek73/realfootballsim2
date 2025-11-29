# Диаграмма симуляции одной минуты матча

## 1. Общий поток

```mermaid
flowchart TD
    A[Celery Task: simulate_active_matches] --> B[Блокировка матча]
    B --> C[Подготовка составов rosters]
    C --> D[simulate_markov_minute]
    D --> E[Цикл 6 тиков]
    E --> F[Сохранение в БД]
    F --> G[WebSocket broadcast]
```

## 2. Цикл одной минуты (6 тиков по 10 сек)

```mermaid
flowchart TD
    START((Начало минуты)) --> T1

    subgraph TICK["Для каждого тика (1-6)"]
        T1[1. Выбор пары игроков] --> T2[2. Расчёт коэффициентов]
        T2 --> T3[3. Выбор перехода по вероятностям]
        T3 --> T4[4. Запись события]
        T4 --> T5[5. Обновление состояния]
    end

    T5 --> CHECK{Тик < 6?}
    CHECK -->|Да| T1
    CHECK -->|Нет| END((Конец минуты))
```

## 3. Машина состояний (Markov Chain)

```mermaid
stateDiagram-v2
    [*] --> KICKOFF: Начало матча/после гола

    KICKOFF --> OPEN_PLAY_MID: 88%
    KICKOFF --> OPEN_PLAY_DEF: 8%
    KICKOFF --> FOUL: 2%
    KICKOFF --> OUT: 2%

    OPEN_PLAY_DEF --> OPEN_PLAY_DEF: 20%
    OPEN_PLAY_DEF --> OPEN_PLAY_MID: 40%
    OPEN_PLAY_DEF --> OPEN_PLAY_MID: 18% turnover
    OPEN_PLAY_DEF --> OUT: 12%
    OPEN_PLAY_DEF --> FOUL: 8%
    OPEN_PLAY_DEF --> SHOT: 2%

    OPEN_PLAY_MID --> OPEN_PLAY_MID: 25%
    OPEN_PLAY_MID --> OPEN_PLAY_FINAL: 30%
    OPEN_PLAY_MID --> OPEN_PLAY_DEF: 10%
    OPEN_PLAY_MID --> OPEN_PLAY_MID: 20% turnover
    OPEN_PLAY_MID --> OUT: 10%
    OPEN_PLAY_MID --> FOUL: 3%
    OPEN_PLAY_MID --> SHOT: 2%

    OPEN_PLAY_FINAL --> OPEN_PLAY_FINAL: 20%
    OPEN_PLAY_FINAL --> SHOT: 30%
    OPEN_PLAY_FINAL --> OPEN_PLAY_DEF: 20% turnover
    OPEN_PLAY_FINAL --> OUT: 18%
    OPEN_PLAY_FINAL --> FOUL: 7%
    OPEN_PLAY_FINAL --> OPEN_PLAY_MID: 5%

    SHOT --> KICKOFF: 11% ГОЛ!
    SHOT --> GK: 27% saved
    SHOT --> GK: 52% мимо
    SHOT --> OUT: 10% угловой

    GK --> OPEN_PLAY_DEF: 100%

    FOUL --> OPEN_PLAY_DEF: в зоне DEF
    FOUL --> OPEN_PLAY_MID: в зоне MID
    FOUL --> OPEN_PLAY_FINAL: в зоне FINAL

    OUT --> OPEN_PLAY_MID: throw-in
    OUT --> OPEN_PLAY_FINAL: corner
    OUT --> GK: goal kick
```

## 4. Упрощённая схема состояний

```
                    ┌─────────────┐
                    │   KICKOFF   │
                    │ (после гола)│
                    └──────┬──────┘
                           │ 88%
                           ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ OPEN_PLAY   │◄───►│ OPEN_PLAY   │────►│ OPEN_PLAY   │
│    DEF      │ 40% │    MID      │ 30% │   FINAL     │
│ (защита)    │     │ (центр)     │     │ (атака)     │
└──────┬──────┘     └─────────────┘     └──────┬──────┘
       │                                        │ 30%
       │                                        ▼
       │                                 ┌─────────────┐
       │                                 │    SHOT     │
       │                                 │   (удар)    │
       │                                 └──────┬──────┘
       │                                        │
       │            ┌───────────────────────────┼───────────────┐
       │            │ 11%                       │ 79%           │ 10%
       │            ▼                           ▼               ▼
       │     ┌─────────────┐             ┌─────────────┐  ┌─────────┐
       │     │    GOAL!    │             │     GK      │  │   OUT   │
       │     │  → KICKOFF  │             │ (вратарь)   │  │ (аут)   │
       │     └─────────────┘             └──────┬──────┘  └────┬────┘
       │                                        │              │
       └────────────────────────────────────────┴──────────────┘
                            возврат в игру
```

## 5. Влияние силы команд

```
Базовая вероятность удара: 30%

              Атакующий сильнее                  Защитник сильнее
              (рейтинг 90 vs 70)                 (рейтинг 70 vs 90)
                     │                                   │
                     ▼                                   ▼
            Вероятность удара: ~40%              Вероятность удара: ~22%
```

**Формула:**
```
multiplier = attack_coeff / defense_coeff
new_probability = base_probability × multiplier
```

## 6. Пример одной минуты

```
Минута 25, Home владеет мячом в центре

Тик 1: MID → MID      "Home пасуют в центре"
Тик 2: MID → FINAL    "Home проходят в штрафную"  ← entries_final++
Тик 3: FINAL → SHOT   "Home бьют!"                ← shots++
Тик 4: SHOT → GK      "Мимо ворот"                ← владение к Away
Тик 5: GK → DEF       "Вратарь Away вводит мяч"
Тик 6: DEF → MID      "Away выходят в центр"

Результат: Away владеет в центре, 1 удар, 0 голов
```

## 7. Ключевые файлы

| Файл | Назначение |
|------|------------|
| `matches/engines/markov_runtime.py` | Движок симуляции |
| `matches/engines/markov_spec_v0.yaml` | Вероятности переходов |
| `tournaments/tasks.py` | Celery задача запуска |

## 8. Параметры

- **1 минута** = 6 тиков × 10 секунд
- **Матч** = 90 минут
- **Состояний** = 8 (KICKOFF, DEF, MID, FINAL, SHOT, OUT, FOUL, GK)
- **Вероятность гола** = 30% (выход на удар) × 11% (гол) ≈ 3.3% за тик в штрафной
