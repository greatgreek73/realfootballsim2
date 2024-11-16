document.addEventListener('DOMContentLoaded', function() {
    // Инициализация календаря
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: calendarEvents,
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false,
            meridiem: false
        },
        eventClick: function(info) {
            if (info.event.url) {
                window.location.href = info.event.url;
                info.jsEvent.preventDefault();
            }
        },
        eventDidMount: function(info) {
            // Добавляем тултип с деталями матча
            const event = info.event;
            let tooltipContent = `${event.title}<br>`;
            if (event.extendedProps.status === 'finished') {
                tooltipContent += `Score: ${event.extendedProps.score}`;
            } else {
                tooltipContent += event.extendedProps.status;
            }
            
            new bootstrap.Tooltip(info.el, {
                title: tooltipContent,
                html: true,
                placement: 'top',
                customClass: 'match-tooltip'
            });
        }
    });

    calendar.render();
});

// Функция для обновления отображения времени
function updateMatchTimes(timezone) {
    document.querySelectorAll('.match-time').forEach(function(el) {
        const utcTime = moment.utc(el.dataset.utc);
        el.textContent = utcTime.tz(timezone).format('DD MMM HH:mm');
    });
    
    if (typeof calendar !== 'undefined') {
        calendar.setOption('timeZone', timezone);
        calendar.refetchEvents();
    }
}