document.addEventListener('DOMContentLoaded', function() {
    const pitch = document.getElementById('pitch');
    const playerList = document.getElementById('playerList');
    const saveButton = document.getElementById('saveTeam');

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

    // Fetch players and create draggable elements
    const matchId = document.getElementById('matchId').value;  // Добавьте скрытое поле с ID матча в HTML
    fetch(`/matches/${matchId}/get-players/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(players => {
            if (players.length === 0) {
                console.log('No players received from the server');
                playerList.innerHTML = '<p>No players available</p>';
                return;
            }
            players.forEach(player => {
                const playerElem = document.createElement('div');
                playerElem.className = 'player-item';
                playerElem.textContent = `${player.name} (${player.position})`;
                playerElem.dataset.playerId = player.id;
                playerList.appendChild(playerElem);
            });

            // Initialize Sortable for drag and drop
            new Sortable(playerList, {
                group: 'shared',
                animation: 150
            });

            document.querySelectorAll('.player-slot').forEach(slot => {
                new Sortable(slot, {
                    group: 'shared',
                    animation: 150,
                    max: 1  // Only one player per slot
                });
            });
        })
        .catch(error => {
            console.error('Error fetching players:', error);
            playerList.innerHTML = '<p>Error loading players</p>';
        });

    // Save team selection
    saveButton.addEventListener('click', function() {
        const selection = {};
        document.querySelectorAll('.player-slot').forEach(slot => {
            const playerElem = slot.querySelector('.player-item');
            if (playerElem) {
                selection[slot.dataset.position] = playerElem.dataset.playerId;
            }
        });

        fetch(`/matches/${matchId}/save-team-selection/`, {
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
                alert('Team selection saved successfully!');
            } else {
                alert('Failed to save team selection.');
            }
        });
    });

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