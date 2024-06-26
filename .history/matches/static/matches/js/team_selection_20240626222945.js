document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');

    const pitch = document.getElementById('pitch');
    const playerList = document.getElementById('playerList');
    const resetButton = document.createElement('button');
    resetButton.textContent = 'Reset Selection';
    resetButton.id = 'resetTeam';
    document.body.appendChild(resetButton);
    
    const saveStatus = document.createElement('span');
    saveStatus.id = 'saveStatus';
    document.body.appendChild(saveStatus);

    const matchId = document.getElementById('matchId').value;
    console.log('matchId:', matchId);

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

        console.log('Saving team selection:', selection);

        fetch(`/matches/${matchId}/save-team-selection/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(selection)
        })
        .then(response => {
            console.log('Save response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Save response data:', data);
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
            console.error('Error saving team selection:', error);
            saveStatus.textContent = 'Save failed';
        });
    }

    function loadPreviousSelection() {
        console.log('Loading previous selection');
        fetch(`/matches/${matchId}/get-team-selection/`)
            .then(response => {
                console.log('Load previous selection response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Previous selection data:', data);
                if (data.selection) {
                    Object.entries(data.selection).forEach(([position, playerId]) => {
                        const slot = document.querySelector(`.player-slot[data-position="${position}"]`);
                        const player = document.querySelector(`.player-item[data-player-id="${playerId}"]`);
                        if (slot && player) {
                            slot.appendChild(player);
                            console.log(`Player ${playerId} placed in position ${position}`);
                        } else {
                            console.warn(`Unable to place player ${playerId} in position ${position}`);
                        }
                    });
                } else {
                    console.log('No previous selection found');
                }
            })
            .catch(error => {
                console.error('Error loading previous selection:', error);
            });
    }

    function resetSelection() {
        console.log('Resetting selection');
        document.querySelectorAll('.player-slot .player-item').forEach(player => {
            playerList.appendChild(player);
        });
        autoSave();
    }

    function initializeSortable() {
        console.log('Initializing Sortable');
        new Sortable(playerList, {
            group: 'shared',
            animation: 150,
            onEnd: autoSave
        });

        document.querySelectorAll('.player-slot').forEach(slot => {
            new Sortable(slot, {
                group: 'shared',
                animation: 150,
                max: 1,
                onAdd: function(evt) {
                    const slotElement = evt.to;
                    const newPlayer = evt.item;
                    
                    // Если в слоте уже есть игрок, перемещаем его обратно в список
                    if (slotElement.children.length > 1) {
                        const oldPlayer = slotElement.children[0];
                        playerList.appendChild(oldPlayer);
                        console.log('Moved existing player back to player list');
                    }
                    
                    // Перемещаем нового игрока в начало слота
                    slotElement.insertBefore(newPlayer, slotElement.firstChild);
                    console.log(`Moved player ${newPlayer.dataset.playerId} to slot ${slotElement.dataset.position}`);
                    
                    autoSave();
                }
            });
        });
    }

    console.log('Fetching players');
    fetch(`/matches/${matchId}/get-players/`)
        .then(response => {
            console.log('Get players response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(players => {
            console.log('Received players:', players);
            if (!Array.isArray(players) || players.length === 0) {
                console.warn('No players received or invalid data format');
                playerList.textContent = 'No players available';
                return;
            }
            players.forEach(player => {
                console.log('Processing player:', player);
                const playerElem = document.createElement('div');
                playerElem.className = 'player-item';
                playerElem.textContent = `${player.name} (${player.position})`;
                playerElem.dataset.playerId = player.id;
                playerList.appendChild(playerElem);
                console.log('Player element created:', playerElem);
            });
            console.log('All players added to the list');

            initializeSortable();
            loadPreviousSelection();
        })
        .catch(error => {
            console.error('Error loading players:', error);
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