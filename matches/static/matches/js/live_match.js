// matches/static/matches/js/live_match.js
// ----------------------------------------------------------------------------
// Лайв-страница матча: WebSocket-клиент, обработка статистики, моментума и т.д.
// ----------------------------------------------------------------------------

let matchId = null;            // устанавливается после DOMContentLoaded

// --- Утилита получения CSRF ---------------------------------------------------
function getCookie(name) {
    const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : null;
}

// --- Обработчик кнопки замены -------------------------------------------------
document.querySelector('#replace-player')?.addEventListener('click', () => {
    const select = document.getElementById('playerToReplaceSelect');
    if (!select?.value) {
        console.warn('No player selected for substitution');
        return;
    }
    fetch(`/matches/${matchId}/substitute/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ out_player_id: select.value }),
    })
        .then(r => r.json())
        .then(d => console.log('Substitution response', d))
        .catch(err => console.error('Substitution error', err));
});

// ------------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    //---------------------------------------------------------------------------
    // БАЗОВЫЕ DOM-ЭЛЕМЕНТЫ
    //---------------------------------------------------------------------------

    const matchInfoArea = document.getElementById('matchInfoArea');
    if (!matchInfoArea) return console.error('#matchInfoArea not found');

    matchId                        = matchInfoArea.dataset.matchId;
    const initialStatus            = matchInfoArea.dataset.matchStatus;
    let   currentStatus            = initialStatus;
    const isLive                   = initialStatus === 'in_progress';

    const timeEl                   = document.getElementById('matchTime');
    const homeScoreEl              = document.querySelector('.home-score');
    const awayScoreEl              = document.querySelector('.away-score');
    const eventsBox                = document.querySelector('#originalEvents .events-box');
    const statBox                  = document.querySelector('.stat-box');
    const homeMomIcon              = document.getElementById('homeMomentumIcon');
    const awayMomIcon              = document.getElementById('awayMomentumIcon');
    const homeMomVal               = document.getElementById('homeMomentumValue');
    const awayMomVal               = document.getElementById('awayMomentumValue');
    const injuryActionForm         = document.querySelector('#matchUserAction-inj');

    //---------------------------------------------------------------------------
    // Вспомогательные функции
    //---------------------------------------------------------------------------

    function setMomentum(iconEl, value, valEl) {
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
        valEl.textContent  = value;
    }

    function updateMomentum(d) {
        if (d.home_momentum !== undefined) setMomentum(homeMomIcon, d.home_momentum, homeMomVal);
        if (d.away_momentum !== undefined) setMomentum(awayMomIcon, d.away_momentum, awayMomVal);
    }

    function updateStats(d) {
        if (!statBox) return;
        statBox.querySelector('.stat-passes')     ?.textContent = d.st_passes      ?? '--';
        statBox.querySelector('.stat-shoots')     ?.textContent = d.st_shoots      ?? '--';
        statBox.querySelector('.stat-possessions')?.textContent = d.st_possessions ?? '--';
        statBox.querySelector('.stat-fouls')      ?.textContent = d.st_fouls       ?? '--';
        statBox.querySelector('.stat-injuries')   ?.textContent = d.st_injury      ?? '0';
    }

    function addEvent(evt) {
        if (!eventsBox) return;
        const key = `${evt.minute}-${evt.event_type}-${evt.description}`;
        window._evtSet = window._evtSet || new Set();
        if (window._evtSet.has(key)) return;
        window._evtSet.add(key);

        const div = document.createElement('div');
        div.className = 'list-group-item';
        div.innerHTML = `<strong>${evt.minute}'</strong> ${evt.description}`;
        eventsBox.prepend(div);
        while (eventsBox.children.length > 100)
            eventsBox.removeChild(eventsBox.lastChild);
    }

    //---------------------------------------------------------------------------
    // WebSocket
    //---------------------------------------------------------------------------

    if (!isLive) {
        console.log(`Match ${matchId} status ${initialStatus}. WebSocket not started.`);
        return;
    }

    const wsScheme = location.protocol === 'https:' ? 'wss' : 'ws';
    const socket   = new WebSocket(`${wsScheme}://${location.host}/ws/match/${matchId}/`);

    socket.onopen    = () => console.log('WS connected');
    socket.onerror   = e  => console.error('WS error:', e);
    socket.onclose   = e  => console.warn('WS closed', e.code);

    socket.onmessage = e => {
        let d;
        try {
            const m = JSON.parse(e.data);
            if (m.type !== 'match_update' || !m.data) return;
            d = m.data;
        } catch (err) {
            console.error('Bad WS JSON', err, e.data);
            return;
        }

        // ---------- первое «полное» сообщение ----------
        if (d.partial_update === undefined && Array.isArray(d.events)) {
            eventsBox.innerHTML = '';
            d.events.forEach(addEvent);
            if (timeEl && d.minute !== undefined) timeEl.textContent = `${d.minute}'`;
            updateStats(d);
            updateMomentum(d);
        }

        // ---------- любое partial-обновление ----------
        else if (d.partial_update === true || (d.partial_update === undefined && d.minute !== undefined)) {

            if (Array.isArray(d.events) && d.events.length) {
                const ev = d.events[0];
                addEvent(ev);
                if (ev.event_type === 'goal') {
                    if (d.home_score !== undefined) homeScoreEl.textContent = d.home_score;
                    if (d.away_score !== undefined) awayScoreEl.textContent = d.away_score;
                }
            }

            if (timeEl && d.minute !== undefined) timeEl.textContent = `${d.minute}'`;
            updateStats(d);
            updateMomentum(d);
        }

        // ---------- изменение статуса ----------
        if (d.status && d.status !== currentStatus) {
            currentStatus = d.status;
            if (['finished', 'cancelled', 'error'].includes(currentStatus)) {
                console.log(`Match ${matchId} ended (${currentStatus}).`);
                socket.close();
            }
        }
    };
});
