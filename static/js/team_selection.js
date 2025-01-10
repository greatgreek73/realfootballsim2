document.addEventListener('DOMContentLoaded', function() {
    const pitch = document.getElementById('pitch');
    const playerList = document.getElementById('playerList');
    const clubId = document.getElementById('clubId').value;
    const resetButton = document.getElementById('resetButton');
    const saveStatus = document.getElementById('saveStatus');
    const tacticSelect = document.getElementById('tacticSelect');

    // Конфигурация слотов
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

    // Создаём слоты на поле
    positions.forEach((pos, index) => {
        const slot = document.createElement('div');
        slot.className = 'player-slot empty';  // Добавляем класс empty
        slot.style.top = pos.top;
        slot.style.left = pos.left;

        slot.dataset.position = index;
        slot.dataset.type = pos.type;

        const label = document.createElement('div');
        label.className = 'position-label';
        label.textContent = pos.label;
        slot.appendChild(label);

        pitch.appendChild(slot);
    });

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

    function isValidPosition(playerType, slotType) {
        switch (slotType) {
            case 'goalkeeper':
                return playerType === 'goalkeeper';
            case 'defender':
                return playerType === 'defender';
            case 'midfielder':
                return playerType === 'midfielder';
            case 'forward':
                return playerType === 'forward';
            default:
                return false;
        }
    }

    function createPlayerElement(player) {
        const playerElement = document.createElement('div');
        const playerType = getPlayerType(player.position);

        playerElement.className = `player-item ${playerType}`;
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

    function showMessage(text, type = 'success') {
        saveStatus.textContent = text;
        saveStatus.className = `alert alert-${type} mt-2`;
        setTimeout(() => {
            saveStatus.textContent = '';
            saveStatus.className = '';
        }, 4000);
    }

    function saveTeamLineup() {
        const lineup = {};
        document.querySelectorAll('.player-slot').forEach(slot => {
            const playerElem = slot.querySelector('.player-item');
            if (playerElem) {
                lineup[slot.dataset.position] = {
                    playerId: playerElem.dataset.playerId,
                    playerPosition: playerElem.dataset.playerPosition,
                    slotType: slot.dataset.type,
                    slotLabel: slot.querySelector('.position-label').textContent
                };
            }
        });

        const tacticValue = tacticSelect ? tacticSelect.value : 'balanced';
        const payload = {
            lineup: lineup,
            tactic: tacticValue
        };

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

    function loadTeamLineup() {
        fetch(`/clubs/detail/${clubId}/get-team-lineup/`)
            .then(response => response.json())
            .then(data => {
                if (data.lineup) {
                    Object.entries(data.lineup).forEach(([slotIndex, details]) => {
                        const slot = document.querySelector(`.player-slot[data-position="${slotIndex}"]`);
                        if (!slot || !details) return;

                        const playerId = details.playerId;
                        const playerElem = document.querySelector(`.player-item[data-player-id="${playerId}"]`);
                        if (playerElem) {
                            slot.classList.remove('empty');  // Убираем класс empty
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

    function resetLineup() {
        document.querySelectorAll('.player-slot .player-item').forEach(player => {
            playerList.appendChild(player);
        });
        document.querySelectorAll('.player-slot').forEach(slot => {
            slot.classList.add('empty');
        });
        saveTeamLineup();
        showMessage('Lineup has been reset');
    }

    if (resetButton) {
        resetButton.addEventListener('click', resetLineup);
    }

    function initializeSortable() {
        new Sortable(playerList, {
            group: 'shared',
            animation: 150,
            onStart: function(evt) {
                const playerType = getPlayerType(evt.item.dataset.playerPosition);
                document.querySelectorAll('.player-slot.empty').forEach(slot => {
                    if (isValidPosition(playerType, slot.dataset.type)) {
                        slot.classList.add('highlight');
                    }
                });
            },
            onEnd: function(evt) {
                document.querySelectorAll('.player-slot').forEach(slot => {
                    slot.classList.remove('highlight');
                    slot.classList.remove('dragover');
                });
                saveTeamLineup();
            }
        });

        document.querySelectorAll('.player-slot').forEach(slot => {
            new Sortable(slot, {
                group: 'shared',
                animation: 150,
                onAdd: function(evt) {
                    const slotElement = evt.to;
                    const newPlayer = evt.item;
                    
                    if (isValidPosition(getPlayerType(newPlayer.dataset.playerPosition), slotElement.dataset.type)) {
                        slotElement.classList.remove('empty');
                        slotElement.classList.remove('highlight');
                        
                        slotElement.querySelectorAll('.player-item').forEach(existingPlayer => {
                            if (existingPlayer !== newPlayer) {
                                playerList.appendChild(existingPlayer);
                                slotElement.classList.add('empty');
                            }
                        });
                        
                        slotElement.appendChild(newPlayer);
                        saveTeamLineup();
                    } else {
                        playerList.appendChild(newPlayer);
                        showMessage('Invalid player position!', 'danger');
                    }
                },
                onRemove: function(evt) {
                    const slot = evt.from;
                    slot.classList.add('empty');
                }
            });

            slot.addEventListener('dragenter', function(e) {
                if (slot.classList.contains('empty') && slot.classList.contains('highlight')) {
                    slot.classList.add('dragover');
                }
            });
            
            slot.addEventListener('dragleave', function(e) {
                slot.classList.remove('dragover');
            });
        });
    }

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