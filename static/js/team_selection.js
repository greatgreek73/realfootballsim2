// team_selection.js
document.addEventListener('DOMContentLoaded', function() {
    const pitch = document.getElementById('pitch');
    const playerList = document.getElementById('playerList');
    const clubId = document.getElementById('clubId').value;
    const resetButton = document.getElementById('resetButton');
    const saveStatus = document.getElementById('saveStatus');
    const tacticSelect = document.getElementById('tacticSelect');

    // -------------------------------
    // Конфигурация слотов
    // 1) GK (1 слот)
    // 2) Защита (defense): 5 слотов (ldef, rdef, cdef1, cdef2, cdef3)
    // 3) Опорная зона (defensive midfield): 5 слотов (ldm, rdm, cdm1, cdm2, cdm3)
    // 4) Полузащита (midfield): 5 слотов (lm, rm, cm1, cm2, cm3)
    // 5) Атакующая полузащита: 4 слота (lam, ram, cam1, cam2)
    // 6) Форварды (3 центральных): cf1, cf2, cf3

    const positions = [
        // 3 центральных форварда
        { top: '15%', left: '35%', type: 'cf1',  label: 'CF1' },
        { top: '15%', left: '50%', type: 'cf2',  label: 'CF2' },
        { top: '15%', left: '65%', type: 'cf3',  label: 'CF3' },

        // Атакующая полузащита (4)
        { top: '30%', left: '15%', type: 'lam',  label: 'LAM' },
        { top: '30%', left: '85%', type: 'ram',  label: 'RAM' },
        { top: '30%', left: '35%', type: 'cam1', label: 'CAM1' },
        { top: '30%', left: '65%', type: 'cam2', label: 'CAM2' },

        // Обычная полузащита (5)
        { top: '45%', left: '15%', type: 'lm',  label: 'LM' },
        { top: '45%', left: '85%', type: 'rm',  label: 'RM' },
        { top: '45%', left: '35%', type: 'cm1', label: 'CM1' },
        { top: '45%', left: '50%', type: 'cm2', label: 'CM2' },
        { top: '45%', left: '65%', type: 'cm3', label: 'CM3' },

        // Опорная зона (5)
        { top: '60%', left: '15%', type: 'ldm',  label: 'LDM' },
        { top: '60%', left: '85%', type: 'rdm',  label: 'RDM' },
        { top: '60%', left: '35%', type: 'cdm1', label: 'CDM1' },
        { top: '60%', left: '50%', type: 'cdm2', label: 'CDM2' },
        { top: '60%', left: '65%', type: 'cdm3', label: 'CDM3' },

        // Защита (5)
        { top: '75%', left: '15%', type: 'ldef',  label: 'LDEF' },
        { top: '75%', left: '85%', type: 'rdef',  label: 'RDEF' },
        { top: '75%', left: '35%', type: 'cdef1', label: 'CDEF1' },
        { top: '75%', left: '50%', type: 'cdef2', label: 'CDEF2' },
        { top: '75%', left: '65%', type: 'cdef3', label: 'CDEF3' },

        // GK (1)
        { top: '90%', left: '50%', type: 'goalkeeper', label: 'GK' }
    ];

    // Создаём слоты
    positions.forEach((pos, index) => {
        const slot = document.createElement('div');
        slot.className = 'player-slot empty';  // изначально пуст
        slot.style.top = pos.top;
        slot.style.left = pos.left;

        slot.dataset.position = String(index);
        slot.dataset.type = pos.type;  // напр. "ldef", "cdm2", "cam1", "cf2"

        const label = document.createElement('div');
        label.className = 'position-label';
        label.textContent = pos.label;
        slot.appendChild(label);

        pitch.appendChild(slot);
    });

    // -------------------------------
    // Определяем базовый тип игрока (goalkeeper, defender, midfielder, forward)
    function getPlayerType(positionString) {
        if (!positionString) return 'other';
        const p = positionString.toLowerCase();
        if (p.includes('goalkeeper')) return 'goalkeeper';
        if (p.includes('back') || p.includes('defender')) return 'defender';
        if (p.includes('midfielder')) return 'midfielder';
        if (p.includes('forward') || p.includes('striker')) return 'forward';
        return 'other';
    }

    // -------------------------------
    // Проверка соответствия slotType -> playerType/position
    // Например, slotType "ldm" требует "Defensive Midfielder"
    function isValidPosition(playerType, slotType, fullPositionName) {
        const pLower = (fullPositionName || '').toLowerCase();

        switch (slotType) {
            case 'goalkeeper':
                return (playerType === 'goalkeeper');

            // --- 5 защитников ---
            case 'ldef':
            case 'rdef':
            case 'cdef1':
            case 'cdef2':
            case 'cdef3':
                return (playerType === 'defender');

            // --- опорная зона ---
            case 'ldm':
            case 'rdm':
            case 'cdm1':
            case 'cdm2':
            case 'cdm3':
                // Нужно наличие "defensive midfielder"
                return pLower.includes('defensive midfielder');

            // --- обычная полузащита ---
            case 'lm':
            case 'rm':
            case 'cm1':
            case 'cm2':
            case 'cm3':
                // Должен быть midfielder, но не "defensive" и не "attacking"
                if (playerType !== 'midfielder') return false;
                if (pLower.includes('defensive midfielder')) return false;
                if (pLower.includes('attacking midfielder')) return false;
                return true;

            // --- атакующая полузащита ---
            case 'lam':
            case 'ram':
            case 'cam1':
            case 'cam2':
                // Нужно именно "attacking midfielder"
                return pLower.includes('attacking midfielder');

            // --- форварды (cf1, cf2, cf3)
            case 'cf1':
            case 'cf2':
            case 'cf3':
                return (playerType === 'forward');

            default:
                return false;
        }
    }

    // -------------------------------
    // Создаём DOM-элемент игрока
    function createPlayerElement(player) {
        const playerElement = document.createElement('div');
        const pt = getPlayerType(player.position);

        playerElement.className = `player-item ${pt}`;
        playerElement.dataset.playerId = String(player.id);
        playerElement.dataset.playerPosition = player.position || '';

        const nameEl = document.createElement('div');
        nameEl.className = 'player-name';
        nameEl.textContent = player.name;

        const posEl = document.createElement('div');
        posEl.className = 'player-position text-muted';
        posEl.textContent = player.position;

        playerElement.appendChild(nameEl);
        playerElement.appendChild(posEl);

        return playerElement;
    }

    // -------------------------------
    // Вывод сообщения
    function showMessage(msg, type = 'success') {
        saveStatus.textContent = msg;
        saveStatus.className = `alert alert-${type} mt-2`;
        setTimeout(() => {
            saveStatus.textContent = '';
            saveStatus.className = '';
        }, 4000);
    }

    // -------------------------------
    // Сохранение состава
    function saveTeamLineup() {
        const lineup = {};
        document.querySelectorAll('.player-slot').forEach(slot => {
            const playerItem = slot.querySelector('.player-item');
            if (playerItem) {
                lineup[slot.dataset.position] = {
                    playerId:       playerItem.dataset.playerId,
                    playerPosition: playerItem.dataset.playerPosition,
                    slotType:       slot.dataset.type,
                    slotLabel:      slot.querySelector('.position-label').textContent
                };
            }
        });

        const tacticVal = tacticSelect ? tacticSelect.value : 'balanced';
        const payload = {
            lineup: lineup,
            tactic: tacticVal
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
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showMessage('Lineup saved!');
            } else {
                showMessage(`Error saving lineup: ${data.error || ''}`, 'danger');
            }
        })
        .catch(err => {
            showMessage('Server error', 'danger');
            console.error('Error saving lineup:', err);
        });
    }

    // -------------------------------
    // Загрузка уже сохранённого состава
    function loadTeamLineup() {
        fetch(`/clubs/detail/${clubId}/get-team-lineup/`)
            .then(r => r.json())
            .then(data => {
                if (data.lineup) {
                    Object.entries(data.lineup).forEach(([slotIndex, details]) => {
                        const slot = document.querySelector(`.player-slot[data-position="${slotIndex}"]`);
                        if (!slot || !details) return;
                        const pid = details.playerId;
                        const pElem = document.querySelector(`.player-item[data-player-id="${pid}"]`);
                        if (pElem) {
                            slot.classList.remove('empty');
                            slot.appendChild(pElem);
                        }
                    });
                }
                if (data.tactic) {
                    tacticSelect.value = data.tactic;
                }
            })
            .catch(err => {
                showMessage('Error loading lineup', 'danger');
                console.error('Error loading lineup:', err);
            });
    }

    // -------------------------------
    // Сброс состава
    function resetLineup() {
        document.querySelectorAll('.player-slot .player-item').forEach(pl => {
            playerList.appendChild(pl);
        });
        document.querySelectorAll('.player-slot').forEach(s => {
            s.classList.add('empty');
        });
        saveTeamLineup();
        showMessage('Lineup has been reset');
    }

    if (resetButton) {
        resetButton.addEventListener('click', resetLineup);
    }

    // -------------------------------
    // Инициализация перетаскивания
    function initializeSortable() {
        new Sortable(playerList, {
            group: 'shared',
            animation: 150,
            onStart: function(evt) {
                const pPos = evt.item.dataset.playerPosition || '';
                const pType = getPlayerType(pPos);

                // Подсветим все слоты, куда можно положить
                document.querySelectorAll('.player-slot.empty').forEach(slot => {
                    if (isValidPosition(pType, slot.dataset.type, pPos)) {
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
                    const slotEl = evt.to;
                    const newPlayer = evt.item;
                    const pPos = newPlayer.dataset.playerPosition || '';
                    const pType = getPlayerType(pPos);
                    const stype = slotEl.dataset.type;

                    if (isValidPosition(pType, stype, pPos)) {
                        slotEl.classList.remove('empty');
                        slotEl.classList.remove('highlight');

                        slotEl.querySelectorAll('.player-item').forEach(ex => {
                            if (ex !== newPlayer) {
                                playerList.appendChild(ex);
                                slotEl.classList.add('empty');
                            }
                        });

                        slotEl.appendChild(newPlayer);
                        saveTeamLineup();
                    } else {
                        playerList.appendChild(newPlayer);
                        showMessage('Invalid player position!', 'danger');
                    }
                },
                onRemove: function(evt) {
                    const oldSlot = evt.from;
                    oldSlot.classList.add('empty');
                }
            });

            slot.addEventListener('dragenter', function() {
                if (slot.classList.contains('empty') && slot.classList.contains('highlight')) {
                    slot.classList.add('dragover');
                }
            });
            slot.addEventListener('dragleave', function() {
                slot.classList.remove('dragover');
            });
        });
    }

    // -------------------------------
    // 1) Загрузить список игроков,
    // 2) Инициализировать перетаскивание,
    // 3) Загрузить уже сохранённый состав
    fetch(`/clubs/detail/${clubId}/get-players/`)
        .then(r => r.json())
        .then(players => {
            playerList.innerHTML = '';
            players.forEach(pl => {
                const pel = createPlayerElement(pl);
                playerList.appendChild(pel);
            });
            initializeSortable();
            loadTeamLineup();
        })
        .catch(err => {
            showMessage('Error loading players', 'danger');
            console.error('Error loading players:', err);
        });
});
