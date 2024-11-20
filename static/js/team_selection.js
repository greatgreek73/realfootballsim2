document.addEventListener('DOMContentLoaded', function() {
    const pitch = document.getElementById('pitch');
    const playerList = document.getElementById('playerList');
    const clubId = document.getElementById('clubId').value;
    const resetButton = document.getElementById('resetButton');
    const saveStatus = document.getElementById('saveStatus');

    // Конфигурация позиций на поле
    const positions = [
        { top: '10%', left: '50%', type: 'goalkeeper', label: 'GK' },  // GK
        { top: '30%', left: '20%', type: 'defender', label: 'LB' },   // DEF
        { top: '30%', left: '40%', type: 'defender', label: 'CB' },
        { top: '30%', left: '60%', type: 'defender', label: 'CB' },
        { top: '30%', left: '80%', type: 'defender', label: 'RB' },
        { top: '60%', left: '30%', type: 'midfielder', label: 'LM' }, // MID
        { top: '60%', left: '50%', type: 'midfielder', label: 'CM' },
        { top: '60%', left: '70%', type: 'midfielder', label: 'RM' },
        { top: '80%', left: '30%', type: 'forward', label: 'LF' },    // FWD
        { top: '80%', left: '50%', type: 'forward', label: 'ST' },
        { top: '80%', left: '70%', type: 'forward', label: 'RF' }
    ];

    // Создание слотов для игроков на поле
    positions.forEach((pos, index) => {
        const slot = document.createElement('div');
        slot.className = 'player-slot';
        slot.style.top = pos.top;
        slot.style.left = pos.left;
        slot.dataset.position = index;
        slot.dataset.type = pos.type;

        // Добавляем подпись позиции
        const label = document.createElement('div');
        label.className = 'position-label';
        label.textContent = pos.label;
        slot.appendChild(label);

        pitch.appendChild(slot);
    });

    // Определение типа позиции игрока
    function getPlayerType(position) {
        if (position.includes('Goalkeeper')) return 'goalkeeper';
        if (position.includes('Back') || position.includes('Center Back')) return 'defender';
        if (position.includes('Midfielder')) return 'midfielder';
        if (position.includes('Forward') || position.includes('Striker')) return 'forward';
        return 'other';
    }

    // Создание элемента игрока
    function createPlayerElement(player) {
        const playerElement = document.createElement('div');
        const playerType = getPlayerType(player.position);
        playerElement.className = `player-item ${playerType}`;
        playerElement.dataset.playerId = player.id;
        playerElement.dataset.position = player.position;

        const nameElement = document.createElement('div');
        nameElement.className = 'player-name';
        nameElement.textContent = player.name;

        const positionElement = document.createElement('div');
        positionElement.className = 'player-position text-muted';
        positionElement.textContent = player.position;

        playerElement.appendChild(nameElement);
        playerElement.appendChild(positionElement);

        return playerElement;
    }

    // Показ сообщений
    function showMessage(text, type = 'success') {
        saveStatus.textContent = text;
        saveStatus.className = `alert alert-${type} mt-2`;
        setTimeout(() => {
            saveStatus.textContent = '';
            saveStatus.className = '';
        }, 3000);
    }

    // Сохранение состава
    function saveTeamLineup() {
        const lineup = {};
        document.querySelectorAll('.player-slot').forEach(slot => {
            const playerElem = slot.querySelector('.player-item');
            if (playerElem) {
                lineup[slot.dataset.position] = playerElem.dataset.playerId;
            }
        });

        showMessage('Сохранение...');
        fetch(`/clubs/detail/${clubId}/save-team-lineup/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(lineup)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage('Состав успешно сохранен!');
            } else {
                showMessage('Ошибка при сохранении', 'danger');
            }
        })
        .catch(error => {
            showMessage('Ошибка сервера', 'danger');
            console.error('Error saving lineup:', error);
        });
    }

    // Загрузка текущего состава
    function loadTeamLineup() {
        fetch(`/clubs/detail/${clubId}/get-team-lineup/`)
            .then(response => response.json())
            .then(data => {
                if (data.lineup) {
                    Object.entries(data.lineup).forEach(([position, playerId]) => {
                        const slot = document.querySelector(`.player-slot[data-position="${position}"]`);
                        const player = document.querySelector(`.player-item[data-player-id="${playerId}"]`);
                        if (slot && player) {
                            slot.appendChild(player);
                        }
                    });
                }
            })
            .catch(error => {
                showMessage('Ошибка загрузки состава', 'danger');
                console.error('Error loading lineup:', error);
            });
    }

    // Сброс состава
    function resetLineup() {
        document.querySelectorAll('.player-slot .player-item').forEach(player => {
            playerList.appendChild(player);
        });
        saveTeamLineup();
        showMessage('Состав сброшен');
    }

    resetButton.addEventListener('click', resetLineup);

    // Инициализация Sortable
    function initializeSortable() {
        new Sortable(playerList, {
            group: 'shared',
            animation: 150,
            onEnd: saveTeamLineup
        });

        document.querySelectorAll('.player-slot').forEach(slot => {
            new Sortable(slot, {
                group: 'shared',
                animation: 150,
                onAdd: function(evt) {
                    const slotElement = evt.to;
                    const newPlayer = evt.item;
                    const slotType = slotElement.dataset.type;
                    const playerPosition = newPlayer.dataset.position;

                    // Проверка соответствия позиции
                    let isValid = false;
                    switch (slotType) {
                        case 'goalkeeper':
                            isValid = playerPosition.includes('Goalkeeper');
                            break;
                        case 'defender':
                            isValid = playerPosition.includes('Back') || playerPosition.includes('Center Back');
                            break;
                        case 'midfielder':
                            isValid = playerPosition.includes('Midfielder');
                            break;
                        case 'forward':
                            isValid = playerPosition.includes('Forward') || playerPosition.includes('Striker');
                            break;
                    }

                    if (!isValid) {
                        playerList.appendChild(newPlayer);
                        showMessage('Неверная позиция игрока!', 'danger');
                        return;
                    }
                    
                    // Удаляем всех существующих игроков из слота
                    slotElement.querySelectorAll('.player-item').forEach(player => {
                        if (player !== newPlayer) {
                            playerList.appendChild(player);
                        }
                    });
                    
                    // Перемещаем нового игрока в слот
                    slotElement.appendChild(newPlayer);
                    saveTeamLineup();
                }
            });
        });
    }

    // Загрузка игроков
    fetch(`/clubs/detail/${clubId}/get-players/`)
        .then(response => response.json())
        .then(players => {
            players.forEach(player => {
                const playerElement = createPlayerElement(player);
                playerList.appendChild(playerElement);
            });

            initializeSortable();
            loadTeamLineup();
        })
        .catch(error => {
            showMessage('Ошибка загрузки игроков', 'danger');
            console.error('Error loading players:', error);
        });

    // Получение CSRF токена
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
});