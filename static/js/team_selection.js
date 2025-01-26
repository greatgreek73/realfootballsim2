// team_selection.js

document.addEventListener('DOMContentLoaded', function() {
    const pitch = document.getElementById('pitch');
    const playerList = document.getElementById('playerList');
    const clubId = document.getElementById('clubId').value;
    const resetButton = document.getElementById('resetButton');
    const saveStatus = document.getElementById('saveStatus');
    const tacticSelect = document.getElementById('tacticSelect');

    // --------------------------------------
    // Исходная большая конфигурация слотов
    // --------------------------------------
    const positions = [
        // 3 центральных форварда (вверху)
        { top: '15%', left: '35%', type: 'cf1',  label: 'CF1' },
        { top: '15%', left: '50%', type: 'cf2',  label: 'CF2' },
        { top: '15%', left: '65%', type: 'cf3',  label: 'CF3' },

        // Атакующая полузащита (4)
        { top: '30%', left: '15%', type: 'lam',  label: 'LAM' },
        { top: '30%', left: '85%', type: 'ram',  label: 'RAM' },
        { top: '30%', left: '35%', type: 'cam1', label: 'CAM1' },
        { top: '30%', left: '65%', type: 'cam2', label: 'CAM2' },

        // Обычная полузащита (5)
        { top: '45%', left: '15%', type: 'lm',   label: 'LM' },
        { top: '45%', left: '85%', type: 'rm',   label: 'RM' },
        { top: '45%', left: '35%', type: 'cm1',  label: 'CM1' },
        { top: '45%', left: '50%', type: 'cm2',  label: 'CM2' },
        { top: '45%', left: '65%', type: 'cm3',  label: 'CM3' },

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

        // GK (1) (внизу)
        { top: '90%', left: '50%', type: 'goalkeeper', label: 'GK' }
    ];

    // Создаём слоты на поле
    positions.forEach((pos, index) => {
        const slot = document.createElement('div');
        slot.className = 'player-slot empty';
        slot.style.top = pos.top;
        slot.style.left = pos.left;

        // Сохраняем номер и тип, чтобы потом найти слот при загрузке
        slot.dataset.position = String(index);   // уникальный индекс
        slot.dataset.type = pos.type;           // cf1, ram, cam2, gk, etc.

        const label = document.createElement('div');
        label.className = 'position-label';
        label.textContent = pos.label;
        slot.appendChild(label);

        pitch.appendChild(slot);
    });

    // --------------------------------------
    // Функция, определяющая тип игрока
    // (goalkeeper, defender, midfielder, forward, etc.)
    // --------------------------------------
    function getPlayerType(positionString) {
        if (!positionString) return 'other';
        const p = positionString.toLowerCase();

        if (p.includes('goalkeeper')) return 'goalkeeper';
        if (p.includes('back') || p.includes('defender')) return 'defender';
        if (p.includes('midfielder')) return 'midfielder';
        if (p.includes('forward') || p.includes('striker')) return 'forward';
        return 'other';
    }

    // --------------------------------------
    // Функция проверки соответствия игрока slotType
    // Например, cf1 => forward, lam => attacking midfielder, etc.
    // --------------------------------------
    function isValidPosition(playerType, slotType, fullPositionName = '') {
        const lowerPos = (fullPositionName || '').toLowerCase();

        switch (slotType) {
            // Вратарь
            case 'goalkeeper':
                return (playerType === 'goalkeeper');

            // 3 центральных форварда
            case 'cf1':
            case 'cf2':
            case 'cf3':
                return (playerType === 'forward');

            // 4 атакующих полузащитника
            case 'lam':
            case 'ram':
            case 'cam1':
            case 'cam2':
                // Часто "Attacking Midfielder" => midfielder
                // Можно проверить, содержит ли "attacking midfielder"
                return lowerPos.includes('attacking midfielder') 
                       || lowerPos.includes('forward');

            // 5 обычных полузащитников (lm, rm, cm1, cm2, cm3)
            case 'lm':
            case 'rm':
            case 'cm1':
            case 'cm2':
            case 'cm3':
                // Для обычных полузащитников: exclude "defensive midfielder" / "attacking midfielder"
                if (playerType !== 'midfielder') return false;
                if (lowerPos.includes('defensive')) return false;
                if (lowerPos.includes('attacking')) return false;
                return true;

            // 5 опорных (ldm, rdm, cdm1, cdm2, cdm3)
            case 'ldm':
            case 'rdm':
            case 'cdm1':
            case 'cdm2':
            case 'cdm3':
                // defensive midfielder
                return lowerPos.includes('defensive midfielder');

            // 5 защитников (ldef, rdef, cdef1, cdef2, cdef3)
            case 'ldef':
            case 'rdef':
            case 'cdef1':
            case 'cdef2':
            case 'cdef3':
                // back or defender
                return (playerType === 'defender');

            default:
                return false;
        }
    }

    // --------------------------------------
    // Создаём DOM-элемент игрока
    // --------------------------------------
    function createPlayerElement(player) {
        const playerElement = document.createElement('div');
        const pType = getPlayerType(player.position);

        playerElement.className = `player-item ${pType}`;
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

        // Сохраняем объект "attributes" (JS в виде JSON)
        if (player.attributes) {
            playerElement.dataset.attrs = JSON.stringify(player.attributes);
        }

        return playerElement;
    }

    // --------------------------------------
    // Показать сообщение (alert) 
    // --------------------------------------
    function showMessage(msg, type = 'success') {
        saveStatus.textContent = msg;
        saveStatus.className = `alert alert-${type} mt-2`;
        setTimeout(() => {
            saveStatus.textContent = '';
            saveStatus.className = '';
        }, 4000);
    }

    // --------------------------------------
    // Функция: сохранить состав (lineup) на сервер
    // --------------------------------------
    function saveTeamLineup() {
        const lineup = {};
        document.querySelectorAll('.player-slot').forEach(slot => {
            const playerItem = slot.querySelector('.player-item');
            if (playerItem) {
                lineup[slot.dataset.position] = {
                    playerId: playerItem.dataset.playerId,
                    playerPosition: playerItem.dataset.playerPosition,
                    slotType: slot.dataset.type,
                    slotLabel: slot.querySelector('.position-label').textContent
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
                const err = data.error || data.message || 'Unknown error';
                showMessage(`Error saving lineup: ${err}`, 'danger');
            }
        })
        .catch(err => {
            console.error('Error saving lineup:', err);
            showMessage('Server error', 'danger');
        });
    }

    // --------------------------------------
    // Функция расчёта суммарного "Team Attack"
    // --------------------------------------
    function calculateTeamStats() {
        let totalAttack = 0;
        let countPlayersOnPitch = 0;

        // Проходим по всем слотам, где есть player-item
        document.querySelectorAll('.player-slot:not(.empty) .player-item').forEach(elem => {
            const raw = elem.dataset.attrs;
            if (!raw) return;

            const attrs = JSON.parse(raw);

            // "attack" — поле, которое ваш бэкенд отдаёт 
            // (finishing + dribbling + accuracy + long_range + heading)
            const aVal = parseInt(attrs.attack) || 0;
            totalAttack += aVal;

            countPlayersOnPitch++;
        });

        // Выводим результат 
        // (можно просто вывести сумму totalAttack, 
        //  либо среднее totalAttack / countPlayersOnPitch)
        const attackSpan = document.getElementById('attackVal');
        if (attackSpan) {
            attackSpan.textContent = totalAttack.toString();
        }
    }

    // --------------------------------------
    // Сброс состава
    // --------------------------------------
    function resetLineup() {
        document.querySelectorAll('.player-slot .player-item').forEach(pl => {
            playerList.appendChild(pl);
        });
        document.querySelectorAll('.player-slot').forEach(slot => {
            slot.classList.add('empty');
        });
        saveTeamLineup();
        showMessage('Lineup has been reset');
        calculateTeamStats();
    }

    if (resetButton) {
        resetButton.addEventListener('click', resetLineup);
    }

    // --------------------------------------
    // Инициализация перетаскивания (Sortable.js)
    // --------------------------------------
    function initializeSortable() {
        // Cписок игроков (список справа/снизу)
        new Sortable(playerList, {
            group: 'shared',
            animation: 150,
            onStart: function(evt) {
                // Подсветим слоты, куда можно скинуть игрока
                const pPos = evt.item.dataset.playerPosition || '';
                const pType = getPlayerType(pPos);

                document.querySelectorAll('.player-slot.empty').forEach(slot => {
                    if (isValidPosition(pType, slot.dataset.type, pPos)) {
                        slot.classList.add('highlight');
                    }
                });
            },
            onEnd: function(evt) {
                document.querySelectorAll('.player-slot').forEach(slot => {
                    slot.classList.remove('highlight', 'dragover');
                });
                saveTeamLineup();
                calculateTeamStats();
            }
        });

        // Каждый слот
        document.querySelectorAll('.player-slot').forEach(slot => {
            new Sortable(slot, {
                group: 'shared',
                animation: 150,
                onAdd: function(evt) {
                    const slotEl = evt.to;
                    const newPlayer = evt.item;

                    const pPos = newPlayer.dataset.playerPosition || '';
                    const pType = getPlayerType(pPos);

                    if (isValidPosition(pType, slotEl.dataset.type, pPos)) {
                        slotEl.classList.remove('empty', 'highlight');
                        
                        // Если уже был игрок, выгоняем его в playerList
                        slotEl.querySelectorAll('.player-item').forEach(existingPlayer => {
                            if (existingPlayer !== newPlayer) {
                                playerList.appendChild(existingPlayer);
                                slotEl.classList.add('empty');
                            }
                        });

                        slotEl.appendChild(newPlayer);
                        saveTeamLineup();
                        calculateTeamStats();
                    } else {
                        // Вернём игрока обратно в список
                        playerList.appendChild(newPlayer);
                        showMessage('Invalid player position!', 'danger');
                        calculateTeamStats();
                    }
                },
                onRemove: function(evt) {
                    const oldSlot = evt.from;
                    oldSlot.classList.add('empty');
                    calculateTeamStats();
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

    // --------------------------------------
    // Загрузка списка игроков и lineup
    // --------------------------------------
    fetch(`/clubs/detail/${clubId}/get-players/`)
        .then(resp => resp.json())
        .then(players => {
            // Очищаем список и заполняем
            playerList.innerHTML = '';
            players.forEach(pl => {
                const pEl = createPlayerElement(pl);
                playerList.appendChild(pEl);
            });

            // Включаем Sortable
            initializeSortable();
            // Затем грузим готовый состав 
            loadTeamLineup();
        })
        .catch(err => {
            console.error('Error loading players:', err);
            showMessage('Error loading players', 'danger');
        });

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
                if (data.tactic && tacticSelect) {
                    tacticSelect.value = data.tactic;
                }
                // Посчитаем итоговую атаку
                calculateTeamStats();
            })
            .catch(err => {
                console.error('Error loading lineup:', err);
                showMessage('Error loading lineup', 'danger');
            });
    }
});
