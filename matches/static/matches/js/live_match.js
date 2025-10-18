// matches/static/matches/js/live_match.js
// ----------------------------------------------------------------------------
// ╨Ы╨░╨╣╨▓тАС╤Б╤В╤А╨░╨╜╨╕╤Ж╨░ ╨╝╨░╤В╤З╨░: WebSocketтАС╨║╨╗╨╕╨╡╨╜╤В, ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╨░ ╤Б╤В╨░╤В╨╕╤Б╤В╨╕╨║╨╕, ╨╝╨╛╨╝╨╡╨╜╤В╤Г╨╝╨░ ╨╕ ╤В.╨┤.
// ----------------------------------------------------------------------------

// --- ╨Я╨╡╤А╨╡╨╝╨╡╨╜╨╜╤Л╨╡ ╨▓╨╡╤А╤Е╨╜╨╡╨│╨╛ ╤Г╤А╨╛╨▓╨╜╤П ------------------------------------------------
let matchId = null;            // ╤Г╤Б╤В╨░╨╜╨░╨▓╨╗╨╕╨▓╨░╨╡╤В╤Б╤П ╨┐╨╛╤Б╨╗╨╡ DOMContentLoaded
const EVENT_DELAY_MS = 1000;
const minutesMap = new Map();
const seenEventIds = new Set();
const eventsBox = document.querySelector('.events-box');

// --- ╨г╤В╨╕╨╗╨╕╤В╨░ ╨┐╨╛╨╗╤Г╤З╨╡╨╜╨╕╨╡ CSRF ----------------------------------------------------
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

// --- ╨Ю╨▒╤А╨░╨▒╨╛╤В╤З╨╕╨║ ╨║╨╜╨╛╨┐╨║╨╕ ╨╖╨░╨╝╨╡╨╜╤Л --------------------------------------------------
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

