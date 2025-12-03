// static/js/main.js

document.addEventListener("DOMContentLoaded", function() {
    const token = localStorage.getItem('access_token');

    if (token) {
        // Пользователь залогинен
        document.getElementById('nav-login').classList.add('d-none');
        document.getElementById('nav-register').classList.add('d-none');
        
        document.getElementById('nav-dashboard').classList.remove('d-none');
        document.getElementById('nav-profile').classList.remove('d-none'); // <-- Добавили показ кнопки
        document.getElementById('nav-logout').classList.remove('d-none');
    } else {
        // Гость
        document.getElementById('nav-login').classList.remove('d-none');
        document.getElementById('nav-register').classList.remove('d-none');
        
        document.getElementById('nav-dashboard').classList.add('d-none');
        document.getElementById('nav-profile').classList.add('d-none'); // <-- Скрываем кнопку
        document.getElementById('nav-logout').classList.add('d-none');
    }
});


function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
}
