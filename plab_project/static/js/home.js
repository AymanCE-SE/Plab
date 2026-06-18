document.addEventListener("DOMContentLoaded", function() {
    const heartButtons = document.querySelectorAll(".heart-toggle-btn");
    
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
    const csrftoken = getCookie('csrftoken');

    heartButtons.forEach(function(button) {
        button.addEventListener("click", function(e) {
            e.preventDefault();
            
            const btn = this;
            const url = btn.getAttribute("data-url");
            const textHeart = btn.getAttribute("data-text-heart");
            const textUnheart = btn.getAttribute("data-text-unheart");
            
            const parentContainer = btn.closest(".d-flex");
            const btnTextSpan = parentContainer.querySelector(".heart-btn-text");
            const countDisplay = parentContainer.querySelector(".heart-count-display");
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    countDisplay.innerText = data.total_hearts;
                    
                    if (data.has_hearted) {
                        btnTextSpan.innerText = textUnheart;
                        btn.classList.remove('btn-light');
                        btn.classList.add('btn-primary', 'text-white'); // تغيير ستايل الزرار كإشارة بصرية
                    } else {
                        btnTextSpan.innerText = textHeart;
                        btn.classList.remove('btn-primary', 'text-white');
                        btn.classList.add('btn-light');
                    }
                } else {
                    console.error("Server Error:", data.message);
                }
            })
            .catch(error => console.error('Fetch Error:', error));
        });
    });
});
