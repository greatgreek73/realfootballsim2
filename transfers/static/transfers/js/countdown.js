// Скрипт для обратного отсчета времени трансфера и автоматического завершения аукциона
document.addEventListener('DOMContentLoaded', function()  {
    // Находим все элементы с таймерами обратного отсчета
    const countdownTimers = document.querySelectorAll('.countdown-timer');
    
    // Для каждого таймера настраиваем обратный отсчет
    countdownTimers.forEach(function(timer) {
        const expiresAt = new Date(timer.dataset.expires);
        const listingId = timer.dataset.listingId;
        const hoursElement = timer.querySelector('.hours');
        const minutesElement = timer.querySelector('.minutes');
        const secondsElement = timer.querySelector('.seconds');
        
        // Функция обновления таймера
        function updateTimer() {
            const now = new Date();
            const diff = expiresAt - now;
            
            // Если время истекло
            if (diff <= 0) {
                hoursElement.textContent = '00';
                minutesElement.textContent = '00';
                secondsElement.textContent = '00';
                
                // Отправляем запрос на сервер для обработки истечения срока трансфера
                expireTransferListing(listingId);
                
                // Останавливаем таймер
                clearInterval(interval);
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
        
        // Запускаем таймер и обновляем его каждую секунду
        updateTimer();
        const interval = setInterval(updateTimer, 1000);
    });
});
