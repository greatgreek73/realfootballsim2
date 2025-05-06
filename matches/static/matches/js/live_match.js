// matches/static/matches/js/live_match.js

// --- Обработчик кнопки замены (оставляем как есть) ---
const replaceButton = document.querySelector('#replace-player');
if (replaceButton) {
    replaceButton.addEventListener('click', function(){
        const actionForm = document.querySelector('.matchUserAction'); // Используем класс вместо ID для формы
        if (actionForm) {
            actionForm.classList.remove('display-action');
        }
        // TODO: Добавить логику отправки данных о замене на сервер
        console.log("Replace button clicked - Implement replacement logic.");
        // Пример: получить выбранного игрока из select#playerToReplaceSelect
        // Отправить AJAX/fetch запрос на бэкенд с ID матча и ID игрока
    });
}

// --- Основная логика при загрузке страницы ---
document.addEventListener('DOMContentLoaded', function() {
    const matchInfoArea = document.getElementById('matchInfoArea');
    if (!matchInfoArea) {
        console.error('Element with ID "matchInfoArea" not found!');
        return;
    }

    const matchId = matchInfoArea.dataset.matchId;
    const initialStatus = matchInfoArea.dataset.matchStatus; 
    let currentMatchStatus = initialStatus; // Сохраняем текущий статус для проверок
    let isLive = initialStatus === 'in_progress'; 

    console.log('Match setup:', { matchId, isLive, status: initialStatus });

    // --- Получаем ссылки на элементы DOM один раз ---
    const timeElement = document.getElementById('matchTime');
    const homeScoreElement = document.querySelector('.home-score');
    const awayScoreElement = document.querySelector('.away-score');
    const eventsListContainer = document.getElementById('originalEvents'); // Контейнер с прокруткой
    const eventsBox = eventsListContainer ? eventsListContainer.querySelector('.events-box') : null; // Внутренний блок для добавления
    const statBox = document.querySelector('.stat-box'); // Блок для статистики
    const injuryActionForm = document.querySelector('#matchUserAction-inj'); // Форма для травмы

    // Проверяем наличие основных элементов для обновления
    if (!timeElement) { console.error('Element #matchTime not found!'); }
    if (!homeScoreElement) { console.error('Element .home-score not found!'); }
    if (!awayScoreElement) { console.error('Element .away-score not found!'); }
    if (!eventsBox) { console.error('Element .events-box inside #originalEvents not found!'); }
    if (!statBox) { console.error('Element .stat-box not found!'); }
    // injuryActionForm может отсутствовать, это не критично

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
                // Можно добавить автоскрытие
                // setTimeout(() => {
                //     injuryActionForm.style.display = 'none';
                //     injuryActionForm.classList.remove('display-action');
                // }, 15000); 
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

    // --- Функция добавления одного события в лог ---
    function addEventToList(event) {
        // Добавляем логирование в начало функции
        console.log(">>> addEventToList called with event:", event); 

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
            case 'interception': icon = ' 🔄 '; break;
            case 'shot_miss': icon = ' ❌ '; break;
            case 'pass': icon = ' ➡️ '; break;
            case 'foul': icon = ' ⚠️ '; break;
            case 'injury_concern': icon = ' ✚ '; break;
            case 'yellow_card': icon = ' 🟨 '; break;
            case 'red_card': icon = ' 🟥 '; break;
            case 'substitution': icon = ' ⇆ '; break;
            case 'match_start': icon = ' ▶️ '; break;
            case 'match_end': icon = ' ⏹️ '; break;
            case 'match_paused': icon = ' ⏸️ '; break;
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
        
        // Вставляем в начало списка
        if (eventsBox.firstChild) {
            eventsBox.insertBefore(eventDiv, eventsBox.firstChild);
            console.log(">>> Event prepended to eventsBox"); 
        } else {
            // Если список был пуст (например, содержал "Waiting..."), очистим его перед добавлением
            eventsBox.innerHTML = ''; 
            eventsBox.appendChild(eventDiv);
            console.log(">>> Event appended to initially empty eventsBox"); 
        }

        // Ограничиваем количество событий
        while (eventsBox.children.length > 30) {
            eventsBox.removeChild(eventsBox.lastChild);
        }

        // Анимация появления
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                 eventDiv.classList.add('new-event-visible');
                 console.log(">>> Animation class added for:", eventDiv); 
            });
        });
    }

    // --- Логика WebSocket ---
    if (isLive) {
        console.log('Match is live, attempting WebSocket connection...');
        
        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const wsUrl = `${wsScheme}://${window.location.host}/ws/match/${matchId}/`;
        console.log('WebSocket URL:', wsUrl) ;
        
        const matchSocket = new WebSocket(wsUrl);

        matchSocket.onopen = function(e) {
            console.log('WebSocket connection established successfully!');
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
                
                // Логируем ПОЛУЧЕННОЕ сообщение
                console.log('Received WS message data:', messageData.data); 

                const data = messageData.data; 

                // --- Разделение логики ---

                // 1. Обновление СОБЫТИЯ (от broadcast...)
                // Проверяем наличие 'events' и 'partial_update'
                if (data.events && data.partial_update === true && Array.isArray(data.events) && data.events.length > 0) {
                    console.log('Processing EVENT update (from broadcast_minute_events_in_chunks):', data.events[0]);
                    addEventToList(data.events[0]); 
                } 
                // 2. Обновление СОСТОЯНИЯ (от send_update)
                // Проверяем ОТСУТСТВИЕ 'events'
                else if (data.events === undefined) { 
                    console.log('Processing STATE update (from send_update)');
                    
                    // Обновляем время
                    if (timeElement && data.minute !== undefined) {
                        timeElement.textContent = `${data.minute}'`;
                    } else if(timeElement) {
                        console.warn("State update received, but 'minute' is missing or undefined.");
                    }

                    // Обновляем счет
                    if (homeScoreElement && data.home_score !== undefined) {
                        homeScoreElement.textContent = data.home_score;
                    } else if(homeScoreElement) {
                         console.warn("State update received, but 'home_score' is missing or undefined.");
                    }
                     if (awayScoreElement && data.away_score !== undefined) {
                        awayScoreElement.textContent = data.away_score;
                    } else if(awayScoreElement) {
                         console.warn("State update received, but 'away_score' is missing or undefined.");
                    }

                    // Обновляем статистику
                    updateStatistics(data);

                    // Обновляем статус матча и закрываем сокет, если матч закончился
                    if (data.status && data.status !== currentMatchStatus) {
                         console.log(`Match status changed from ${currentMatchStatus} to: ${data.status}`);
                         currentMatchStatus = data.status; // Обновляем текущий статус
                         const statusDisplay = document.getElementById('matchStatusDisplay');
                         if(statusDisplay) statusDisplay.textContent = data.status; // Обновляем отображение статуса

                         if (currentMatchStatus === 'finished' || currentMatchStatus === 'cancelled' || currentMatchStatus === 'error') {
                              console.log("Match ended. Closing WebSocket.");
                              showMessage(`Match ${currentMatchStatus}. Live updates stopped.`, 'info');
                              matchSocket.close(); 
                              // Можно добавить логику для кнопки реплея и т.д.
                              const replayButton = document.getElementById('startReplayBtn');
                              if (replayButton && currentMatchStatus === 'finished') {
                                   replayButton.style.display = 'block'; // Показываем кнопку реплея
                              }
                         }
                    }
                } else {
                     // Сообщение имеет ключ 'events', но не имеет флага partial_update
                     // или events - пустой массив. Игнорируем или логируем.
                     console.warn("Received message seems like a state update but contains 'events' key, or 'events' is empty. Ignored.", data);
                }

            } catch (error) {
                console.error('Error parsing WebSocket message or processing data:', error);
                console.error('Raw message data:', e.data);
            }
        };

    } else {
        console.log('Match is not live (' + initialStatus + '), skipping WebSocket setup.');
        // Инициализация статистики из начальных данных (если нужно)
        // Предполагаем, что начальные данные переданы в data-атрибуты или JS переменные
        // const initialData = { ... }; 
        // updateStatistics(initialData);
    }
}); // End DOMContentLoaded