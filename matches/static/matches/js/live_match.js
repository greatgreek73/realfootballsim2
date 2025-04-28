const replaceButton = document.querySelector('#replace-player');
if (replaceButton) {
    replaceButton.addEventListener('click', function(){
        const actionForm = document.querySelector('matchUserAction-inj');
        if (actionForm) {
            actionForm.classList.remove('display-action');
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const matchInfoArea = document.getElementById('matchInfoArea');
    if (!matchInfoArea) {
        console.error('matchInfoArea not found!');
        return;
    }

    const matchId = matchInfoArea.dataset.matchId;
    const isLive = matchInfoArea.dataset.matchStatus === 'in_progress';

    console.log('Match setup:', { matchId, isLive, status: matchInfoArea.dataset.matchStatus });

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
            console.log('WebSocket connection closed:', e.code, e.reason);
            console.error('Match socket closed unexpectedly');
            // Попытка переподключения через 5 секунд
            // setTimeout(() => window.location.reload(), 5000);
        };

        matchSocket.onerror = function(e) {
            console.error('WebSocket error occurred:', e);
        };

        matchSocket.onmessage = function(e) {
            try {
                const data = JSON.parse(e.data);
                console.log('Parsed data:', data);
                
                // Обновляем время
                const timeElement = document.getElementById('matchTime');
                if (timeElement && data.minute !== undefined) {
                    timeElement.textContent = `${data.minute}'`;
                }

                // Обновляем счет
                const scoreElement = document.getElementById('score');
                if (scoreElement && data.home_score !== undefined && data.away_score !== undefined) {
                    const homeScoreElement = document.querySelector('.home-score');
                    const awayScoreElement = document.querySelector('.away-score');
                    
                    if (homeScoreElement) {
                        homeScoreElement.textContent = data.home_score;
                    }
                    
                    if (awayScoreElement) {
                        awayScoreElement.textContent = data.away_score;
                    }
                }

                // Обновляем события
                if (data.events && Array.isArray(data.events)) {
                    const eventsList = document.getElementById('originalEvents');
                    if (eventsList) {
                        const stat = document.querySelector('.stat-box');
                        //Handle user activity
                        const injElement = document.querySelector('#inj');
                        if (injElement) {
                            const inj = parseInt(injElement.innerText);
                            if (inj != data.st_injury) {
                                const action = document.querySelector('#matchUserAction-inj');
                                if (action) {
                                    action.classList.add('display-action');
                                    setTimeout(() => {
                                        action.classList.remove('display-action');
                                    }, 5000);
                                }
                            }
                        }
                        
                        if (stat) {
                            stat.innerHTML = `
                            <h5>Passes : ${data.st_passes}</h5>
                            <h5>Shoots : ${data.st_shoots}</h5>
                            <h5>Posessions : ${data.st_posessions}</h5>
                            <h5>Fouls : ${data.st_fouls}</h5>
                            <h5>Injuries : <span id="inj">${data.st_injury}</span></h5>
                            `;
                        }
                        
                        const listGroup = eventsList.querySelector('.events-box');
                        if (listGroup) {
                            // Проверяем, является ли это частичным обновлением
                            if (data.partial_update) {
                                console.log('Получено частичное обновление с событиями:', data.events);
                                
                                // Обрабатываем каждое событие в частичном обновлении
                                data.events.forEach(event => {
                                    // Создаем новый элемент события с анимацией
                                    const eventDiv = document.createElement('div');
                                    eventDiv.className = 'list-group-item new-event'; // Класс для анимации
                                    
                                    // Выбираем иконку в зависимости от типа события
                                    let icon = '📝';
                                    if (event.event_type === 'goal') {
                                        icon = '⚽';
                                    } else if (event.event_type === 'interception') {
                                        icon = '🔄';
                                    } else if (event.event_type === 'shot_miss') {
                                        icon = '❌';
                                    } else if (event.event_type === 'pass') {
                                        icon = '➡️';
                                    } else if (event.event_type === 'yellow_card') {
                                        icon = '🟨';
                                    } else if (event.event_type === 'red_card') {
                                        icon = '🟥';
                                    }
                            
                                    // Формируем HTML содержимое события
                                    eventDiv.innerHTML = `
                                        <div class="d-flex justify-content-between align-items-center">
                                            <div>
                                                <strong>${event.minute}'</strong> 
                                                <span class="event-icon">${icon}</span>
                                                ${event.description}
                                            </div>
                                        </div>
                                    `;
                                    
                                    // Вставляем в начало списка
                                    if (listGroup.firstChild) {
                                        listGroup.insertBefore(eventDiv, listGroup.firstChild);
                                    } else {
                                        listGroup.appendChild(eventDiv);
                                    }

                                    // Добавляем анимацию появления с небольшой задержкой
                                    setTimeout(() => {
                                        eventDiv.classList.add('new-event-visible');
                                    }, 50);
                                });
                            } else {
                                // Полное обновление - заменяем все события
                                console.log('Получено полное обновление с событиями:', data.events);
                                
                                // Очищаем старые события
                                listGroup.innerHTML = '';
                                
                                // Добавляем новые события (сортируем в порядке минут)
                                data.events
                                    .sort((a, b) => b.minute - a.minute)
                                    .forEach(event => {
                                        const eventDiv = document.createElement('div');
                                        eventDiv.className = 'list-group-item';
                                        
                                        let icon = '📝';
                                        if (event.event_type === 'goal') {
                                            icon = '⚽';
                                        } else if (event.event_type === 'interception') {
                                            icon = '🔄';
                                        } else if (event.event_type === 'shot_miss') {
                                            icon = '❌';
                                        } else if (event.event_type === 'pass') {
                                            icon = '➡️';
                                        } else if (event.event_type === 'yellow_card') {
                                            icon = '🟨';
                                        } else if (event.event_type === 'red_card') {
                                            icon = '🟥';
                                        }
                                
                                        eventDiv.innerHTML = `
                                            <div class="d-flex justify-content-between align-items-center">
                                                <div>
                                                    <strong>${event.minute}'</strong> 
                                                    <span class="event-icon">${icon}</span>
                                                    ${event.description}
                                                </div>
                                            </div>
                                        `;
                                        
                                        listGroup.appendChild(eventDiv);
                                    });
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
                console.error('Raw message:', e.data);
            }
        };
    } else {
        console.log('Match is not live, skipping WebSocket setup');
    }
});
