// matches/static/matches/js/live_match.js
// ----------------------------------------------------------------------------
// Лайв‑страница матча: WebSocket‑клиент, обработка статистики, моментума и т.д.
// ----------------------------------------------------------------------------

// --- Переменные верхнего уровня ------------------------------------------------
let matchId = null;            // устанавливается после DOMContentLoaded
const EVENT_DELAY_MS = 1000;

// --- Утилита получение CSRF ----------------------------------------------------
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

// --- Обработчик кнопки замены --------------------------------------------------
const replaceButton = document.querySelector('#replace-player');
if (replaceButton) {
    replaceButton.addEventListener('click', () => {
        const actionForm = document.querySelector('.matchUserAction');
        if (actionForm) actionForm.classList.remove('display-action');

        const select = document.getElementById('playerToReplaceSelect');
        if (!select || !select.value) {
            console.warn('No player selected for substitution');
            return;
        }

        const csrftoken = getCookie('csrftoken');
        fetch(`/matches/${matchId}/substitute/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ out_player_id: select.value })
        })
        .then(r => r.json())
        .then(d => console.log('Substitution response', d))
        .catch(err => console.error('Substitution error', err));
    });
}

// --- Основная логика -----------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    const matchInfoArea = document.getElementById('matchInfoArea');
    if (!matchInfoArea) {
        console.error('Element #matchInfoArea not found!');
        return;
    }

    matchId               = matchInfoArea.dataset.matchId;
    const initialStatus   = matchInfoArea.dataset.matchStatus;
    let   currentStatus   = initialStatus;
    const isLive          = initialStatus === 'in_progress';

    // Добавлено: ID команд для маппинга possessing_team
    const homeTeamId = parseInt(matchInfoArea.dataset.homeTeamId);
    const awayTeamId = parseInt(matchInfoArea.dataset.awayTeamId);

    // DOM‑элементы, используемые повторно
    const timeElement        = document.getElementById('matchTime');
    const homeScoreElement   = document.querySelector('.home-score');
    const awayScoreElement   = document.querySelector('.away-score');
    const eventsContainer    = document.getElementById('originalEvents');
    const eventsBox          = eventsContainer ? eventsContainer.querySelector('.events-box') : null;
    const statBox            = document.querySelector('.stat-box');
    const homeMomentumIcon   = document.getElementById('homeMomentumIcon');
    const awayMomentumIcon   = document.getElementById('awayMomentumIcon');
    const homeMomentumValue  = document.getElementById('homeMomentumValue');
    const awayMomentumValue  = document.getElementById('awayMomentumValue');
    const injuryActionForm   = document.querySelector('#matchUserAction-inj');
    const nextMinuteBtn      = document.getElementById('nextMinuteBtn');
    const pitchEl            = document.getElementById('pitch');

    // --- Защитные проверки на наличие ключевых узлов --------------------------
    if (!timeElement)      console.error('Element #matchTime not found!');
    if (!homeScoreElement) console.error('Element .home-score not found!');
    if (!awayScoreElement) console.error('Element .away-score not found!');
    if (!eventsBox)        console.error('Element .events-box inside #originalEvents not found!');
    if (!statBox)          console.error('Element .stat-box not found!');

    //---------------------------------------------------------------------------
    // ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
    //---------------------------------------------------------------------------

    // Показ сообщений пользователю (упрощённое, выводит в консоль)
    function showMessage(text, type = 'info') {
        console.log(`MESSAGE (${type}): ${text}`);
    }

    // Маппинг абстрактных зон на физические (с зеркалированием)
    const homeZoneMap = {
        'GK': 'goal-left',
        'DEF-R': 'left-def-top',
        'DEF-C': 'left-def-middle',
        'DEF-L': 'left-def-bottom',
        'DM-R': 'left-dm-top',
        'DM-C': 'left-dm-middle',
        'DM-L': 'left-dm-bottom',
        'MID-R': 'left-mid-top',
        'MID-C': 'left-mid-middle',
        'MID-L': 'left-mid-bottom',
        'AM-R': 'right-am-top',
        'AM-C': 'right-am-middle',
        'AM-L': 'right-am-bottom',
        'FWD-R': 'right-def-top',
        'FWD-C': 'right-def-middle',
        'FWD-L': 'right-def-bottom',
    };

    const awayZoneMap = {
        'GK': 'goal-right',
        'DEF-L': 'right-def-top',
        'DEF-C': 'right-def-middle',
        'DEF-R': 'right-def-bottom',
        'DM-L': 'right-am-top',
        'DM-C': 'right-am-middle',
        'DM-R': 'right-am-bottom',
        'MID-L': 'left-mid-top',
        'MID-C': 'left-mid-middle',
        'MID-R': 'left-mid-bottom',
        'AM-L': 'left-dm-top',
        'AM-C': 'left-dm-middle',
        'AM-R': 'left-dm-bottom',
        'FWD-L': 'left-def-top',
        'FWD-C': 'left-def-middle',
        'FWD-R': 'left-def-bottom',
    };

    // Функция для получения физической зоны
    function getPhysicalZone(abstractZone, possessingTeamId) {
        if (!abstractZone || possessingTeamId === undefined) return null;
        const teamId = parseInt(possessingTeamId);
        const isHome = !isNaN(teamId) && teamId === homeTeamId;
        const map = isHome ? homeZoneMap : awayZoneMap;
        const key = abstractZone.toUpperCase();
        return map[key] || null;
    }

    // Выделение зоны (теперь работает с физической зоной)
    function highlight(physicalZone) {
        if (!pitchEl || !physicalZone) return;
        document.querySelectorAll('#pitch .zone').forEach(z => {
            z.classList.toggle('active', z.dataset.zone === physicalZone);
        });
    }

    // Показ иконки события в зоне (теперь с физической зоной)
    function showIcon(physicalZone, type) {
        if (!pitchEl || !physicalZone) return;
        const icons = {
            goal: '⚽', shot: '⚽', shot_miss: '❌', pass: '➡️',
            interception: '🔄', foul: '⚠️', counterattack: '⚡', dribble: '↕️'
        };
        const cell = document.querySelector(`#pitch .zone[data-zone="${physicalZone}"]`);
        if (!cell) return;
        let ico = cell.querySelector('.event-icon');
        if (!ico) {
            ico = document.createElement('span');
            ico.className = 'event-icon';
            cell.appendChild(ico);
        }
        ico.textContent = icons[type] || '';
        clearTimeout(ico._timer);
        ico._timer = setTimeout(() => ico.remove(), 2000);
    }

    function setMomentum(iconEl, value, valueEl) {
        // Обновляем значение (если элемент есть)
        if (valueEl) valueEl.textContent = value;

        // Обновляем иконку в зависимости от диапазона
        if (!iconEl) return;

        iconEl.classList.remove(
            'momentum-neutral', 'momentum-positive', 'momentum-hot',
            'momentum-unstoppable', 'momentum-nervous', 'momentum-demoralized', 'momentum-panic'
        );

        if (value >= -10 && value <= 10) {
            iconEl.classList.add('momentum-neutral');
            iconEl.textContent = '😐';
        } else if (value > 10 && value <= 30) {
            iconEl.classList.add('momentum-positive');
            iconEl.textContent = '😊';
        } else if (value > 30 && value <= 60) {
            iconEl.classList.add('momentum-hot');
            iconEl.textContent = '🔥';
        } else if (value > 60) {
            iconEl.classList.add('momentum-unstoppable');
            iconEl.textContent = '🚀';
        } else if (value < -10 && value >= -30) {
            iconEl.classList.add('momentum-nervous');
            iconEl.textContent = '😟';
        } else if (value < -30 && value >= -60) {
            iconEl.classList.add('momentum-demoralized');
            iconEl.textContent = '😢';
        } else if (value < -60) {
            iconEl.classList.add('momentum-panic');
            iconEl.textContent = '😱';
        }
    }

    function updateMomentum(data) {
        if (data.home_momentum !== undefined)
            setMomentum(homeMomentumIcon, data.home_momentum, homeMomentumValue);
        if (data.away_momentum !== undefined)
            setMomentum(awayMomentumIcon, data.away_momentum, awayMomentumValue);
    }

    function updateStatistics(data) {
        if (!statBox) return;

        // Обновляем статистику по классам
        const statMap = {
            'st_passes': 'stat-passes',
            'st_shoots': 'stat-shoots',
            'st_possessions': 'stat-possessions',
            'st_fouls': 'stat-fouls',
            'st_injury': 'stat-injuries'
        };

        for (const [dataKey, className] of Object.entries(statMap)) {
            if (data[dataKey] !== undefined) {
                const element = statBox.querySelector(`.${className}`);
                if (element) {
                    element.textContent = data[dataKey];
                }
            }
        }

        // Специальная обработка для травм
        if (data.st_injury !== undefined && injuryActionForm) {
            const injuryBadge = document.getElementById('inj');
            if (injuryBadge) injuryBadge.textContent = data.st_injury;
            
            // Показываем форму замены только для команды пользователя
            const userClubId = parseInt(document.querySelector('[data-user-club-id]')?.dataset.userClubId || '0');
            if (data.st_injury > 0 && (userClubId === homeTeamId || userClubId === awayTeamId)) {
                injuryActionForm.style.display = 'block';
            }
        }
    }

    function addEventToList(evt) {
        if (!eventsBox) return;

        const item = document.createElement('div');
        item.className = 'list-group-item new-event';

        // Иконка события
        const iconMap = {
            goal: '⚽', counterattack: '⚡', interception: '🔄',
            shot_miss: '❌', pass: '➡️', foul: '⚠️', injury_concern: '✚'
        };
        const icon = iconMap[evt.event_type] || 'M';

        // Формируем HTML события
        let html = `<strong>${evt.minute}'</strong> <span class="event-icon">${icon}</span> ${evt.description}`;
        
        // Добавляем информацию об игроках
        if (evt.player_name) {
            html += ` <small class="text-muted">(${evt.player_name}`;
            if (evt.related_player_name) {
                html += ` → ${evt.related_player_name}`;
            }
            html += `)</small>`;
        }

        item.innerHTML = html;

        // Добавляем в начало списка и анимируем
        eventsBox.insertBefore(item, eventsBox.firstChild);
        requestAnimationFrame(() => {
            item.classList.add('new-event-visible');
        });

        // Прокручиваем к новому событию
        eventsContainer.scrollTop = 0;
    }

    const eventQueue = [];
    let processingQueue = false;

    function processQueue() {
        if (eventQueue.length === 0) {
            processingQueue = false;
            return;
        }
        processingQueue = true;
        const item = eventQueue.shift();
        addEventToList(item.event);
        // Добавлено: маппинг и выделение/иконка с учетом possessing_team
        if (item.data.current_zone && item.data.possessing_team_id !== undefined) {
            const physical = getPhysicalZone(item.data.current_zone, item.data.possessing_team_id);
            if (physical) {
                highlight(physical);
                showIcon(physical, item.event.event_type);
            }
        }
        if (item.event.event_type === 'goal') {
            if (item.data.home_score !== undefined) homeScoreElement.textContent = item.data.home_score;
            if (item.data.away_score !== undefined) awayScoreElement.textContent = item.data.away_score;
        }
        setTimeout(processQueue, EVENT_DELAY_MS);
    }

    function enqueueEvents(events, data) {
        events.forEach(ev => eventQueue.push({event: ev, data: data}));
        if (!processingQueue) processQueue();
    }

    // --- WebSocket -------------------------------------------------------------
    if (!isLive) {
        console.log(`Match ${matchId} is not live (${initialStatus}), WS disabled.`);
        return;
    }

    const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsUrl    = `${wsScheme}://${window.location.host}/ws/match/${matchId}/`;
    const socket   = new WebSocket(wsUrl);

    socket.onopen = () =>
        console.log(`WebSocket connected: ${wsUrl}`);

    socket.onerror = e => {
        console.error('WebSocket error:', e);
        showMessage('Connection error occurred.', 'danger');
    };

    socket.onclose = e => {
        console.log(`WebSocket closed (code ${e.code})`);
        if (currentStatus === 'in_progress')
            showMessage('Connection lost. Match updates stopped.', 'warning');
    };

    socket.onmessage = e => {
        try {
            const msg  = JSON.parse(e.data);
            if (msg.type !== 'match_update' || !msg.data) return;
            const d = msg.data;
            console.log('WS data:', d);

            // Добавлено: выделение зоны при любом обновлении (если есть current_zone и possessing_team_id)
            if (d.current_zone && d.possessing_team_id !== undefined) {
                const physical = getPhysicalZone(d.current_zone, d.possessing_team_id);
                if (physical) highlight(physical);
            }

            // 1) Первое сообщение: полный стейт + история
            if (d.partial_update === undefined && Array.isArray(d.events)) {
                eventsBox.innerHTML = '';
                d.events.forEach(addEventToList);
                if (timeElement && d.minute !== undefined)
                    timeElement.textContent = `${d.minute}'`;
                updateStatistics(d);
                updateMomentum(d);
            }

            // 2) Любое ЧАСТИЧНОЕ обновление (с событием ИЛИ без него)
            else if (d.partial_update === true) {

                // если событие есть — выводим
                if (d.events && Array.isArray(d.events) && d.events.length > 0) {
                    enqueueEvents(d.events, d);
                }

                // время
                if (timeElement && d.minute !== undefined)
                    timeElement.textContent = `${d.minute}'`;

                updateStatistics(d);
                updateMomentum(d);   // ← вызывается ВСЕГДА
            }

            // 3) Пакет только с обновлением состояния
            else if (d.partial_update === undefined && d.events === undefined) {
                if (timeElement && d.minute !== undefined)
                    timeElement.textContent = `${d.minute}'`;
                updateStatistics(d);
                updateMomentum(d);
            }

            // 4) Контроль статуса матча
            if (d.status && d.status !== currentStatus) {
                currentStatus = d.status;
                if (['finished', 'cancelled', 'error'].includes(currentStatus)) {
                    showMessage(`Match ${currentStatus}. Live updates stopped.`, 'info');
                    socket.close();
                }
            }

        } catch (err) {
            console.error('WS processing error:', err, e.data);
        }
    };
});
