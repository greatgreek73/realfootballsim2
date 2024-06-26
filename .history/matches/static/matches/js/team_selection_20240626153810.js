document.addEventListener('DOMContentLoaded', function() {
    const pitch = document.getElementById('pitch');
    const playerList = document.getElementById('playerList');
    const resetButton = document.getElementById('resetTeam');
    const saveStatus = document.getElementById('saveStatus');
    const matchId = document.getElementById('matchId').value;
    let saveTimeout;

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
                saveStatus.textContent = 'Saved';
                setTimeout(() => {
                    saveStatus.textContent = '';
                }, 2000);
            } else {
                saveStatus.textContent = 'Save failed';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            saveStatus.textContent = 'Save failed';
        });
    }

    function loadPreviousSelection() {
        fetch(`/matches/${matchId}/get-team-selection/`)
            .then(response => response.json())
            .then(data => {
                if (data.selection) {
                    Object.entries(data.selection).forEach(([position, playerId]) => {
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

    fetch(`/matches/${matchId}/get-players/`)
        .then(response => response.json())
        .then(players => {
            players.forEach(player => {
                const playerElem = document.createElement('div');
                playerElem.className = 'player-item';
                playerElem.textContent = `${player.name} (${player.position})`;
                playerElem.dataset.playerId = player.id;
                playerList.appendChild(playerElem);
            });

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
                    onEnd: autoSave
                });
            });

            loadPreviousSelection();
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