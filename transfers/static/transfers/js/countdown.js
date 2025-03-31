// Скрипт для обратного отсчета времени трансфера и автоматического завершения аукциона
document.addEventListener('DOMContentLoaded', function()  {
    // Находим все элементы с таймерами обратного отсчета
    const countdownTimers = document.querySelectorAll('.countdown-timer');
    
    // Для хранения текущего времени окончания каждого аукциона
    const expiresAtMap = new Map();
    // Для хранения интервалов обновления для каждого аукциона
    const intervals = new Map();
    // Был ли показан эффект продления времени для данного аукциона
    const extensionShown = new Map();
    
    // Функция для получения CSRF-токена из cookies
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
    
    // Для каждого таймера настраиваем обратный отсчет
    countdownTimers.forEach(function(timer) {
        // Изначальное время окончания аукциона
        let expiresAt = new Date(timer.dataset.expires);
        const listingId = timer.dataset.listingId;
        const hoursElement = timer.querySelector('.hours');
        const minutesElement = timer.querySelector('.minutes');
        const secondsElement = timer.querySelector('.seconds');
        
        // Сохраняем время окончания в карту
        expiresAtMap.set(listingId, expiresAt);
        extensionShown.set(listingId, false);
        
        // Функция обновления таймера
        function updateTimer() {
            const now = new Date();
            // Получаем актуальное время окончания из карты
            expiresAt = expiresAtMap.get(listingId);
            const diff = expiresAt - now;
            
            // Если время истекло
            if (diff <= 0) {
                hoursElement.textContent = '00';
                minutesElement.textContent = '00';
                secondsElement.textContent = '00';
                
                // Отправляем запрос на сервер для обработки истечения срока трансфера
                expireTransferListing(listingId);
                
                // Останавливаем таймер
                if (intervals.has(listingId)) {
                    clearInterval(intervals.get(listingId));
                    intervals.delete(listingId);
                }
                return;
            }
            
            // Рассчитываем оставшееся время
            const hours = Math.floor(diff / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);
            
            // Обновляем отображение
            hoursElement.textContent = hours.toString().padStart(2, '0');
            minutesElement.textContent = minutes.toString().padStart(2, '0');
            secondsElement.textContent = seconds.toString().padStart(2, '0');
            
            // Если до окончания осталось менее 30 секунд, добавляем визуальное оформление
            if (diff < 30000) {
                timer.classList.add('countdown-ending');
            } else {
                timer.classList.remove('countdown-ending');
                extensionShown.set(listingId, false); // Сбрасываем флаг для следующего продления
            }
            
            // Проверяем, было ли недавно продление аукциона
            checkForTimeExtension(listingId);
        }
        
        // Функция для проверки и отображения продления времени аукциона
        function checkForTimeExtension(listingId) {
            // Запрашиваем актуальную информацию о времени окончания аукциона
            fetch(`/transfers/api/listing-info/${listingId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const serverExpiresAt = new Date(data.expires_at);
                    const currentExpiresAt = expiresAtMap.get(listingId);
                    
                    // Если время на сервере отличается от нашего локального на более чем 2 секунды
                    if (Math.abs(serverExpiresAt - currentExpiresAt) > 2000) {
                        // Обновляем локальное время окончания
                        expiresAtMap.set(listingId, serverExpiresAt);
                        
                        // Если время было продлено и это продление еще не было показано
                        if (serverExpiresAt > currentExpiresAt && !extensionShown.get(listingId)) {
                            // Показываем визуальный эффект продления времени
                            timer.classList.add('time-extended');
                            setTimeout(() => {
                                timer.classList.remove('time-extended');
                            }, 3000);
                            
                            // Устанавливаем флаг, что продление было показано
                            extensionShown.set(listingId, true);
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error checking for time extension:', error);
            });
        }
        
        // Функция для отправки запроса на сервер при истечении срока
        function expireTransferListing(listingId) {
            fetch(`/transfers/api/expire-listing/${listingId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Если аукцион успешно завершен, обновляем страницу
                    window.location.reload();
                } else {
                    console.error('Failed to expire listing:', data.message);
                }
            })
            .catch(error => {
                console.error('Error expiring listing:', error);
            });
        }
        
        // Запускаем таймер и обновляем его каждую секунду
        updateTimer();
        const interval = setInterval(updateTimer, 1000);
        intervals.set(listingId, interval);
        
        // Периодически проверяем обновление времени (каждые 5 секунд)
        const updateCheckInterval = setInterval(() => {
            checkForTimeExtension(listingId);
        }, 5000);
    });
});
