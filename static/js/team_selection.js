document.addEventListener('DOMContentLoaded', function() {
    const pitch = document.getElementById('pitch');
    const playerList = document.getElementById('playerList');
    const clubId = document.getElementById('clubId').value;
    const resetButton = document.getElementById('resetButton');
    const saveStatus = document.getElementById('saveStatus');
    const tacticSelect = document.getElementById('tacticSelect');

    // Configuration of player slots on the pitch
    const positions = [
        { top: '10%', left: '50%', type: 'goalkeeper', label: 'GK' },  // GK
        { top: '30%', left: '20%', type: 'defender',   label: 'LB' },  // DEF
        { top: '30%', left: '40%', type: 'defender',   label: 'CB' },
        { top: '30%', left: '60%', type: 'defender',   label: 'CB' },
        { top: '30%', left: '80%', type: 'defender',   label: 'RB' },
        { top: '60%', left: '30%', type: 'midfielder', label: 'LM' },  // MID
        { top: '60%', left: '50%', type: 'midfielder', label: 'CM' },
        { top: '60%', left: '70%', type: 'midfielder', label: 'RM' },
        { top: '80%', left: '30%', type: 'forward',    label: 'LF' },  // FWD
        { top: '80%', left: '50%', type: 'forward',    label: 'ST' },
        { top: '80%', left: '70%', type: 'forward',    label: 'RF' }
    ];

    // Create slots on the pitch
    positions.forEach((pos, index) => {
        const slot = document.createElement('div');
        slot.className = 'player-slot';
        slot.style.top = pos.top;
        slot.style.left = pos.left;
        slot.dataset.position = index;     // numeric index (0..10)
        slot.dataset.type = pos.type;      // "goalkeeper"/"defender"/"midfielder"/"forward"

        // Add small label for position
        const label = document.createElement('div');
        label.className = 'position-label';
        label.textContent = pos.label;
        slot.appendChild(label);

        pitch.appendChild(slot);
    });

    // Map position string to "type"
    function getPlayerType(position) {
        if (position.includes('Goalkeeper')) return 'goalkeeper';
        if (position.includes('Back')) return 'defender'; 
        if (position.includes('Midfielder')) return 'midfielder';
        if (position.includes('Forward') || position.includes('Striker')) return 'forward';
        return 'other';
    }

    // Create DOM element for player
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

    // Show message in #saveStatus
    function showMessage(text, type = 'success') {
        saveStatus.textContent = text;
        saveStatus.className = `alert alert-${type} mt-2`;
        setTimeout(() => {
            saveStatus.textContent = '';
            saveStatus.className = '';
        }, 3000);
    }

    // Save lineup to the server
    function saveTeamLineup() {
        const lineup = {};
        // Collect players from each slot
        document.querySelectorAll('.player-slot').forEach(slot => {
            const playerElem = slot.querySelector('.player-item');
            if (playerElem) {
                lineup[slot.dataset.position] = playerElem.dataset.playerId;
            }
        });

        // Also capture the tactic from the <select>:
        const tacticValue = tacticSelect ? tacticSelect.value : 'balanced';

        showMessage('Saving lineup...');

        // IMPORTANT: sending { lineup: { ... }, tactic: "..." }
        const payload = {
            lineup: lineup,
            tactic: tacticValue
        };

        fetch(`/clubs/detail/${clubId}/save-team-lineup/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage('Lineup successfully saved!');
            } else {
                showMessage(`Error saving lineup: ${data.error || ''}`, 'danger');
            }
        })
        .catch(error => {
            showMessage('Server error', 'danger');
            console.error('Error saving lineup:', error);
        });
    }

    // Load existing lineup from server
    function loadTeamLineup() {
        fetch(`/clubs/detail/${clubId}/get-team-lineup/`)
            .then(response => response.json())
            .then(data => {
                if (data.lineup) {
                    // if data.lineup => object { "0": "42", "1": "55", ...}
                    Object.entries(data.lineup).forEach(([position, playerId]) => {
                        // Find the slot by position
                        const slot = document.querySelector(`.player-slot[data-position="${position}"]`);
                        // Find the actual player item
                        const player = document.querySelector(`.player-item[data-player-id="${playerId}"]`);
                        if (slot && player) {
                            slot.appendChild(player);
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

    // Reset lineup => move all players back to playerList
    function resetLineup() {
        document.querySelectorAll('.player-slot .player-item').forEach(player => {
            playerList.appendChild(player);
        });
        saveTeamLineup();
        showMessage('Lineup has been reset');
    }

    resetButton.addEventListener('click', resetLineup);

    // Initialize Sortable for drag-and-drop
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

                    // Validate position
                    let isValid = false;
                    switch (slotType) {
                        case 'goalkeeper':
                            isValid = playerPosition.includes('Goalkeeper');
                            break;
                        case 'defender':
                            isValid = playerPosition.includes('Back');
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
                        showMessage('Invalid player position!', 'danger');
                        return;
                    }
                    
                    // Remove existing player from that slot (if any)
                    slotElement.querySelectorAll('.player-item').forEach(existingPlayer => {
                        if (existingPlayer !== newPlayer) {
                            playerList.appendChild(existingPlayer);
                        }
                    });
                    
                    // Put new player in the slot
                    slotElement.appendChild(newPlayer);
                    saveTeamLineup();
                }
            });
        });
    }

    // Fetch the players and build list
    fetch(`/clubs/detail/${clubId}/get-players/`)
        .then(response => response.json())
        .then(players => {
            players.forEach(player => {
                const playerElement = createPlayerElement(player);
                playerList.appendChild(playerElement);
            });
            // after players are loaded, init drag-and-drop
            initializeSortable();
            // then load the saved lineup
            loadTeamLineup();
        })
        .catch(error => {
            showMessage('Error loading players', 'danger');
            console.error('Error loading players:', error);
        });

    // Helper to get CSRF token from cookie
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
