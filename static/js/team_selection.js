// static/js/team_selection.js

document.addEventListener('DOMContentLoaded', function () {
    const pitch        = document.getElementById('pitch');
    const playerList   = document.getElementById('playerList');
    const clubIdInput  = document.getElementById('clubId'); // Получаем сам input
    const resetButton  = document.getElementById('resetButton');
    const saveStatus   = document.getElementById('saveStatus');
    const tacticSelect = document.getElementById('tacticSelect');
    const teamAttackSpan = document.getElementById('teamAttackValue'); // Предполагаемый ID для атаки
    const teamDefenseSpan = document.getElementById('teamDefenseValue'); // Предполагаемый ID для защиты

    // Проверяем наличие основных элементов
    if (!pitch || !playerList || !clubIdInput || !saveStatus || !tacticSelect) {
        console.error("One or more essential elements (pitch, playerList, clubId, saveStatus, tacticSelect) not found!");
        return; // Прерываем выполнение, если чего-то нет
    }
    const clubId = clubIdInput.value; // Получаем значение ID клуба

    // --------------------------------------------------
    // 1.  Слоты на поле (23 шт.)
    // --------------------------------------------------
    const positions = [
        // ---------- Forwards ----------
        { top: '15%', left: '35%', type: 'cf1',  label: 'CF1' },   // 0
        { top: '15%', left: '50%', type: 'cf2',  label: 'CF2' },   // 1
        { top: '15%', left: '65%', type: 'cf3',  label: 'CF3' },   // 2
        // ---------- Attacking Mid ----------
        { top: '30%', left: '15%', type: 'lam',  label: 'LAM' },  // 3
        { top: '30%', left: '85%', type: 'ram',  label: 'RAM' },  // 4
        { top: '30%', left: '35%', type: 'cam1', label: 'CAM1' }, // 5
        { top: '30%', left: '65%', type: 'cam2', label: 'CAM2' }, // 6
        // ---------- Midfield ----------
        { top: '45%', left: '15%', type: 'lm',   label: 'LM' },   // 7
        { top: '45%', left: '85%', type: 'rm',   label: 'RM' },   // 8
        { top: '45%', left: '35%', type: 'cm1',  label: 'CM1' },  // 9
        { top: '45%', left: '50%', type: 'cm2',  label: 'CM2' },  // 10
        { top: '45%', left: '65%', type: 'cm3',  label: 'CM3' },  // 11
        // ---------- Defensive Mid ----------
        { top: '60%', left: '15%', type: 'ldm',  label: 'LDM' },  // 12
        { top: '60%', left: '85%', type: 'rdm',  label: 'RDM' },  // 13
        { top: '60%', left: '35%', type: 'cdm1', label: 'CDM1' }, // 14
        { top: '60%', left: '50%', type: 'cdm2', label: 'CDM2' }, // 15
        { top: '60%', left: '65%', type: 'cdm3', label: 'CDM3' }, // 16
        // ---------- Defence ----------
        { top: '75%', left: '15%', type: 'ldef',  label: 'LDEF' },  // 17
        { top: '75%', left: '85%', type: 'rdef',  label: 'RDEF' },  // 18
        { top: '75%', left: '35%', type: 'cdef1', label: 'CDEF1' }, // 19
        { top: '75%', left: '50%', type: 'cdef2', label: 'CDEF2' }, // 20
        { top: '75%', left: '65%', type: 'cdef3', label: 'CDEF3' }, // 21
        // ---------- Goalkeeper ----------
        { top: '90%', left: '50%', type: 'goalkeeper', label: 'GK' } // 22
    ];

    // рисуем слоты на поле
    positions.forEach((pos, idx) => {
        const slot = document.createElement('div');
        slot.className = 'player-slot empty';
        slot.style.top = pos.top;
        slot.style.left = pos.left;
        slot.dataset.position = String(idx); // Индекс 0-22 для идентификации слота
        slot.dataset.type     = pos.type;    // Тип слота (cf1, gk, ...)
        slot.dataset.label    = pos.label;   // Лейбл для восстановления

        const label = document.createElement('div');
        label.className = 'position-label';
        label.textContent = pos.label;
        slot.appendChild(label);

        pitch.appendChild(slot);
    });

    // --------------------------------------------------
    // 2.  Хелперы
    // --------------------------------------------------
    function getPlayerType(posStr) {
        if (!posStr) return 'other';
        const p = posStr.toLowerCase();
        if (p.includes('goalkeeper')) return 'goalkeeper';
        if (p.includes('back') || p.includes('defender')) return 'defender';
        if (p.includes('midfielder')) return 'midfielder';
        if (p.includes('forward') || p.includes('striker')) return 'forward';
        return 'other';
    }

    function isValidPosition(playerType, slotType, fullPos = '') {
        const lower = fullPos.toLowerCase();
        switch (slotType) {
            case 'goalkeeper': return playerType === 'goalkeeper';
            case 'cf1': case 'cf2': case 'cf3': return playerType === 'forward';
            case 'lam': case 'ram': case 'cam1': case 'cam2': return lower.includes('attacking midfielder') || playerType === 'forward';
            case 'lm': case 'rm': case 'cm1': case 'cm2': case 'cm3': return playerType === 'midfielder' && !lower.includes('defensive') && !lower.includes('attacking');
            case 'ldm': case 'rdm': case 'cdm1': case 'cdm2': case 'cdm3': return lower.includes('defensive midfielder');
            case 'ldef': case 'rdef': case 'cdef1': case 'cdef2': case 'cdef3': return playerType === 'defender';
            default: return false;
        }
    }

    function createPlayerElement(player) {
        const el = document.createElement('div');
        const pTy = getPlayerType(player.position);
        el.className = `player-item ${pTy}`;
        el.draggable = true; // Важно для HTML Drag and Drop API (если SortableJS не используется или как fallback)
        el.dataset.playerId = String(player.id);
        el.dataset.playerName = player.name || `Player ${player.id}`; // Добавим имя для отображения
        el.dataset.playerPosition = player.position || '';
        el.dataset.playerClass = player.playerClass || ''; // Добавим класс, если есть
        if (player.attributes) {
            try {
                 el.dataset.attrs = JSON.stringify(player.attributes);
            } catch(e) {
                 console.error("Failed to stringify player attributes:", player.attributes, e);
            }
        }

        const name = document.createElement('div');
        name.className = 'player-name';
        name.textContent = player.name || `Player ${player.id}`;

        const pos = document.createElement('div');
        pos.className = 'player-position text-muted';
        pos.textContent = player.position || 'Unknown Position';

        el.appendChild(name);
        el.appendChild(pos);
        return el;
    }

    function showMessage(msg, type = 'success') {
        saveStatus.textContent = msg;
        saveStatus.className = `alert alert-${type} mt-2`;
        saveStatus.style.display = 'block'; // Показываем элемент
        setTimeout(() => {
            saveStatus.textContent = '';
            saveStatus.style.display = 'none'; // Скрываем элемент
            saveStatus.className = '';
        }, 4000);
    }

    // Функция для получения CSRF токена из куки
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
    const csrftoken = getCookie('csrftoken'); // Получаем токен

    // --------------------------------------------------
    // 3.  Сохранение состава (КЛЮЧЕВАЯ ФУНКЦИЯ С КЛЮЧАМИ 0-10)
    // --------------------------------------------------
    function saveTeamLineup() {
        console.log("saveTeamLineup called"); // Лог вызова функции
        const finalLineup = {};
        let goalkeeperData = null;
        const fieldPlayersData = [];

        document.querySelectorAll('.player-slot:not(.empty)').forEach(slot => {
            const playerItem = slot.querySelector('.player-item');
            if (playerItem && playerItem.dataset.playerId) { // Добавлена проверка наличия playerId
                const playerData = {
                    playerId: playerItem.dataset.playerId,
                    playerPosition: playerItem.dataset.playerPosition || '',
                    slotType: slot.dataset.type || 'unknown',
                    slotLabel: slot.dataset.label || 'Unknown',
                    // Добавим имя для отладки
                    playerName: playerItem.dataset.playerName || ''
                };

                if (slot.dataset.type === 'goalkeeper') {
                    if (!goalkeeperData) { // Берем только первого вратаря
                       goalkeeperData = playerData;
                       console.log("Goalkeeper found:", playerData);
                    } else {
                       console.warn("Multiple goalkeepers placed, using the first one found.");
                       // Возвращаем "лишнего" вратаря в список
                       playerList.appendChild(playerItem);
                       slot.innerHTML = ''; // Очищаем слот
                       const labelDiv = document.createElement('div');
                       labelDiv.className = 'position-label';
                       labelDiv.textContent = slot.dataset.label;
                       slot.appendChild(labelDiv);
                       slot.classList.add('empty');
                    }
                } else {
                    fieldPlayersData.push(playerData);
                }
            } else {
                console.warn("Player item or playerId missing in slot:", slot);
            }
        });
        console.log("Field players collected:", fieldPlayersData);

        if (goalkeeperData) {
             finalLineup["0"] = goalkeeperData;
        } else {
             console.warn("Goalkeeper not placed! Saving lineup without goalkeeper in slot 0.");
             // Не прерываем сохранение, но бэкенд должен это учесть
             // showMessage('Goalkeeper must be placed in GK slot!', 'warning');
             // return; // Можно раскомментировать для прерывания
        }

        const numFieldPlayersToTake = Math.min(10, fieldPlayersData.length);
        console.log(`Taking ${numFieldPlayersToTake} field players.`);
        for (let i = 0; i < numFieldPlayersToTake; i++) {
            finalLineup[String(i + 1)] = fieldPlayersData[i];
        }

        const totalPlayers = Object.keys(finalLineup).length;
        console.log(`Final lineup object has ${totalPlayers} players.`, finalLineup);
        if (totalPlayers < 11) {
             console.warn(`Attempting to save lineup with ${totalPlayers} players.`);
             // Можно показать предупреждение, но не прерывать
             // showMessage(`Lineup has only ${totalPlayers} players. Please select 11.`, 'warning');
        }

        const tacticVal = tacticSelect ? tacticSelect.value : 'balanced';
        const payload = {
            lineup: finalLineup,
            tactic: tacticVal
        };

        console.log("Payload to send:", JSON.stringify(payload)); // Логируем то, что отправляем

        fetch(`/clubs/detail/${clubId}/save-team-lineup/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken // Используем полученный токен
            },
            body: JSON.stringify(payload),
            credentials: 'include' // Важно для отправки куки с CSRF токеном
        })
            .then(response => {
                if (!response.ok) {
                     // Попытка прочитать тело ошибки, если оно есть
                    return response.json().then(errData => {
                         throw new Error(`HTTP error ${response.status}: ${errData.error || response.statusText}`);
                    }).catch(() => {
                         // Если тело ошибки не JSON или пустое
                         throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log("Save response:", data);
                if (data.success) {
                    showMessage('Lineup saved!');
                } else {
                    showMessage(`Error saving lineup: ${data.error || 'Unknown error'}`, 'danger');
                }
            })
            .catch(err => {
                showMessage(`Server error: ${err.message}`, 'danger');
                console.error('Error saving lineup:', err);
            });
    }

    // --------------------------------------------------
    // 4.  Team Attack / Defense
    // --------------------------------------------------
    function calculateTeamStats() {
        let totalAttack = 0;
        let totalDefense = 0;
        let playerCount = 0;

        document.querySelectorAll('.player-slot:not(.empty) .player-item').forEach(el => {
            playerCount++;
            const raw = el.dataset.attrs;
            if (!raw) return;
            try {
                const attrs = JSON.parse(raw);
                const att = parseInt(attrs.attack) || 0;
                const def = parseInt(attrs.defense) || 0;
                totalAttack += att;
                totalDefense += def;
            } catch (e) {
                console.error("Error parsing player attributes:", raw, e);
            }
        });

        // Обновляем значения в HTML, если элементы найдены
        if(teamAttackSpan) teamAttackSpan.textContent = totalAttack;
        if(teamDefenseSpan) teamDefenseSpan.textContent = totalDefense;
        // console.log(`Stats calculated: Attack=${totalAttack}, Defense=${totalDefense}, Players=${playerCount}`);
    }

    // --------------------------------------------------
    // 5.  Сброс состава
    // --------------------------------------------------
    function resetLineup(silent = false) {
        // Возвращаем всех игроков со слотов в список
        document.querySelectorAll('.player-slot .player-item').forEach(playerElement => {
            playerList.appendChild(playerElement);
        });
        // Очищаем все слоты и восстанавливаем лейблы
        document.querySelectorAll('.player-slot').forEach(slot => {
            slot.innerHTML = ''; // Удаляем все содержимое (включая старый лейбл)
            const labelDiv = document.createElement('div');
            labelDiv.className = 'position-label';
            labelDiv.textContent = slot.dataset.label || '???'; // Используем сохраненный label
            slot.appendChild(labelDiv);
            slot.classList.add('empty');
            slot.classList.remove('dragover', 'highlight');
        });

        if (!silent) {
            saveTeamLineup(); // Сохраняем пустой (или почти пустой) состав
            showMessage('Lineup has been reset');
        }
        calculateTeamStats(); // Пересчитываем статы (должны стать 0)
    }
    // Навешиваем обработчик, если кнопка есть
    if (resetButton) {
        resetButton.addEventListener('click', () => resetLineup(false));
    } else {
        console.warn("Reset button not found");
    }


    // --------------------------------------------------
    // 6.  Drag & Drop (Используем SortableJS)
    // --------------------------------------------------
    let sortablePlayerList = null;
    const sortableSlots = [];

    function initializeSortable() {
        // Уничтожаем старые экземпляры, если они есть (на случай повторной инициализации)
        if (sortablePlayerList) sortablePlayerList.destroy();
        sortableSlots.forEach(s => s.destroy());
        sortableSlots.length = 0; // Очищаем массив

        // Список доступных игроков
        sortablePlayerList = new Sortable(playerList, {
            group: { name: 'shared', pull: 'clone', put: true },
            sort: false,
            animation: 150,
            onStart: function (evt) {
                // Подсветка валидных слотов при начале перетаскивания ИЗ СПИСКА
                const item = evt.item; // Элемент, который тащим
                const pPos = item.dataset.playerPosition || '';
                const pType = getPlayerType(pPos);
                document.querySelectorAll('.player-slot.empty').forEach(slot => {
                    if (isValidPosition(pType, slot.dataset.type, pPos)) {
                        slot.classList.add('highlight');
                    }
                });
            },
            onEnd: function (evt) {
                document.querySelectorAll('.player-slot').forEach(slot => {
                    slot.classList.remove('highlight', 'dragover');
                });
                // Если элемент вернулся в исходный список, SortableJS обычно сам удаляет клон
                calculateTeamStats();
            }
        });

        // Слоты на поле
        document.querySelectorAll('.player-slot').forEach(slot => {
            const sortableSlot = new Sortable(slot, {
                group: 'shared',
                animation: 150,
                onAdd: function (evt) {
                    const targetSlot = evt.to;
                    const addedItem = evt.item;
                    const sourceListOrSlot = evt.from;

                    const pPos = addedItem.dataset.playerPosition || '';
                    const pType = getPlayerType(pPos);

                    if (isValidPosition(pType, targetSlot.dataset.type, pPos)) {
                        targetSlot.classList.remove('empty', 'highlight', 'dragover');

                        // Удаляем старого игрока, если он был (перетащили одного на другого)
                        const existingPlayers = Array.from(targetSlot.querySelectorAll('.player-item'));
                        existingPlayers.forEach(p => {
                            if (p !== addedItem) {
                                console.log(`Returning player ${p.dataset.playerName} to list from slot ${targetSlot.dataset.label}`);
                                playerList.appendChild(p); // Возвращаем в список
                            }
                        });

                        // Если игрок пришел из другого слота, очищаем тот слот
                        if (sourceListOrSlot !== playerList && sourceListOrSlot.classList.contains('player-slot')) {
                             console.log(`Player moved from slot ${sourceListOrSlot.dataset.label}`);
                             sourceListOrSlot.innerHTML = ''; // Очищаем
                             const labelDiv = document.createElement('div');
                             labelDiv.className = 'position-label';
                             labelDiv.textContent = sourceListOrSlot.dataset.label;
                             sourceListOrSlot.appendChild(labelDiv);
                             sourceListOrSlot.classList.add('empty');
                        }

                        // Убеждаемся, что добавленный элемент остался в слоте
                        // (appendChild может быть не нужен, если SortableJS его уже переместил)
                        // targetSlot.appendChild(addedItem); // Можно закомментировать, если дублирует

                        console.log(`Player ${addedItem.dataset.playerName} added to slot ${targetSlot.dataset.label}`);
                        saveTeamLineup();
                        calculateTeamStats();
                    } else {
                        // Невалидная позиция
                        showMessage('Invalid player position!', 'danger');
                        console.log(`Invalid position for player ${addedItem.dataset.playerName} in slot ${targetSlot.dataset.label}`);
                        // Отмена: SortableJS обычно сам возвращает элемент обратно в 'from'
                        // Если нет, раскомментировать: sourceListOrSlot.appendChild(addedItem);
                        targetSlot.classList.remove('highlight', 'dragover');
                         // Убедимся, что слот назначения остался/стал пустым (если игрок не встал)
                         if (!targetSlot.querySelector('.player-item')) {
                             targetSlot.classList.add('empty');
                         }
                    }
                },
                onRemove: function (evt) {
                     // Слот, ИЗ КОТОРОГО убрали игрока
                     console.log(`Player removed from slot ${evt.from.dataset.label}`);
                     evt.from.classList.add('empty');
                     // Восстанавливаем label, если его нет (на всякий случай)
                     if (!evt.from.querySelector('.position-label')) {
                         const labelDiv = document.createElement('div');
                         labelDiv.className = 'position-label';
                         labelDiv.textContent = evt.from.dataset.label;
                         evt.from.appendChild(labelDiv);
                     }
                     // Не сохраняем здесь, сохранение при onAdd
                     calculateTeamStats();
                }
            });
            sortableSlots.push(sortableSlot); // Сохраняем для возможного destroy()

            // Добавляем обработчики для подсветки вручную (dragenter/leave не всегда надежны с SortableJS)
             slot.addEventListener('dragover', (event) => {
                 event.preventDefault(); // Разрешаем drop
                 // Подсветка при наведении, если слот валидный (подсвечен классом highlight)
                 if (slot.classList.contains('highlight')) {
                    slot.classList.add('dragover');
                 }
             });
             slot.addEventListener('dragleave', () => {
                 slot.classList.remove('dragover');
             });
             slot.addEventListener('drop', () => {
                  // Убираем подсветку после drop
                 slot.classList.remove('dragover', 'highlight');
             });
        });
        console.log("SortableJS initialized");
    }

    // --------------------------------------------------
    // 7.  Загрузка игроков и начального состава
    // --------------------------------------------------
    function loadInitialData() {
        console.log("Loading initial data for club:", clubId);
        if (!clubId) {
            console.error("Club ID is missing!");
            showMessage("Cannot load data: Club ID is missing", "danger");
            return;
        }

        fetch(`/clubs/detail/${clubId}/get-players/`)
            .then(r => {
                if (!r.ok) throw new Error(`HTTP error ${r.status} loading players: ${r.statusText}`);
                return r.json();
             })
            .then(players => {
                console.log("Players loaded:", players);
                playerList.innerHTML = ''; // Очищаем список
                if (Array.isArray(players)) {
                    players.forEach(p => playerList.appendChild(createPlayerElement(p)));
                } else {
                    console.error("Received non-array data for players:", players);
                }
                initializeSortable(); // Инициализируем D&D ПОСЛЕ загрузки игроков
                loadTeamLineup();     // Загружаем состав ПОСЛЕ D&D
            })
            .catch(err => {
                console.error('Error loading players:', err);
                showMessage(`Error loading players: ${err.message}`, 'danger');
            });
    }

    function loadTeamLineup() {
        console.log("Loading team lineup");
        fetch(`/clubs/detail/${clubId}/get-team-lineup/`)
             .then(r => {
                if (!r.ok) throw new Error(`HTTP error ${r.status} loading lineup: ${r.statusText}`);
                return r.json();
             })
            .then(data => {
                console.log("Lineup data received:", data);
                // Сброс поля без сохранения/сообщения
                resetLineup(true);

                if (data.lineup && typeof data.lineup === 'object') {
                    // Ожидаем ключи "0", "1", ..., "10" от бэкенда
                    Object.entries(data.lineup).forEach(([index, details]) => {
                         if (!details || !details.playerId) {
                              console.warn(`Empty or invalid details for lineup index ${index}`);
                              return;
                         }
                         const playerId = details.playerId;
                         // Ищем игрока в списке доступных
                         const playerElement = playerList.querySelector(`.player-item[data-player-id="${playerId}"]`);

                         if (playerElement) {
                             // Ищем слот на поле. Ключ index ('0'-'10') НЕ соответствует dataset.position ('0'-'22').
                             // Нам нужно найти слот по ТИПУ (slotType), сохраненному в данных.
                             const targetSlotType = details.slotType;
                             if (!targetSlotType) {
                                 console.warn(`Missing slotType for player ${playerId} at index ${index}`);
                                 return;
                             }

                             // Ищем ПЕРВЫЙ ПУСТОЙ слот с нужным типом
                             let targetSlot = document.querySelector(`.player-slot.empty[data-type="${targetSlotType}"]`);

                             if (targetSlot) {
                                 console.log(`Placing player ${playerId} into slot ${targetSlot.dataset.label} (type: ${targetSlotType})`);
                                 targetSlot.appendChild(playerElement); // Перемещаем из списка в слот
                                 targetSlot.classList.remove('empty');
                             } else {
                                 console.warn(`Could not find empty slot with type ${targetSlotType} for player ${playerId}`);
                                 // Игрок останется в списке доступных
                             }
                         } else {
                              console.warn(`Player element with ID ${playerId} (for lineup index ${index}) not found in playerList.`);
                         }
                    });
                } else {
                    console.log("No lineup data found or invalid format in response.");
                }

                // Устанавливаем тактику
                if (data.tactic && tacticSelect) {
                    tacticSelect.value = data.tactic;
                    console.log("Tactic set to:", data.tactic);
                } else {
                     console.log("No tactic data received.");
                }

                calculateTeamStats(); // Пересчитываем статы после загрузки

            })
            .catch(err => {
                console.error('Error loading lineup:', err);
                showMessage(`Error loading lineup: ${err.message}`, 'danger');
            });
    }

    // Запускаем загрузку данных при старте
    loadInitialData();

}); // End DOMContentLoaded