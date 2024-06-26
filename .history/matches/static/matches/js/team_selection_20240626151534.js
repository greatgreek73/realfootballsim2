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

    let saveTimeout;

    // Функция автоматического сохранения
    function autoSave() {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            saveTeamSelection();
        }, 2000); // Сохраняем через 2 секунды после последнего изменения
    }

    // Функция сохранения выбора команды
    function saveTeamSelection() {
        const selection = {};
        document.querySelectorAll('.player-slot').forEach(slot => {
            const playerElem = slot.querySelector('.player-item');
            if (playerElem) {
                selection[slot.dataset.position] = playerElem.dataset.playerId;
            }
        });

        saveStatus.textContent = 'Saving...';

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
        });
    }

    // Функция загрузки предыдущего состава
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

    // Функция сброса выбора
    function resetSelection() {
        document.querySelectorAll('.player-slot .player-item').forEach(player => {
            playerList.appendChild(player);
        });
        autoSave();
    }

    // Инициализация Sortable и добавление слушателей событий
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

    resetButton.addEventListener('click', resetSelection);

    // Загрузка предыдущего состава при инициализации страницы
    loadPreviousSelection();
});