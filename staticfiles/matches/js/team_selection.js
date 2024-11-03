document.addEventListener('DOMContentLoaded', function() {
    const pitch = document.getElementById('pitch');
    const playerList = document.getElementById('playerList');
    const resetButton = document.createElement('button');
    resetButton.textContent = 'Reset Selection';
    resetButton.id = 'resetTeam';
    document.body.appendChild(resetButton);
    
    const saveStatus = document.createElement('span');
    saveStatus.id = 'saveStatus';
    document.body.appendChild(saveStatus);

    const clubId = document.getElementById('clubId').value;
    let saveTimeout;

    // Создание слотов для игроков на поле
    const positions = [
        {top: '10%', left: '50%'},  // GK
        {top: '30%', left: '20%'}, {top: '30%', left: '40%'},  // DEF
        {top: '30%', left: '60%'}, {top: '30%', left: '80%'},
        {top: '60%', left: '30%'}, {top: '60%', left: '50%'},  // MID
        {top: '60%', left: '70%'},
        {top: '80%', left: '30%'}, {top: '80%', left: '50%'},  // FWD
        {top: '80%', left: '70%'}
    ];

    positions.forEach((pos, index) => {
        const slot = document.createElement('div');
        slot.className = 'player-slot';
        slot.style.top = pos.top;
        slot.style.left = pos.left;
        slot.dataset.position = index;
        pitch.appendChild(slot);
    });

    function autoSave() {
        clearTimeout(saveTimeout);
        saveStatus.textContent = 'Saving...';
        saveTimeout = setTimeout(() => {
            saveTeamSelection();
        }, 1000); // Сохраняем через 1 секунду после последнего изменения
    }

    function saveTeamSelection() {
        const selection = {};
        document.querySelectorAll('.player-slot').forEach(slot => {
            const playerElem = slot.querySelector('.player-item');
            if (playerElem) {
                selection[slot.dataset.position] = playerElem.dataset.playerId;
            }
        });

        fetch(`/clubs/${clubId}/save-team-lineup/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(selection)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                saveStatus.textContent = 'Saved';
                setTimeout(() => {
                    saveStatus.textContent = '';
                }, 2000);
            } else {
                saveStatus.textContent = 'Save failed';
            }
        })
        .catch(error => {
            saveStatus.textContent = 'Save failed';
        });
    }

    function loadPreviousSelection() {
        fetch(`/clubs/${clubId}/get-team-lineup/`)
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
            });
    }

    function resetSelection() {
        document.querySelectorAll('.player-slot .player-item').forEach(player => {
            playerList.appendChild(player);
        });
        autoSave();
    }

    function initializeSortable() {
        new Sortable(playerList, {
            group: 'shared',
            animation: 150,
            onEnd: autoSave
        });

        document.querySelectorAll('.player-slot').forEach(slot => {
            new Sortable(slot, {
                group: 'shared',
                animation: 150,
                onAdd: function(evt) {
                    const slotElement = evt.to;
                    const newPlayer = evt.item;
                    
                    // Удаляем всех существующих игроков из слота
                    slotElement.querySelectorAll('.player-item').forEach(player => {
                        if (player !== newPlayer) {
                            playerList.appendChild(player);
                        }
                    });
                    
                    // Перемещаем нового игрока в слот
                    slotElement.appendChild(newPlayer);
                    
                    autoSave();
                }
            });
        });
    }

    fetch(`/clubs/${clubId}/get-players/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(players => {
            if (!Array.isArray(players) || players.length === 0) {
                playerList.textContent = 'No players available';
                return;
            }
            players.forEach(player => {
                const playerElem = document.createElement('div');
                playerElem.className = 'player-item';
                playerElem.textContent = `${player.name} (${player.position})`;
                playerElem.dataset.playerId = player.id;
                playerList.appendChild(playerElem);
            });

            initializeSortable();
            loadPreviousSelection();
        })
        .catch(error => {
            playerList.textContent = 'Error loading players. Please try again later.';
        });

    resetButton.addEventListener('click', resetSelection);

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