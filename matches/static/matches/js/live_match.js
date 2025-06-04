// matches/static/matches/js/live_match.js
let matchId = null; // set on DOMContentLoaded

// --- Обработчик кнопки замены ---
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const replaceButton = document.querySelector('#replace-player');
if (replaceButton) {
    replaceButton.addEventListener('click', function(){
        const actionForm = document.querySelector('.matchUserAction');
        if (actionForm) {
            actionForm.classList.remove('display-action');
        }
        const select = document.getElementById('playerToReplaceSelect');
        if (!select || !select.value) {
            console.warn('No player selected for substitution');
            return;
        }
        const csrftoken = getCookie('csrftoken');
        fetch(`/matches/${matchId}/substitute/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ out_player_id: select.value })
        })
        .then(resp => resp.json())
        .then(data => {
            console.log('Substitution response', data);
        })
        .catch(err => console.error('Substitution error', err));
    });
}

// --- Основная логика при загрузке страницы ---
document.addEventListener('DOMContentLoaded', function() {
    const matchInfoArea = document.getElementById('matchInfoArea');
    if (!matchInfoArea) {
        console.error('Element with ID "matchInfoArea" not found!');
        return;
    }

    matchId = matchInfoArea.dataset.matchId;
    const initialStatus = matchInfoArea.dataset.matchStatus;
    let currentMatchStatus = initialStatus; // Сохраняем текущий статус для проверок
    let isLive = initialStatus === 'in_progress';
    let matchSocket;

    console.log('Match setup:', { matchId, isLive, status: initialStatus });

    // --- Получаем ссылки на элементы DOM один раз ---
    const timeElement = document.getElementById('matchTime');
    const homeScoreElement = document.querySelector('.home-score');
    const awayScoreElement = document.querySelector('.away-score');
    const eventsListContainer = document.getElementById('originalEvents'); // Контейнер с прокруткой
    const eventsBox = eventsListContainer ? eventsListContainer.querySelector('.events-box') : null; // Внутренний блок для добавления
    const statBox = document.querySelector('.stat-box'); // Блок для статистики
    const injuryActionForm = document.querySelector('#matchUserAction-inj'); // Форма для травмы
    const nextMinuteBtn = document.getElementById('nextMinuteBtn');
    // Duration of one simulated minute in real seconds
    const minuteSeconds = parseFloat(matchInfoArea.dataset.minuteSeconds) || 0;
    let nextMinuteTimeout = null;

    // Проверяем наличие основных элементов для обновления
    if (!timeElement) { console.error('Element #matchTime not found!'); }
    if (!homeScoreElement) { console.error('Element .home-score not found!'); }
    if (!awayScoreElement) { console.error('Element .away-score not found!'); }
    if (!eventsBox) { console.error('Element .events-box inside #originalEvents not found!'); }
    if (!statBox) { console.error('Element .stat-box not found!'); }

    function handleStatusChange(status) {
        if (nextMinuteBtn) {
            if (status === 'paused') {
                nextMinuteBtn.style.display = 'block';
                nextMinuteBtn.disabled = false;
                if (minuteSeconds > 0) {
                    clearTimeout(nextMinuteTimeout);
                    nextMinuteTimeout = setTimeout(() => {
                        sendNextMinute();
                    }, minuteSeconds * 1000);
                }
            } else {
                nextMinuteBtn.style.display = 'none';
                clearTimeout(nextMinuteTimeout);
            }
        }
    }

    handleStatusChange(initialStatus);

    function sendNextMinute() {
        if (matchSocket && matchSocket.readyState === WebSocket.OPEN) {
            matchSocket.send(JSON.stringify({
                type: 'control',
                action: 'next_minute',
                match_id: matchId
            }));
        }
        if (nextMinuteBtn) {
            nextMinuteBtn.style.display = 'none';
        }
        clearTimeout(nextMinuteTimeout);
    }

    if (nextMinuteBtn) {
        nextMinuteBtn.addEventListener('click', function() {
            sendNextMinute();
        });
    }
    // injuryActionForm может отсутствовать, это не критично

     // --- Функция для отображения сообщений пользователю ---
     function showMessage(text, type = 'info') {
        // Эта функция должна быть реализована где-то в вашем коде (например, в core/base.html)
        // Временно выведем в консоль
        console.log(`MESSAGE (${type}): ${text}`);
        // Если у вас есть элементы для сообщений (как в base.html с alert-ами), используйте их:
        // const messagesContainer = document.getElementById('messagesContainer'); // Пример
        // if (messagesContainer) { /* Создать и добавить alert */ }
     }


    // --- Функция обновления статистики ---
    function updateStatistics(data) {
        // Обновляем только если statBox найден
        if (!statBox) return;

        // Ищем счетчик травм (может быть внутри statBox или отдельно)
        const injCounterElement = document.getElementById('inj');

        // Показываем форму реакции на травму, если счетчик изменился и форма есть
        if (injCounterElement && injuryActionForm && data.st_injury !== undefined) {
            const currentInjuries = parseInt(injCounterElement.innerText) || 0;
            if (currentInjuries !== data.st_injury) {
                console.log(`Injury count changed from ${currentInjuries} to ${data.st_injury}. Showing action form.`);
                injuryActionForm.style.display = 'block'; // Показываем форму
                injuryActionForm.classList.add('display-action'); // Добавляем класс (если нужен для стилей)
                // Можно добавить автоскрытие через таймаут, если нужно
                // setTimeout(() => { /* скрыть форму */ }, 15000);
            }
        }

        // Обновляем текст статистики, используя данные из data, если они есть
        // Используем более безопасный способ обновления через querySelector внутри statBox
        const passesSpan = statBox.querySelector('.stat-passes');
        const shootsSpan = statBox.querySelector('.stat-shoots');
        const possessionsSpan = statBox.querySelector('.stat-possessions');
        const foulsSpan = statBox.querySelector('.stat-fouls');
        const injuriesSpan = statBox.querySelector('.stat-injuries'); // Может быть тем же, что и injCounterElement

        if (passesSpan && data.st_passes !== undefined) passesSpan.textContent = data.st_passes;
        if (shootsSpan && data.st_shoots !== undefined) shootsSpan.textContent = data.st_shoots;
        if (possessionsSpan && data.st_possessions !== undefined) possessionsSpan.textContent = data.st_possessions;
        if (foulsSpan && data.st_fouls !== undefined) foulsSpan.textContent = data.st_fouls;
        if (injuriesSpan && data.st_injury !== undefined) injuriesSpan.textContent = data.st_injury;
        // Обновляем и отдельный счетчик, если он есть
        if (injCounterElement && data.st_injury !== undefined) injCounterElement.textContent = data.st_injury;

    }

    // --- Функция добавления одного события в лог (теперь добавляет в начало для обратного порядка) ---
    function addEventToList(event) {
        // Добавляем логирование в начало функции
        console.log(">>> addEventToList called with event:", event);
        
        // Защита от дублирования событий
        const eventSignature = `${event.minute}-${event.event_type}-${event.description}`;
        if (!window.processedEvents) {
            window.processedEvents = new Set();
        }
        
        if (window.processedEvents.has(eventSignature)) {
            console.log(">>> Duplicate event detected, skipping:", eventSignature);
            return;
        }
        
        window.processedEvents.add(eventSignature);

        // Проверяем наличие контейнера .events-box
        if (!eventsBox) {
             console.error("!!! eventsBox element not found inside #originalEvents! Cannot add event.");
             return;
        }
        // Логируем, что контейнер найден
        console.log(">>> Found eventsBox element:", eventsBox);

        // Создаем новый элемент события
        const eventDiv = document.createElement('div');
        eventDiv.className = 'list-group-item new-event'; // Класс для анимации

        // Иконки для событий
        let icon = ' M ';
        switch(event.event_type) {
            case 'goal': icon = ' ⚽ '; break;
            case 'counterattack': icon = ' ⚡ '; break;
            case 'interception': icon = ' 🔄 '; break;
            case 'shot_miss': icon = ' ❌ '; break;
            case 'pass': icon = ' ➡ '; break;
            case 'foul': icon = ' ⚠ '; break;
            case 'injury_concern': icon = ' ✚ '; break;
            case 'yellow_card': icon = ' 🟨 '; break;
            case 'red_card': icon = ' 🟥 '; break;
            case 'substitution': icon = ' ⇆ '; break;
            case 'match_start': icon = ' ▶ '; break;
            case 'match_end': icon = ' ⏹ '; break;
            case 'match_paused': icon = ' ⏸ '; break;
             case 'info': icon = ' ⓘ '; break; // Добавлено для информационных сообщений
        }

        // Имена игроков
        let playerInfo = event.player_name ? ` (${event.player_name})` : '';
        if (event.related_player_name) {
             playerInfo += ` -> ${event.related_player_name}`;
        }

        // Формируем HTML
        eventDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${event.minute}'</strong>
                    <span class="event-icon">${icon}</span>
                    ${event.description}
                    <small class="text-muted">${playerInfo}</small>
                </div>
            </div>
        `;

        // Вставляем в НАЧАЛО списка для обратного хронологического порядка (новые сверху)
        eventsBox.insertBefore(eventDiv, eventsBox.firstChild);
        console.log(">>> Event prepended to eventsBox");

        // Ограничиваем количество событий (опционально, но хорошая практика)
        // Удаляем старые события снизу
        while (eventsBox.children.length > 100) { // Можно увеличить лимит, если нужно
            eventsBox.removeChild(eventsBox.lastChild); // Удаляем с конца
        }

        // Анимация появления
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                 eventDiv.classList.add('new-event-visible');
                 console.log(">>> Animation class added for:", eventDiv);
            });
        });

        // Автоматическая прокрутка вверх к новым событиям (если лог уже заполнен)
         if (eventsListContainer) {
              // eventsListContainer.scrollTop = 0; // Прокрутка в самый верх
              // Или плавная прокрутка:
              eventsListContainer.scrollTo({ top: 0, behavior: 'smooth' });
         }
    }

    // --- Логика WebSocket ---
    if (isLive) {
        console.log('Match is live, attempting WebSocket connection...');

        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const wsUrl = `${wsScheme}://${window.location.host}/ws/match/${matchId}/`;
        console.log('WebSocket URL:', wsUrl) ;

        matchSocket = new WebSocket(wsUrl);

        matchSocket.onopen = function(e) {
            console.log('WebSocket connection established successfully!');
             // При успешном подключении консьюмер пришлет первое сообщение с начальным состоянием и всей историей событий.
             // Эти события будут обработаны в onmessage.
        };

        matchSocket.onclose = function(e) {
            console.log(`WebSocket connection closed: Code=${e.code}, Reason='${e.reason}', WasClean=${e.wasClean}`);
            if (currentMatchStatus === 'in_progress') { // Показываем предупреждение, только если матч еще должен идти
                showMessage('Connection lost. Match updates stopped.', 'warning');
            }
        };

        matchSocket.onerror = function(e) {
            console.error('WebSocket error occurred:', e);
            showMessage('Connection error occurred.', 'danger');
        };

        matchSocket.onmessage = function(e) {
            try {
                const messageData = JSON.parse(e.data);

                // Проверяем базовую структуру
                if (messageData.type !== 'match_update' || !messageData.data) {
                     console.warn("Received message is not 'match_update' or missing 'data'.", messageData);
                     return;
                }

                const data = messageData.data;
                console.log('Received WS message data:', data); // Логируем ПОЛУЧЕННОЕ сообщение

                // --- Обработка полного обновления состояния и ИСТОРИИ (обычно первое сообщение) ---
                // Проверяем, что это не одиночное событие (нет partial_update: true)
                // и что есть список событий.
                if (data.partial_update === undefined && data.events && Array.isArray(data.events)) {
                    console.log(`Processing initial FULL STATE + HISTORY update (${data.events.length} events)`);

                     // Очищаем текущий лог событий (включая те, что вывел шаблон)
                     if (eventsBox) {
                         eventsBox.innerHTML = '';
                         console.log("Cleared eventsBox for initial load.");
                     }

                    // Добавляем все исторические события.
                    // Так как addEventToList добавляет в начало,
                    // а события в массиве data.events приходят в хронологическом порядке с бэкенда,
                    // итоговый список будет в обратном хронологическом порядке.
                    data.events.forEach(event => {
                         addEventToList(event);
                    });
                    console.log(`Added ${data.events.length} historical events from initial message.`);

                     // Обновляем состояние после загрузки всех исторических событий
                     if (timeElement && data.minute !== undefined) timeElement.textContent = `${data.minute}'`;
                     updateStatistics(data);

                }
                 // --- Обработка одиночного события (от broadcast_minute_events_in_chunks) ---
                else if (data.partial_update === true && data.events && Array.isArray(data.events) && data.events.length > 0) {
                    console.log('Processing single EVENT update (from broadcast_minute_events_in_chunks):', data.events[0]);
                    // Добавляем событие в список (функция addEventToList добавляет в начало)
                    const eventObj = data.events[0];
                    addEventToList(eventObj);
                    // Также обновляем состояние, если оно пришло в этом же сообщении (обычно нет)
                    if (data.minute !== undefined) timeElement.textContent = `${data.minute}'`;
                    // Обновляем счет только при показе события "goal"
                    if (eventObj.event_type === "goal") {
                        if (data.home_score !== undefined) homeScoreElement.textContent = data.home_score;
                        if (data.away_score !== undefined) awayScoreElement.textContent = data.away_score;
                    }

                }
                 // --- Обработка только обновления состояния (от send_update) ---
                else if (data.partial_update === undefined && data.events === undefined) {
                    console.log('Processing STATE update (from send_update)');

                    // Обновляем время
                    if (timeElement && data.minute !== undefined) {
                        timeElement.textContent = `${data.minute}'`;
                    } else if(timeElement) {
                         console.warn("State update received, but 'minute' is missing or undefined.");
                    }
                    // Счет не обновляем здесь, он изменится вместе с событием

                    // Обновляем статистику


                    updateStatistics(data);
                } else {
                     // Неизвестный формат сообщения
                     console.warn("Received message format not recognized. Ignored.", data);
                }


                // --- Проверка статуса матча (независимо от типа сообщения) ---
                if (data.status && data.status !== currentMatchStatus) {
                     console.log(`Match status changed from ${currentMatchStatus} to: ${data.status}`);
                     currentMatchStatus = data.status; // Обновляем текущий статус
                     handleStatusChange(data.status);
                     const statusDisplay = document.getElementById('matchStatusDisplay');
                     if(statusDisplay) statusDisplay.textContent = data.status; // Обновляем отображение статуса

                     if (['finished', 'cancelled', 'error'].includes(currentMatchStatus)) {
                          console.log("Match ended. Closing WebSocket.");
                           // Показываем сообщение о завершении матча
                           showMessage(`Match ${currentMatchStatus}. Live updates stopped.`, 'info');
                          // Закрываем сокет
                          matchSocket.close();
                          // Можно добавить логику для кнопки реплея и т.д.
                          const replayButton = document.getElementById('startReplayBtn');
                          if (replayButton && currentMatchStatus === 'finished') {
                               replayButton.style.display = 'block'; // Показываем кнопку реплея
                          }
                     }
                }


            } catch (error) {
                console.error('Error parsing WebSocket message or processing data:', error);
                console.error('Raw message data:', e.data);
            }
        };

    } else {
        console.log('Match is not live (' + initialStatus + '), skipping WebSocket setup.');
        // Если матч не live (например, finished или scheduled), события уже выведены шаблоном.
        // Ничего дополнительно делать не нужно, WebSocket не требуется.
    }
}); // End DOMContentLoaded