// --- ╨Ю╤Б╨╜╨╛╨▓╨╜╨░╤П ╨╗╨╛╨│╨╕╨║╨░ -----------------------------------------------------------
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

    // ╨Ф╨╛╨▒╨░╨▓╨╗╨╡╨╜╨╛: ID ╨║╨╛╨╝╨░╨╜╨┤ ╨┤╨╗╤П ╨╝╨░╨┐╨┐╨╕╨╜╨│╨░ possessing_team
    const homeTeamId = parseInt(matchInfoArea.dataset.homeTeamId);
    const awayTeamId = parseInt(matchInfoArea.dataset.awayTeamId);

    // DOMтАС╤Н╨╗╨╡╨╝╨╡╨╜╤В╤Л, ╨╕╤Б╨┐╨╛╨╗╤М╨╖╤Г╨╡╨╝╤Л╨╡ ╨┐╨╛╨▓╤В╨╛╤А╨╜╨╛
    const timeElement        = document.getElementById('matchTime');
    const homeScoreElement   = document.querySelector('.home-score');
    const awayScoreElement   = document.querySelector('.away-score');
    const eventsContainer    = document.getElementById('originalEvents');
    const statBox            = document.querySelector('.stat-box');
    const homeMomentumIcon   = document.getElementById('homeMomentumIcon');
    const awayMomentumIcon   = document.getElementById('awayMomentumIcon');
    const homeMomentumValue  = document.getElementById('homeMomentumValue');
    const awayMomentumValue  = document.getElementById('awayMomentumValue');
    const injuryActionForm   = document.querySelector('#matchUserAction-inj');
    const nextMinuteBtn      = document.getElementById('nextMinuteBtn');
    const pitchEl            = document.getElementById('pitch');

    // --- ╨Ч╨░╤Й╨╕╤В╨╜╤Л╨╡ ╨┐╤А╨╛╨▓╨╡╤А╨║╨╕ ╨╜╨░ ╨╜╨░╨╗╨╕╤З╨╕╨╡ ╨║╨╗╤О╤З╨╡╨▓╤Л╤Е ╤Г╨╖╨╗╨╛╨▓ --------------------------
    if (!timeElement)      console.error('Element #matchTime not found!');
    if (!homeScoreElement) console.error('Element .home-score not found!');
    if (!awayScoreElement) console.error('Element .away-score not found!');
    if (!eventsBox)        console.error('Element .events-box not found!');
    if (!statBox)          console.error('Element .stat-box not found!');

    //---------------------------------------------------------------------------
    // ╨Т╨б╨Я╨Ю╨Ь╨Ю╨У╨Р╨в╨Х╨Ы╨м╨Э╨л╨Х ╨д╨г╨Э╨Ъ╨ж╨Ш╨Ш
    //---------------------------------------------------------------------------

    // ╨Я╨╛╨║╨░╨╖ ╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╨╣ ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤О (╤Г╨┐╤А╨╛╤Й╤С╨╜╨╜╨╛╨╡, ╨▓╤Л╨▓╨╛╨┤╨╕╤В ╨▓ ╨║╨╛╨╜╤Б╨╛╨╗╤М)
    function showMessage(text, type = 'info') {
        console.log(`MESSAGE (${type}): ${text}`);
    }

    // ╨Ь╨░╨┐╨┐╨╕╨╜╨│ ╨░╨▒╤Б╤В╤А╨░╨║╤В╨╜╤Л╤Е ╨╖╨╛╨╜ ╨╜╨░ ╤Д╨╕╨╖╨╕╤З╨╡╤Б╨║╨╕╨╡ (╤Б ╨╖╨╡╤А╨║╨░╨╗╨╕╤А╨╛╨▓╨░╨╜╨╕╨╡╨╝)
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
        'MID-L': 'right-mid-top',
        'MID-C': 'right-mid-middle',
        'MID-R': 'right-mid-bottom',
        'AM-L': 'left-mid-top',
        'AM-C': 'left-mid-middle',
        'AM-R': 'left-mid-bottom',
        'FWD-L': 'left-def-top',
        'FWD-C': 'left-def-middle',
        'FWD-R': 'left-def-bottom',
    };

    // ╨д╤Г╨╜╨║╤Ж╨╕╤П ╨┤╨╗╤П ╨┐╨╛╨╗╤Г╤З╨╡╨╜╨╕╤П ╤Д╨╕╨╖╨╕╤З╨╡╤Б╨║╨╛╨╣ ╨╖╨╛╨╜╤Л
    function getPhysicalZone(abstractZone, possessingTeamId) {
        if (!abstractZone || possessingTeamId === undefined) return null;
        const isHome = possessingTeamId === homeTeamId;
        const map = isHome ? homeZoneMap : awayZoneMap;
        const key = abstractZone.toUpperCase();
        return map[key] || null;
    }

    // ╨Т╤Л╨┤╨╡╨╗╨╡╨╜╨╕╨╡ ╨╖╨╛╨╜╤Л (╤В╨╡╨┐╨╡╤А╤М ╤А╨░╨▒╨╛╤В╨░╨╡╤В ╤Б ╤Д╨╕╨╖╨╕╤З╨╡╤Б╨║╨╛╨╣ ╨╖╨╛╨╜╨╛╨╣)
    function highlight(physicalZone) {
        if (!pitchEl || !physicalZone) return;
        document.querySelectorAll('#pitch .zone').forEach(z => {
            z.classList.toggle('active', z.dataset.zone === physicalZone);
        });
    }

    // ╨Я╨╛╨║╨░╨╖ ╨╕╨║╨╛╨╜╨║╨╕ ╤Б╨╛╨▒╤Л╤В╨╕╤П ╨▓ ╨╖╨╛╨╜╨╡ (╤В╨╡╨┐╨╡╤А╤М ╤Б ╤Д╨╕╨╖╨╕╤З╨╡╤Б╨║╨╛╨╣ ╨╖╨╛╨╜╨╛╨╣)
    function showIcon(physicalZone, type) {
        if (!pitchEl || !physicalZone) return;
        const icons = {
            goal: 'тЪ╜', shot: 'тЪ╜', shot_miss: 'тЭМ', pass: 'тЮбя╕П',
            interception: 'ЁЯФД', foul: 'тЪая╕П', counterattack: 'тЪб', dribble: 'тЖХя╕П'
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
        // ╨Ю╨▒╨╜╨╛╨▓╨╗╤П╨╡╨╝ ╨╖╨╜╨░╤З╨╡╨╜╨╕╨╡ (╨╡╤Б╨╗╨╕ ╤Н╨╗╨╡╨╝╨╡╨╜╤В ╨╡╤Б╤В╤М)
        if (valueEl) valueEl.textContent = value;

        // ╨Ю╨▒╨╜╨╛╨▓╨╗╤П╨╡╨╝ ╨╕╨║╨╛╨╜╨║╤Г ╨▓ ╨╖╨░╨▓╨╕╤Б╨╕╨╝╨╛╤Б╤В╨╕ ╨╛╤В ╨┤╨╕╨░╨┐╨░╨╖╨╛╨╜╨░
        if (!iconEl) return;

        iconEl.classList.remove(
            'momentum-neutral', 'momentum-positive', 'momentum-hot',
            'momentum-unstoppable', 'momentum-nervous', 'momentum-demoralized', 'momentum-panic'
        );

        if (value >= -10 && value <= 10) {
            iconEl.classList.add('momentum-neutral');
            iconEl.textContent = 'ЁЯШР';
        } else if (value > 10 && value <= 30) {
            iconEl.classList.add('momentum-positive');
            iconEl.textContent = 'ЁЯШК';
        } else if (value > 30 && value <= 60) {
            iconEl.classList.add('momentum-hot');
            iconEl.textContent = 'ЁЯФе';
        } else if (value > 60) {
            iconEl.classList.add('momentum-unstoppable');
            iconEl.textContent = 'ЁЯЪА';
        } else if (value < -10 && value >= -30) {
            iconEl.classList.add('momentum-nervous');
            iconEl.textContent = 'ЁЯШЯ';
        } else if (value < -30 && value >= -60) {
            iconEl.classList.add('momentum-demoralized');
            iconEl.textContent = 'ЁЯШв';
        } else if (value < -60) {
            iconEl.classList.add('momentum-panic');
            iconEl.textContent = 'ЁЯШ▒';
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

        // ╨Ю╨▒╨╜╨╛╨▓╨╗╤П╨╡╨╝ ╤Б╤В╨░╤В╨╕╤Б╤В╨╕╨║╤Г ╨┐╨╛ ╨║╨╗╨░╤Б╤Б╨░╨╝
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

        // ╨б╨┐╨╡╤Ж╨╕╨░╨╗╤М╨╜╨░╤П ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╨░ ╨┤╨╗╤П ╤В╤А╨░╨▓╨╝
        if (data.st_injury !== undefined && injuryActionForm) {
            const injuryBadge = document.getElementById('inj');
            if (injuryBadge) injuryBadge.textContent = data.st_injury;
            
            // ╨Я╨╛╨║╨░╨╖╤Л╨▓╨░╨╡╨╝ ╤Д╨╛╤А╨╝╤Г ╨╖╨░╨╝╨╡╨╜╤Л ╤В╨╛╨╗╤М╨║╨╛ ╨┤╨╗╤П ╨║╨╛╨╝╨░╨╜╨┤╤Л ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤П
            const userClubId = parseInt(document.querySelector('[data-user-club-id]')?.dataset.userClubId || '0');
            if (data.st_injury > 0 && (userClubId === homeTeamId || userClubId === awayTeamId)) {
                injuryActionForm.style.display = 'block';
            }
        }
    }

    const eventIconMap = {
    goal: '⚽',
    counterattack: '⚡',
    interception: '🔄',
    shot_miss: '❌',
    pass: '➡️',
    foul: '⚠️',
    injury_concern: '✚',
};

let currentOpenMinuteKey = null;

function eventKey(evt) {
    if (!evt) return null;
    if (evt.id !== undefined && evt.id !== null) {
        return String(evt.id);
    }
    const minute = evt.minute ?? '';
    const type = evt.event_type || '';
    const description = evt.description || '';
    const player = evt.player_name || '';
    const related = evt.related_player_name || '';
    return `${minute}|${type}|${description}|${player}|${related}`;
}

function getComparableMinute(minute) {
    if (minute === null || minute === undefined) return -Infinity;
    const str = String(minute);
    if (str.includes('+')) {
        const [base, extra] = str.split('+');
        const baseValue = parseInt(base, 10) || 0;
        const extraValue = parseInt(extra, 10) || 0;
        return baseValue + extraValue / 100;
    }
    const numeric = parseInt(str, 10);
    return Number.isNaN(numeric) ? -Infinity : numeric;
}

function currentScoreText() {
    const home = homeScoreElement ? homeScoreElement.textContent.trim() : '';
    const away = awayScoreElement ? awayScoreElement.textContent.trim() : '';
    return `${home}-${away}`;
}

function scoreFromPayload(data) {
    if (!data || data.home_score === undefined || data.away_score === undefined) {
        return null;
    }
    if (data.home_score === null || data.away_score === null) {
        return null;
    }
    return `${data.home_score}-${data.away_score}`;
}

function collapseCard(card) {
    if (!card) return;
    const body = card.querySelector('.minute-body');
    if (body) body.style.display = 'none';
    card.classList.add('collapsed');
    card.classList.remove('expanded');
}

function expandCard(card) {
    if (!card) return;
    const body = card.querySelector('.minute-body');
    if (body) body.style.display = '';
    card.classList.add('expanded');
    card.classList.remove('collapsed');
}

function openMinuteCard(minuteKey) {
    minutesMap.forEach((card, key) => {
        if (key === minuteKey) {
            expandCard(card);
        } else {
            collapseCard(card);
        }
    });
    currentOpenMinuteKey = minuteKey;
}

function toggleMinuteCard(minuteKey) {
    const card = minutesMap.get(minuteKey);
    if (!card) return;
    const isCollapsed = card.classList.contains('collapsed');
    if (isCollapsed) {
        openMinuteCard(minuteKey);
    } else {
        collapseCard(card);
        currentOpenMinuteKey = null;
    }
}

function collapseOldMinutes(minute) {
    if (minute === undefined || minute === null) return;
    openMinuteCard(String(minute));
}

function ensureMinuteCard(minute, scoreText) {
    if (!eventsBox) return null;
    const minuteKey = minute !== undefined && minute !== null ? String(minute) : '0';
    let card = minutesMap.get(minuteKey);
    const displayScore = scoreText ?? currentScoreText();

    if (!card) {
        card = document.createElement('div');
        card.className = 'minute-card list-group mb-3 shadow-sm border border-light rounded';
        card.dataset.minute = minuteKey;

        const header = document.createElement('div');
        header.className = 'minute-header d-flex justify-content-between align-items-center';

        const label = document.createElement('strong');
        label.className = 'minute-label';
        label.textContent = minuteKey + "'";

        const scoreEl = document.createElement('span');
        scoreEl.className = 'minute-score';
        scoreEl.textContent = displayScore;

        header.append(label, scoreEl);
        header.addEventListener('click', () => toggleMinuteCard(minuteKey));

        const body = document.createElement('div');
        body.className = 'minute-body list-group';

        card.append(header, body);
        const existingCards = Array.from(eventsBox.querySelectorAll('.minute-card'));
        const newValue = getComparableMinute(minuteKey);
        let inserted = false;
        for (const existing of existingCards) {
            const existingValue = getComparableMinute(existing.dataset.minute);
            if (newValue > existingValue) {
                eventsBox.insertBefore(card, existing);
                inserted = true;
                break;
            }
        }
        if (!inserted) {
            eventsBox.appendChild(card);
        }
        minutesMap.set(minuteKey, card);
        collapseCard(card);
    } else if (displayScore && scoreText !== undefined && scoreText !== null) {
        const scoreEl = card.querySelector('.minute-score');
        if (scoreEl) scoreEl.textContent = displayScore;
    }

    return card;
}

function appendEventToMinute(minute, evt, scoreText) {
    const key = eventKey(evt);
    if (key && seenEventIds.has(key)) {
        return false;
    }
    const card = ensureMinuteCard(minute, scoreText);
    if (!card) return false;
    const body = card.querySelector('.minute-body');
    if (!body) return false;

    if (key) seenEventIds.add(key);

    const item = document.createElement('div');
    item.className = 'list-group-item event-row';

    const wrapper = document.createElement('div');
    wrapper.className = 'd-flex align-items-start';

    const minuteEl = document.createElement('div');
    minuteEl.className = 'flex-shrink-0 me-2 text-muted fw-semibold';
    const minuteLabel = evt.minute !== undefined && evt.minute !== null ? String(evt.minute) : '';
    minuteEl.textContent = minuteLabel
        ? (/\d$/.test(minuteLabel) ? `${minuteLabel}'` : minuteLabel)
        : '';

    const content = document.createElement('div');
    content.className = 'flex-grow-1';

    const row = document.createElement('div');
    row.className = 'd-flex align-items-center mb-1';

    const iconEl = document.createElement('span');
    iconEl.className = 'event-icon me-2';
    iconEl.textContent = eventIconMap[evt.event_type] || 'M';

    const descEl = document.createElement('span');
    descEl.className = 'event-description';
    descEl.textContent = evt.description || '';

    row.append(iconEl, descEl);
    content.append(row);

    if (evt.player_name) {
        const playersEl = document.createElement('div');
        playersEl.className = 'text-muted small';
        playersEl.textContent = '(' + evt.player_name + (evt.related_player_name ? ' → ' + evt.related_player_name : '') + ')';
        content.append(playersEl);
    }

    if (evt.personality_reason) {
        const personalityEl = document.createElement('div');
        personalityEl.className = 'personality-reason mt-1';
        const small = document.createElement('small');
        small.className = 'text-secondary fst-italic';
        small.textContent = '(' + evt.personality_reason + ')';
        personalityEl.append(small);
        content.append(personalityEl);
    }

    wrapper.append(minuteEl, content);
    item.append(wrapper);
    body.appendChild(item);
    return true;
}
function normalizeEventPayload(raw) {
    if (!raw) return null;
    return {
        id: raw.id ?? null,
        minute: raw.minute,
        event_type: raw.event_type || raw.type || null,
        description: raw.description,
        personality_reason: raw.personality_reason,
        player_name: raw.player_name || (raw.player && raw.player.name) || null,
        related_player_name: raw.related_player_name || (raw.related_player && raw.related_player.name) || null,
    };
}
function renderFullEventSnapshot(events, payloadState) {
    if (!eventsBox) return;
    eventsBox.innerHTML = '';
    minutesMap.clear();
    seenEventIds.clear();
    currentOpenMinuteKey = null;

    if (!Array.isArray(events) || events.length === 0) {
        eventsBox.innerHTML = '<div class="text-muted small py-3 text-center">Waiting for match events...</div>';
        return;
    }

    const grouped = new Map();
    events.forEach(raw => {
        const evt = normalizeEventPayload(raw);
        if (!evt) return;
        const key = evt.minute !== undefined && evt.minute !== null ? String(evt.minute) : '0';
        if (!grouped.has(key)) grouped.set(key, []);
        grouped.get(key).push(evt);
    });

    const sortedKeys = Array.from(grouped.keys()).sort((a, b) => getComparableMinute(b) - getComparableMinute(a));
    const scoreHint = scoreFromPayload(payloadState) || currentScoreText();

    sortedKeys.forEach(minuteKey => {
        ensureMinuteCard(minuteKey, scoreHint);
        grouped.get(minuteKey).forEach(evt => appendEventToMinute(minuteKey, evt, scoreHint));
    });

    if (sortedKeys.length > 0) {
        collapseOldMinutes(sortedKeys[0]);
    }
}




    function addEventToList(evt, payload) {
        if (!eventsBox || !evt) return;
        const scoreHint = scoreFromPayload(payload) || currentScoreText();
        const appended = appendEventToMinute(evt.minute, evt, scoreHint);
        if (appended) {
            collapseOldMinutes(evt.minute);
        }
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
        addEventToList(item.event, item.data);
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
            const minuteKey = item.event.minute !== undefined && item.event.minute !== null ? String(item.event.minute) : null;
            if (minuteKey) {
                const card = minutesMap.get(minuteKey);
                const updated = scoreFromPayload(item.data) || currentScoreText();
                if (card) {
                    const scoreEl = card.querySelector('.minute-score');
                    if (scoreEl && updated) scoreEl.textContent = updated;
                }
            }
        }
        setTimeout(processQueue, EVENT_DELAY_MS);
    }

function enqueueEvents(events, data) {
        if (!Array.isArray(events)) return;
        events.forEach(ev => {
            const normalized = normalizeEventPayload(ev);
            if (normalized) {
                eventQueue.push({ event: normalized, data: data });
            }
        });
        if (!processingQueue) processQueue();
    }



    // --- WebSocket -------------------------------------------------------------
    if (!isLive) {
        console.log(`Match ${matchId} is not live (${initialStatus}), WS disabled.`);
        fetch(`/api/matches/${matchId}/events/`, { credentials: 'include' })
            .then(resp => resp.ok ? resp.json() : null)
            .then(payload => {
                const events = Array.isArray(payload?.events) ? payload.events : [];
                renderFullEventSnapshot(events, payload);
                if (!Array.isArray(payload?.events) || payload.events.length === 0) {
                    minutesMap.clear();
                }
            })
            .catch(err => {
                console.error('Failed to load match events:', err);
            });
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
            
            // DEBUG: ╨Ф╨╡╤В╨░╨╗╤М╨╜╨░╤П ╨┐╤А╨╛╨▓╨╡╤А╨║╨░ ╤Б╨╛╨▒╤Л╤В╨╕╨╣
            if (d.events && Array.isArray(d.events)) {
                console.log('=== DEBUG: WebSocket Events ===');
                console.log('Number of events:', d.events.length);
                d.events.forEach((evt, idx) => {
                    console.log(`Event ${idx}:`, evt);
                    if (evt.personality_reason) {
                        console.log(`Event ${idx} has personality_reason:`, evt.personality_reason);
                    }
                });
                console.log('==============================');
            }

            // ╨Ф╨╛╨▒╨░╨▓╨╗╨╡╨╜╨╛: ╨▓╤Л╨┤╨╡╨╗╨╡╨╜╨╕╨╡ ╨╖╨╛╨╜╤Л ╨┐╤А╨╕ ╨╗╤О╨▒╨╛╨╝ ╨╛╨▒╨╜╨╛╨▓╨╗╨╡╨╜╨╕╨╕ (╨╡╤Б╨╗╨╕ ╨╡╤Б╤В╤М current_zone ╨╕ possessing_team_id)
            if (d.current_zone && d.possessing_team_id !== undefined) {
                const physical = getPhysicalZone(d.current_zone, d.possessing_team_id);
                if (physical) highlight(physical);
            }

            // 1) ╨Я╨╡╤А╨▓╨╛╨╡ ╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╨╡: ╨┐╨╛╨╗╨╜╤Л╨╣ ╤Б╤В╨╡╨╣╤В + ╨╕╤Б╤В╨╛╤А╨╕╤П
            if (d.partial_update === undefined && Array.isArray(d.events)) {
                renderFullEventSnapshot(d.events, d);
                if (timeElement && d.minute !== undefined)
                    timeElement.textContent = `${d.minute}'`;
                updateStatistics(d);
                updateMomentum(d);
            }

            // 2) ╨Ы╤О╨▒╨╛╨╡ ╨з╨Р╨б╨в╨Ш╨з╨Э╨Ю╨Х ╨╛╨▒╨╜╨╛╨▓╨╗╨╡╨╜╨╕╨╡ (╤Б ╤Б╨╛╨▒╤Л╤В╨╕╨╡╨╝ ╨Ш╨Ы╨Ш ╨▒╨╡╨╖ ╨╜╨╡╨│╨╛)
            else if (d.partial_update === true) {

                // ╨╡╤Б╨╗╨╕ ╤Б╨╛╨▒╤Л╤В╨╕╨╡ ╨╡╤Б╤В╤М тАФ ╨▓╤Л╨▓╨╛╨┤╨╕╨╝
                if (d.events && Array.isArray(d.events) && d.events.length > 0) {
                    enqueueEvents(d.events, d);
                }

                if (d.minute !== undefined) {
                    ensureMinuteCard(d.minute, scoreFromPayload(d) || currentScoreText());
                    collapseOldMinutes(d.minute);
                }

                if (timeElement && d.minute !== undefined)
                    timeElement.textContent = `${d.minute}'`;

                updateStatistics(d);
                updateMomentum(d);   // тЖР ╨▓╤Л╨╖╤Л╨▓╨░╨╡╤В╤Б╤П ╨Т╨б╨Х╨У╨Ф╨Р
            }

            // 3) ╨Я╨░╨║╨╡╤В ╤В╨╛╨╗╤М╨║╨╛ ╤Б ╨╛╨▒╨╜╨╛╨▓╨╗╨╡╨╜╨╕╨╡╨╝ ╤Б╨╛╤Б╤В╨╛╤П╨╜╨╕╤П
            else if (d.partial_update === undefined && d.events === undefined) {
                if (timeElement && d.minute !== undefined)
                    timeElement.textContent = `${d.minute}'`;
                updateStatistics(d);
                updateMomentum(d);
            }

            // 4) ╨Ъ╨╛╨╜╤В╤А╨╛╨╗╤М ╤Б╤В╨░╤В╤Г╤Б╨░ ╨╝╨░╤В╤З╨░
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
