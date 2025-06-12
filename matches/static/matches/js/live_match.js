// matches/static/matches/js/live_match.js
// ----------------------------------------------------------------------------
// Лайв‑страница матча: WebSocket‑клиент, обработка статистики, моментума и т.д.
// ----------------------------------------------------------------------------

// --- Переменные верхнего уровня ------------------------------------------------
let matchId = null;            // устанавливается после DOMContentLoaded

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

    // Обновление HTML‑иконки и числа моментума
    function setMomentum(iconEl, value, valueEl) {
        if (!iconEl) return;
        iconEl.className = 'momentum-icon';

        let icon = '😐';
        if      (value >= 75)  { icon = '🌟'; iconEl.classList.add('momentum-unstoppable'); }
        else if (value >= 50)  { icon = '🔥'; iconEl.classList.add('momentum-hot'); }
        else if (value >= 25)  { icon = '💪'; iconEl.classList.add('momentum-positive'); }
        else if (value <= -75) { icon = '😱'; iconEl.classList.add('momentum-panic'); }
        else if (value <= -50) { icon = '💔'; iconEl.classList.add('momentum-demoralized'); }
        else if (value <= -25) { icon = '😰'; iconEl.classList.add('momentum-nervous'); }
        else                   { icon = '😐'; iconEl.classList.add('momentum-neutral'); }

        iconEl.textContent = icon;
        if (valueEl) valueEl.textContent = value;
    }

    function updateMomentum(data) {
        if (data.home_momentum !== undefined)
            setMomentum(homeMomentumIcon, data.home_momentum, homeMomentumValue);
        if (data.away_momentum !== undefined)
            setMomentum(awayMomentumIcon, data.away_momentum, awayMomentumValue);
    }

    // --- Обновление статистики -------------------------------------------------
    function updateStatistics(data) {
        if (!statBox) return;

        const passesSpan      = statBox.querySelector('.stat-passes');
        const shootsSpan      = statBox.querySelector('.stat-shoots');
        const possessionsSpan = statBox.querySelector('.stat-possessions');
        const foulsSpan       = statBox.querySelector('.stat-fouls');
        const injuriesSpan    = statBox.querySelector('.stat-injuries');
        const injCounterEl    = document.getElementById('inj');

        if (passesSpan      && data.st_passes      !== undefined) passesSpan.textContent      = data.st_passes;
        if (shootsSpan      && data.st_shoots      !== undefined) shootsSpan.textContent      = data.st_shoots;
        if (possessionsSpan && data.st_possessions !== undefined) possessionsSpan.textContent = data.st_possessions;
        if (foulsSpan       && data.st_fouls       !== undefined) foulsSpan.textContent       = data.st_fouls;
        if (injuriesSpan    && data.st_injury      !== undefined) injuriesSpan.textContent    = data.st_injury;
        if (injCounterEl    && data.st_injury      !== undefined) injCounterEl.textContent    = data.st_injury;

        // всплывающая форма реагирования на травму
        if (injCounterEl && injuryActionForm && data.st_injury !== undefined) {
            const oldVal = parseInt(injCounterEl.innerText) || 0;
            if (oldVal !== data.st_injury) {
                injuryActionForm.style.display = 'block';
                injuryActionForm.classList.add('display-action');
            }
        }
    }

    // --- Добавление события в лог ---------------------------------------------
    function addEventToList(evt) {
        if (!eventsBox) return;

        const sig = `${evt.minute}-${evt.event_type}-${evt.description}`;
        window.processedEvents = window.processedEvents || new Set();
        if (window.processedEvents.has(sig)) return;
        window.processedEvents.add(sig);

        const div = document.createElement('div');
        div.className = 'list-group-item new-event';

        const icons = {
            goal: ' ⚽ ', counterattack: ' ⚡ ', interception: ' 🔄 ',
            shot_miss: ' ❌ ', pass: ' ➡ ', foul: ' ⚠ ',
            injury_concern: ' ✚ ', yellow_card: ' 🟨 ', red_card: ' 🟥 ',
            substitution: ' ⇆ ', match_start: ' ▶ ', match_end: ' ⏹ ',
            match_paused: ' ⏸ ', info: ' ⓘ '
        };
        const icon = icons[evt.event_type] || ' M ';

        let playerInfo = evt.player_name ? ` (${evt.player_name})` : '';
        if (evt.related_player_name)
            playerInfo += ` -> ${evt.related_player_name}`;

        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${evt.minute}'</strong>
                    <span class="event-icon">${icon}</span>
                    ${evt.description}
                    <small class="text-muted">${playerInfo}</small>
                </div>
            </div>`;

        eventsBox.prepend(div);

        // ограничиваем лог 100 строками
        while (eventsBox.children.length > 100)
            eventsBox.removeChild(eventsBox.lastChild);

        // анимация
        requestAnimationFrame(() =>
            requestAnimationFrame(() => div.classList.add('new-event-visible')));
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

    // ----------------------- ИСХОДНОЕ ИСПРАВЛЕННОЕ МЕСТО -----------------------
    socket.onmessage = e => {
        try {
            const msg  = JSON.parse(e.data);
            if (msg.type !== 'match_update' || !msg.data) return;
            const d = msg.data;
            console.log('WS data:', d);

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
                    const ev = d.events[0];
                    addEventToList(ev);

                    // обновляем счёт только при голе
                    if (ev.event_type === 'goal') {
                        if (d.home_score !== undefined) homeScoreElement.textContent = d.home_score;
                        if (d.away_score !== undefined) awayScoreElement.textContent = d.away_score;
                    }
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
