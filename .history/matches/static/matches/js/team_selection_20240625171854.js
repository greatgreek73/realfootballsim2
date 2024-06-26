document.addEventListener('DOMContentLoaded', function() {
    const pitch = document.getElementById('pitch');
    const playerList = document.getElementById('playerList');
    const matchId = document.getElementById('matchId').value;

    // Create player slots on the pitch
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

    // Fetch players and previous selection
    Promise.all([
        Promise.resolve(players),  // players is now provided in the template context
        fetch(`/matches/${matchId}/get-team-selection/`).then(response => response.json())
    ])
    .then(([players, previousSelection]) => {
        if (players.length === 0) {
            console.log('No players available');
            playerList.innerHTML = '<p>No players available</p>';
            return;
        }

        // Create player elements
        players.forEach(player => {
            const playerElem = createPlayerElement(player);
            playerList.appendChild(playerElem);
        });

        // Restore previous selection if exists
        if (Object.keys(previousSelection).length > 0) {
            Object.entries(previousSelection).forEach(([position, playerId]) => {
                const playerElem = document.querySelector(`.player-item[data-player-id="${playerId}"]`);
                const slot = document.querySelector(`.player-slot[data-position="${position}"]`);
                if (playerElem && slot) {
                    slot.appendChild(playerElem);
                }
            });
        }

        // Initialize Sortable for player list
        new Sortable(playerList, {
            group: 'shared',
            animation: 150,
            sort: false
        });

        // Initialize Sortable for each player slot
        document.querySelectorAll('.player-slot').forEach(slot => {
            new Sortable(slot, {
                group: 'shared',
                animation: 150,
                onAdd: function (evt) {
                    const slotElement = evt.to;
                    if (slotElement.children.length > 1) {
                        const removedElement = slotElement.children[0];
                        playerList.appendChild(removedElement);
                    }
                    saveSelection();
                },
                onRemove: function (evt) {
                    saveSelection();
                }
            });
        });
    })
    .catch(error => {
        console.error('Error fetching data:', error);
        playerList.innerHTML = '<p>Error loading players</p>';
    });

    // Helper function to create player element
    function createPlayerElement(player) {
        const playerElem = document.createElement('div');
        playerElem.className = 'player-item';
        playerElem.textContent = `${player.name} (${player.position})`;
        playerElem.dataset.playerId = player.id;
        return playerElem;
    }

    // Function to save team selection
    function saveSelection() {
        const selection = {};
        document.querySelectorAll('.player-slot').forEach(slot => {
            const playerElem = slot.querySelector('.player-item');
            if (playerElem) {
                selection[slot.dataset.position] = playerElem.dataset.playerId;
            }
        });

        fetch(`/matches/team-selection/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(selection)
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                console.error('Failed to save team selection.');
            }
        })
        .catch(error => {
            console.error('Error saving team selection:', error);
        });
    }

    // Helper function to get CSRF token
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