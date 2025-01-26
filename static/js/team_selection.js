// static/js/team_selection.js

document.addEventListener('DOMContentLoaded', function() {
    const pitch = document.getElementById('pitch');
    const playerList = document.getElementById('playerList');
    const clubId = document.getElementById('clubId').value;
    const resetButton = document.getElementById('resetButton');
    const saveStatus = document.getElementById('saveStatus');
    const tacticSelect = document.getElementById('tacticSelect');

    // --------------------------------------
    // Конфигурация слотов (вратарь внизу, 3 CF вверху)
    // --------------------------------------
    const positions = [
        // 3 центральных форварда (сверху)
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

        // GK (1) внизу
        { top: '90%', left: '50%', type: 'goalkeeper', label: 'GK' }
    ];

    // Рисуем слоты
    positions.forEach((pos, index) => {
        const slot = document.createElement('div');
        slot.className = 'player-slot empty';
        slot.style.top = pos.top;
        slot.style.left = pos.left;

        slot.dataset.position = String(index); // уникальный индекс
        slot.dataset.type = pos.type;          // cf1, lam, cdm2, ldef, etc.

        const label = document.createElement('div');
        label.className = 'position-label';
        label.textContent = pos.label;
        slot.appendChild(label);

        pitch.appendChild(slot);
    });

    // --------------------------------------
    // Определяем базовый "тип" игрока по названию позиции (его real pos)
    // (goalkeeper, defender, midfielder, forward)
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
    // Проверяем, подходит ли игрок под slotType
    // (пример: cf1 => forward, lam => attacking-mid, etc.)
    // --------------------------------------
    function isValidPosition(playerType, slotType, fullPositionName = '') {
        const lowerPos = (fullPositionName || '').toLowerCase();

        switch (slotType) {
            case 'goalkeeper':
                return (playerType === 'goalkeeper');

            // форварды
            case 'cf1':
            case 'cf2':
            case 'cf3':
                return (playerType === 'forward');

            // атак. полузащита
            case 'lam':
            case 'ram':
            case 'cam1':
            case 'cam2':
                // для "Attacking Midfielder" => midfielder, forward
                return (
                    lowerPos.includes('attacking midfielder') || 
                    playerType === 'forward'
                );

            // обычная полузащита
            case 'lm':
            case 'rm':
            case 'cm1':
            case 'cm2':
            case 'cm3':
                // exclude defensive, attacking
                if (playerType !== 'midfielder') return false;
                if (lowerPos.includes('defensive')) return false;
                if (lowerPos.includes('attacking')) return false;
                return true;

            // опорная зона
            case 'ldm':
            case 'rdm':
            case 'cdm1':
            case 'cdm2':
            case 'cdm3':
                return lowerPos.includes('defensive midfielder');

            // защита
            case 'ldef':
            case 'rdef':
            case 'cdef1':
            case 'cdef2':
            case 'cdef3':
                return (playerType === 'defender');

            default:
                return false;
        }
    }

    // --------------------------------------
    // Создаём DOM-элемент игрока (в списке справа)
    // --------------------------------------
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

        // Сохраняем {attack: X, defense: Y} для дальнейших расчётов
        if (player.attributes) {
            playerElement.dataset.attrs = JSON.stringify(player.attributes);
        }

        return playerElement;
    }

    // --------------------------------------
    // Показать сообщение
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
    // Сохранение состава (payload -> POST /save-team-lineup/)
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
                showMessage(`Error saving lineup: ${data.error || ''}`, 'danger');
            }
        })
        .catch(err => {
            showMessage('Server error', 'danger');
            console.error('Error saving lineup:', err);
        });
    }

    // --------------------------------------
    // Функция расчёта суммарных Team Attack / Team Defense
    // --------------------------------------
    function calculateTeamStats() {
        let totalAttack = 0;
        let totalDefense = 0;

        // Перебираем все занятые слоты
        document.querySelectorAll('.player-slot:not(.empty) .player-item').forEach(playerEl => {
            const raw = playerEl.dataset.attrs;
            if (!raw) return;

            const attrs = JSON.parse(raw);
            const att = parseInt(attrs.attack)  || 0; // finishing+dribbling+...
            const def = parseInt(attrs.defense) || 0; // marking+tackling+heading

            // Смотрим slotType (cf1, lam, gk, ldef, etc.)
            const slotType = playerEl.parentNode.dataset.type;

            // --- Team Attack ---
            // "Учитывать всех, кроме вратаря, защитников, опорников"
            // => т. е. считаем if slotType in [ 'cf1','cf2','cf3','lam','ram','cam1','cam2','??']
            if (isAttackSlot(slotType)) {
                totalAttack += att;
            }

            // --- Team Defense ---
            // "Учитывать всех, кроме форвардов и атак. полузащитников"
            // => если slotType не forward/cam
            // => (gk, defenders, cdm, cm, etc.)
            if (isDefenseSlot(slotType)) {
                totalDefense += def;
            }
        });

        // Выводим
        const atkSpan = document.getElementById('attackVal');
        const defSpan = document.getElementById('defenseVal');
        if (atkSpan) atkSpan.textContent = totalAttack;
        if (defSpan) defSpan.textContent = totalDefense;
    }

    // Хелперы для слотов
    function isAttackSlot(slotType) {
        // Считаем "cf1/cf2/cf3" и "lam/ram/cam1/cam2" 
        // (возможно, ещё "lm/rm/cm?" — если вы хотите их считать атакой?)
        return [
            'cf1','cf2','cf3',
            'lam','ram','cam1','cam2'
        ].includes(slotType);
    }

    function isDefenseSlot(slotType) {
        // учёт защиты "все, кроме форвардов и атак. полузащитников"
        // => вернём true, если slotType не входит в вышеуказанный массив
        // (и не forward)
        if (['cf1','cf2','cf3','lam','ram','cam1','cam2'].includes(slotType)) {
            return false;
        }
        return true;
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
    // Инициализация перетаскивания
    // --------------------------------------
    function initializeSortable() {
        // Список свободных игроков (playerList)
        new Sortable(playerList, {
            group: 'shared',
            animation: 150,
            onStart: function(evt) {
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
                    slot.classList.remove('highlight');
                    slot.classList.remove('dragover');
                });
                saveTeamLineup();
                calculateTeamStats();
            }
        });

        // Слоты на поле
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

                        // Если там уже лежал другой игрок, его вернём в playerList
                        slotEl.querySelectorAll('.player-item').forEach(ex => {
                            if (ex !== newPlayer) {
                                playerList.appendChild(ex);
                                slotEl.classList.add('empty');
                            }
                        });

                        slotEl.appendChild(newPlayer);
                        saveTeamLineup();
                        calculateTeamStats();
                    } else {
                        // Вернём обратно
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
    // Загрузить список игроков + инициализация
    // --------------------------------------
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
                // Пересчитываем
                calculateTeamStats();
            })
            .catch(err => {
                console.error('Error loading lineup:', err);
                showMessage('Error loading lineup', 'danger');
            });
    }
});
