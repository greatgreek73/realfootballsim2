document.addEventListener('DOMContentLoaded', function() {
    const startButton = document.getElementById('startReplayBtn');
    const replayTime = document.getElementById('replayTime');
    const replayScore = document.getElementById('replayScore');
    const replayEventsList = document.getElementById('replayEvents');
    const matchInfoArea = document.getElementById('matchInfoArea');
    const replayArea = document.getElementById('replayArea');

    let eventsData = [];
    let matchData = null;
    let currentMinute = 0;
    let homeScore = 0;
    let awayScore = 0;
    let replayInterval = null;

    if (startButton) {
        startButton.addEventListener('click', startReplay);
    }

    function startReplay() {
        // Блокируем кнопку на время реплея
        startButton.disabled = true;
        startButton.textContent = 'Replay in progress...';
        
        // Получаем события с бэкенда
        const matchId = matchInfoArea.dataset.matchId;
        
        fetch(`/matches/${matchId}/events-json/`)
            .then(resp => resp.json())
            .then(data => {
                eventsData = data.events;
                matchData = data.match;
                
                // Обнуляем всё
                currentMinute = 0;
                homeScore = 0;
                awayScore = 0;
                replayEventsList.innerHTML = '';
                
                // Показываем область реплея
                replayArea.style.display = 'block';
                
                // Обновляем заголовок
                replayTime.textContent = "0'";
                replayScore.textContent = `${matchData.home_team} 0 - 0 ${matchData.away_team}`;
                
                // Запускаем таймер
                if (replayInterval) {
                    clearInterval(replayInterval);
                }
                
                replayInterval = setInterval(() => {
                    currentMinute += 1;
                    if (currentMinute > 90) {
                        clearInterval(replayInterval);
                        startButton.disabled = false;
                        startButton.textContent = 'Restart Replay';
                        return;
                    }
                    
                    // Обновляем время
                    replayTime.textContent = currentMinute + "'";
                    
                    // Показываем события текущей минуты
                    showEventsUpTo(currentMinute);
                    
                }, 3000); // 3 секунды на каждую минуту матча
            })
            .catch(error => {
                console.error('Error fetching match events:', error);
                startButton.disabled = false;
                startButton.textContent = 'Start Replay';
            });
    }

    function showEventsUpTo(minute) {
        const currentEvents = eventsData.filter(ev => ev.minute === minute);
        
        currentEvents.forEach(ev => {
            // Создаем элемент события
            const eventDiv = document.createElement('div');
            eventDiv.className = 'match-event';
            
            // Добавляем иконку в зависимости от типа события
            let icon = '📝'; // default icon
            if (ev.event_type === 'goal') {
                icon = '⚽';
                if (ev.description.includes(matchData.home_team)) {
                    homeScore++;
                } else if (ev.description.includes(matchData.away_team)) {
                    awayScore++;
                }
            } else if (ev.event_type === 'yellow_card') {
                icon = '🟨';
            } else if (ev.event_type === 'red_card') {
                icon = '🟥';
            }
            
            eventDiv.innerHTML = `
                <span class="event-time">${ev.minute}'</span>
                <span class="event-icon">${icon}</span>
                <span class="event-description">${ev.description}</span>
            `;
            
            // Добавляем событие в список
            replayEventsList.insertBefore(eventDiv, replayEventsList.firstChild);
            
            // Обновляем счет
            replayScore.textContent = 
                `${matchData.home_team} ${homeScore} - ${awayScore} ${matchData.away_team}`;
        });
    }
});