document.addEventListener('DOMContentLoaded', function() {
    const pitch = document.getElementById('pitch');
    const playerList = document.getElementById('playerList');
    const clubId = document.getElementById('clubId').value;
    const resetButton = document.getElementById('resetButton');
    const saveStatus = document.getElementById('saveStatus');
    const tacticSelect = document.getElementById('tacticSelect');

    // Конфигурация слотов: позиция на поле + тип слота + метка
    const positions = [
        { top: '10%', left: '50%', type: 'goalkeeper', label: 'GK' },  
        { top: '30%', left: '20%', type: 'defender',   label: 'LB' },  
        { top: '30%', left: '40%', type: 'defender',   label: 'CB' },
        { top: '30%', left: '60%', type: 'defender',   label: 'CB' },
        { top: '30%', left: '80%', type: 'defender',   label: 'RB' },
        { top: '60%', left: '30%', type: 'midfielder', label: 'LM' },  
        { top: '60%', left: '50%', type: 'midfielder', label: 'CM' },
        { top: '60%', left: '70%', type: 'midfielder', label: 'RM' },
        { top: '80%', left: '30%', type: 'forward',    label: 'LF' },  
        { top: '80%', left: '50%', type: 'forward',    label: 'ST' },
        { top: '80%', left: '70%', type: 'forward',    label: 'RF' }
    ];

    // ----------------------------------------------------------------
    // Создаём слоты на поле
    positions.forEach((pos, index) => {
        const slot = document.createElement('div');
        slot.className = 'player-slot';
        slot.style.top = pos.top;
        slot.style.left = pos.left;

        slot.dataset.position = index;    // индекс (0..10)
        slot.dataset.type = pos.type;     // "goalkeeper"/"defender"/"midfielder"/"forward"

        // Добавляем надпись (label) - "GK", "RB", "LB" и т.д.
        const label = document.createElement('div');
        label.className = 'position-label';
        label.textContent = pos.label;
        slot.appendChild(label);

        pitch.appendChild(slot);
    });

    // ----------------------------------------------------------------
    // Определяем функцию, которая сопоставляет строку позиций игрока
    // (например "Goalkeeper", "Center Back") с типом для css.
    function getPlayerType(position) {
        if (!position) return 'other';
        if (position.toLowerCase().includes('goalkeeper')) return 'goalkeeper';
        if (position.toLowerCase().includes('back') ||
            position.toLowerCase().includes('defender')) return 'defender';
        if (position.toLowerCase().includes('midfielder')) return 'midfielder';
        if (position.toLowerCase().includes('forward') ||
            position.toLowerCase().includes('striker')) return 'forward';
        return 'other';
    }

    // ----------------------------------------------------------------
    // Создаём DOM-элемент для каждого игрока (из get-players)
    function createPlayerElement(player) {
        const playerElement = document.createElement('div');
        const playerType = getPlayerType(player.position);

        playerElement.className = `player-item ${playerType}`;

        // Сохраняем в data-атрибутах:
        // playerId      -> айди игрока
        // playerPosition-> реальная позиция игрока (Forward, Defender и т.п.)
        playerElement.dataset.playerId = player.id;
        playerElement.dataset.playerPosition = player.position || ''; 

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

    // ----------------------------------------------------------------
    // Показать сообщение в #saveStatus
    function showMessage(text, type = 'success') {
        saveStatus.textContent = text;
        saveStatus.className = `alert alert-${type} mt-2`;
        setTimeout(() => {
            saveStatus.textContent = '';
            saveStatus.className = '';
        }, 4000);
    }

    // ----------------------------------------------------------------
    // Сохранение состава на сервер
    function saveTeamLineup() {
        // Собираем lineup
        const lineup = {};
        document.querySelectorAll('.player-slot').forEach(slot => {
            const playerElem = slot.querySelector('.player-item');
            if (playerElem) {
                // Вместо "lineup[slotIndex] = playerId" теперь делаем объект
                lineup[slot.dataset.position] = {
                    playerId: playerElem.dataset.playerId,
                    playerPosition: playerElem.dataset.playerPosition,
                    slotType: slot.dataset.type,
                    slotLabel: slot.querySelector('.position-label').textContent
                };
            }
        });

        // Забираем тактику
        const tacticValue = tacticSelect ? tacticSelect.value : 'balanced';

        // Формируем payload
        const payload = {
            lineup: lineup,
            tactic: tacticValue
        };

        // Для отладки (в консоли браузера)
        console.log('Sending lineup payload:', payload);

        fetch(`/clubs/detail/${clubId}/save-team-lineup/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body: JSON.stringify(payload),
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage('Lineup saved!');
            } else {
                showMessage(`Error saving lineup: ${data.error || ''}`, 'danger');
            }
        })
        .catch(error => {
            showMessage('Server error', 'danger');
            console.error('Error saving lineup:', error);
        });
    }

    // ----------------------------------------------------------------
    // Загрузка состава с сервера
    function loadTeamLineup() {
        fetch(`/clubs/detail/${clubId}/get-team-lineup/`)
            .then(response => response.json())
            .then(data => {
                if (data.lineup) {
                    // data.lineup => { "0": {...}, "1": {...}, ... }
                    Object.entries(data.lineup).forEach(([slotIndex, details]) => {
                        // details = { playerId, playerPosition, slotType, slotLabel, ... }
                        const slot = document.querySelector(`.player-slot[data-position="${slotIndex}"]`);
                        if (!slot || !details) return;

                        const playerId = details.playerId;
                        // Найдём элемент игрока
                        const playerElem = document.querySelector(`.player-item[data-player-id="${playerId}"]`);
                        if (playerElem) {
                            slot.appendChild(playerElem);
                        }
                    });
                }
                if (data.tactic) {
                    tacticSelect.value = data.tactic;
                }
            })
            .catch(error => {
                showMessage('Error loading lineup', 'danger');
                console.error('Error loading lineup:', error);
            });
    }

    // ----------------------------------------------------------------
    // Сбросить состав (перетащить всех игроков обратно в список)
    function resetLineup() {
        document.querySelectorAll('.player-slot .player-item').forEach(player => {
            playerList.appendChild(player);
        });
        saveTeamLineup();
        showMessage('Lineup has been reset');
    }
    resetButton.addEventListener('click', resetLineup);

    // ----------------------------------------------------------------
    // Инициализация SortableJS для drag-and-drop
    function initializeSortable() {
        // Зона со списком игроков
        new Sortable(playerList, {
            group: 'shared',
            animation: 150,
            onEnd: saveTeamLineup
        });

        // Каждый слот
        document.querySelectorAll('.player-slot').forEach(slot => {
            new Sortable(slot, {
                group: 'shared',
                animation: 150,
                onAdd: function(evt) {
                    const slotElement = evt.to;
                    const newPlayer = evt.item;
                    const slotType = slotElement.dataset.type;
                    const playerRealPosition = newPlayer.dataset.playerPosition;

                    // Простейшая проверка соответствия
                    let isValid = false;
                    switch (slotType) {
                        case 'goalkeeper':
                            // Считаем, что "Goalkeeper" есть в playerRealPosition
                            isValid = /goalkeeper/i.test(playerRealPosition);
                            break;
                        case 'defender':
                            isValid = /back|defender/i.test(playerRealPosition);
                            break;
                        case 'midfielder':
                            isValid = /midfielder/i.test(playerRealPosition);
                            break;
                        case 'forward':
                            isValid = /forward|striker/i.test(playerRealPosition);
                            break;
                        default:
                            isValid = true; // или false — на ваше усмотрение
                            break;
                    }

                    if (!isValid) {
                        playerList.appendChild(newPlayer);
                        showMessage('Invalid player position!', 'danger');
                        return;
                    }

                    // Если в слоте уже кто-то есть, выкидываем его обратно в список
                    slotElement.querySelectorAll('.player-item').forEach(existingPlayer => {
                        if (existingPlayer !== newPlayer) {
                            playerList.appendChild(existingPlayer);
                        }
                    });

                    // Кладём нового игрока в слот
                    slotElement.appendChild(newPlayer);
                    saveTeamLineup();
                }
            });
        });
    }

    // ----------------------------------------------------------------
    // При загрузке страницы: сначала получаем игроков, заполняем список, 
    // а затем грузим сохранённый состав
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
            showMessage('Error loading players', 'danger');
            console.error('Error loading players:', error);
        });
});
