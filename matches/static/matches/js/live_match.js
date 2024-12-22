document.addEventListener('DOMContentLoaded', function() {
    const matchInfoArea = document.getElementById('matchInfoArea');
    const matchId = matchInfoArea.dataset.matchId;
    const isLive = matchInfoArea.dataset.matchStatus === 'in_progress';

    if (isLive) {
        console.log('Match is live, connecting to WebSocket...');
        
        // Создаем WebSocket соединение
        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const matchSocket = new WebSocket(
            `${wsScheme}://${window.location.host}/ws/match/${matchId}/`
        );

        matchSocket.onopen = function(e) {
            console.log('WebSocket connection established');
        };

        matchSocket.onmessage = function(e) {
            console.log('Received message:', e.data);
            const data = JSON.parse(e.data);
            
            // Обновляем время
            const timeElement = document.getElementById('matchTime');
            if (timeElement) {
                timeElement.textContent = `${data.minute}'`;
            }

            // Обновляем счет
            const scoreElement = document.getElementById('score');
            if (scoreElement) {
                scoreElement.textContent = `${data.home_score} - ${data.away_score}`;
            }

            // Добавляем новые события
            const eventsList = document.getElementById('originalEvents').querySelector('.list-group');
            data.events.forEach(event => {
                const eventDiv = document.createElement('div');
                eventDiv.className = 'list-group-item';
                
                let icon = '📝';
                if (event.event_type === 'goal') icon = '⚽';
                else if (event.event_type === 'yellow_card') icon = '🟨';
                else if (event.event_type === 'red_card') icon = '🟥';

                eventDiv.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${event.minute}'</strong> 
                            <span class="event-icon">${icon}</span>
                            ${event.description}
                        </div>
                    </div>
                `;
                
                eventsList.insertBefore(eventDiv, eventsList.firstChild);
            });

            // Если матч завершен, перезагружаем страницу
            if (data.status === 'finished') {
                location.reload();
            }
        };

        matchSocket.onclose = function(e) {
            console.error('Match socket closed unexpectedly');
        };

        matchSocket.onerror = function(e) {
            console.error('WebSocket error:', e);
        };
    }
});