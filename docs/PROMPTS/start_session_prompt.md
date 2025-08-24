# START SESSION PROMPT — вставь это сообщение в Claude Code (первым)

Прочитай ТОЛЬКО эти файлы (в этом порядке) — другие из docs НЕ ЧИТАЙ:
1) docs/CODEBASE_MAP.md
2) docs/CURRENT_TASK_template_integration.md
3) docs/AI_RULES.md
4) docs/VITE_NOTES.md

Действия:
1) Кратко перескажи структуру проекта и риски интеграции фронт↔бэк.
2) Дай пошаговый план по задачe CURRENT_TASK_template_integration.md.
3) Подготовь **DIFF-ONLY** патчи **строго для двух файлов**:
   - frontend/vite.config.ts
   - frontend/src/api/http.ts
   Запрещено обновлять зависимости и менять настройки Django/infra.
4) Приложи короткий чек-лист из docs/TEST_CHECKLIST.md (только релевантные пункты).

Формат ответа:
- Список изменяемых файлов (пути).
- DIFF-ONLY (unified diff) для каждого файла.
- Мини-чеклист ручной проверки.

Если дифф > 300 строк — раздели на несколько итераций.
