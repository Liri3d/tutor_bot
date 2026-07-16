// web/script.js

const API_BASE = '/api';
let currentTutorId = null;

// ========== ИНИЦИАЛИЗАЦИЯ ==========

document.addEventListener('DOMContentLoaded', async () => {
    // Проверяем сохраненного пользователя
    const savedUser = localStorage.getItem('tutor_user');
    
    if (savedUser) {
        try {
            const user = JSON.parse(savedUser);
            
            // Проверяем, существует ли пользователь в БД
            const response = await fetch(`${API_BASE}/tutors/${user.telegram_id}/check`);
            const data = await response.json();
            
            if (data.exists) {
                // Восстанавливаем сессию
                currentTutorId = user.telegram_id;
                document.getElementById('auth-section').style.display = 'none';
                document.getElementById('dashboard-section').style.display = 'block';
                await loadDashboard(user.telegram_id);
                return;
            } else {
                // Пользователь удалён из БД
                localStorage.removeItem('tutor_user');
            }
        } catch (e) {
            console.error('Ошибка восстановления сессии:', e);
            localStorage.removeItem('tutor_user');
        }
    }
    
    
    const loginBtn = document.getElementById('login-btn');
    const createInviteBtn = document.getElementById('create-invite-btn');

    loginBtn.addEventListener('click', handleLogin);
    createInviteBtn.addEventListener('click', handleCreateInvite);

    // Enter для входа
    document.getElementById('telegram-id').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleLogin();
    });

    // Enter для создания приглашения
    document.getElementById('student-name').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleCreateInvite();
    });
});

// ========== АУТЕНТИФИКАЦИЯ ==========

async function handleLogin() {
    const input = document.getElementById('telegram-id');
    const telegramId = parseInt(input.value.trim());

    if (!telegramId || isNaN(telegramId)) {
        alert('Пожалуйста, введите корректный Telegram ID');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/tutors/${telegramId}/check`);
        const data = await response.json();

        if (!data.exists) {
            alert('Репетитор с таким Telegram ID не найден в системе.\n\nСначала зарегистрируйтесь в боте: @tutortesting_bot');
            return;
        }

        // Сохраняем пользователя
        const userData = {
            telegram_id: telegramId,
            name: data.name,
            students_count: data.students_count
        };
        localStorage.setItem('tutor_user', JSON.stringify(userData));

        currentTutorId = telegramId;
        document.getElementById('auth-section').style.display = 'none';
        document.getElementById('dashboard-section').style.display = 'block';

        await loadDashboard(telegramId);

    } catch (error) {
        console.error('Ошибка входа:', error);
        alert('Ошибка подключения к серверу. Попробуйте позже.');
    }
}

// ========== ЗАГРУЗКА ДАННЫХ ==========

async function loadDashboard(tutorId) {
    await Promise.all([
        loadStats(tutorId),
        loadStudents(tutorId),
        loadInvites(tutorId)
    ]);
}

async function loadStats(tutorId) {
    try {
        const response = await fetch(`${API_BASE}/tutors/${tutorId}/stats`);
        const stats = await response.json();

        document.getElementById('total-students').textContent = stats.total_students;
        document.getElementById('active-students').textContent = stats.active_students;
        document.getElementById('lessons-week').textContent = stats.lessons_this_week;

    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

async function loadStudents(tutorId) {
    const container = document.getElementById('students-list');

    try {
        const response = await fetch(`${API_BASE}/tutors/${tutorId}/students`);
        const students = await response.json();

        if (!students || students.length === 0) {
            container.innerHTML = '<p class="loading">У вас пока нет учеников</p>';
            return;
        }

        container.innerHTML = students.map(student => `
            <div class="student-item">
                <div>
                    <span class="student-name">${student.first_name}</span>
                    ${student.username ? `<span class="student-username">(@${student.username})</span>` : ''}
                </div>
                <span style="font-size: 13px; color: #a0aec0;">
                    ${new Date(student.registered_at).toLocaleDateString('ru-RU')}
                </span>
            </div>
        `).join('');

    } catch (error) {
        console.error('Ошибка загрузки учеников:', error);
        container.innerHTML = '<p class="error">Ошибка загрузки списка учеников</p>';
    }
}

async function loadInvites(tutorId) {
    const container = document.getElementById('invites-list');

    try {
        const response = await fetch(`${API_BASE}/tutors/${tutorId}/invites`);
        const invites = await response.json();

        if (!invites || invites.length === 0) {
            container.innerHTML = '<p class="loading">Нет активных приглашений</p>';
            return;
        }

        container.innerHTML = invites.map(invite => `
            <div class="invite-item">
                <div>
                    <span class="student-name">${invite.student_name}</span>
                    <span class="invite-code">${invite.code}</span>
                </div>
                <span class="invite-expires">
                    до ${new Date(invite.expires_at).toLocaleDateString('ru-RU')}
                </span>
            </div>
        `).join('');

    } catch (error) {
        console.error('Ошибка загрузки приглашений:', error);
        container.innerHTML = '<p class="error">Ошибка загрузки приглашений</p>';
    }
}



function handleTelegramAuth() {
    // Проверяем, есть ли параметр tgAuthResult в URL
    const urlParams = new URLSearchParams(window.location.search);
    const authResult = urlParams.get('tgAuthResult');
    
    if (authResult) {
        try {
            // Декодируем данные
            const userData = JSON.parse(atob(authResult));
            console.log('Telegram Auth Success:', userData);
            
            // Сохраняем пользователя
            const user = {
                telegram_id: userData.id,
                first_name: userData.first_name,
                username: userData.username,
                auth_date: userData.auth_date
            };
            
            // Проверяем, есть ли пользователь в БД
            checkAndLoginUser(user);
            
        } catch (e) {
            console.error('Ошибка обработки OAuth:', e);
            alert('Ошибка авторизации через Telegram');
        }
    }
}

async function checkAndLoginUser(user) {
    try {
        // Проверяем, существует ли пользователь
        const response = await fetch(`${API_BASE}/tutors/${user.telegram_id}/check`);
        const data = await response.json();
        
        if (!data.exists) {
            alert('Пользователь не найден. Сначала зарегистрируйтесь в боте.');
            return;
        }
        
        // Сохраняем сессию
        localStorage.setItem('tutor_user', JSON.stringify({
            telegram_id: user.telegram_id,
            name: user.first_name,
            students_count: data.students_count
        }));
        
        currentTutorId = user.telegram_id;
        
        // Показываем дашборд
        document.getElementById('auth-section').style.display = 'none';
        document.getElementById('dashboard-section').style.display = 'block';
        
        await loadDashboard(user.telegram_id);
        
        // Очищаем URL от параметров
        window.history.replaceState({}, document.title, window.location.pathname);
        
    } catch (error) {
        console.error('Ошибка проверки пользователя:', error);
        alert('Ошибка подключения к серверу');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Проверяем OAuth-ответ
    handleTelegramAuth();
    
    // Восстанавливаем сессию из localStorage
    const savedUser = localStorage.getItem('tutor_user');
    if (savedUser) {
        try {
            const user = JSON.parse(savedUser);
            currentTutorId = user.telegram_id;
            document.getElementById('auth-section').style.display = 'none';
            document.getElementById('dashboard-section').style.display = 'block';
            loadDashboard(user.telegram_id);
            return;
        } catch (e) {
            localStorage.removeItem('tutor_user');
        }
    }
    
    // Если нет сессии — показываем вход
    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('dashboard-section').style.display = 'none';
    
    // Обработчики
    document.getElementById('login-btn').addEventListener('click', handleLogin);
    document.getElementById('telegram-id').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleLogin();
    });
});

// // ========== СОЗДАНИЕ ПРИГЛАШЕНИЯ ==========

// async function handleCreateInvite() {
//     const input = document.getElementById('student-name');
//     const studentName = input.value.trim();
//     const resultDiv = document.getElementById('invite-result');

//     if (!studentName) {
//         resultDiv.innerHTML = '<p class="error">Введите имя ученика</p>';
//         return;
//     }

//     if (!currentTutorId) {
//         resultDiv.innerHTML = '<p class="error">Сначала войдите в систему</p>';
//         return;
//     }

//     const btn = document.getElementById('create-invite-btn');
//     btn.disabled = true;
//     resultDiv.innerHTML = '<p class="loading">Создание приглашения...</p>';

//     try {
//         const response = await fetch(
//             `${API_BASE}/tutors/${currentTutorId}/invites?student_name=${encodeURIComponent(studentName)}`,
//             { method: 'POST' }
//         );

//         const data = await response.json();

//         if (response.ok) {
//             resultDiv.innerHTML = `
//                 <div class="success">
//                     ✅ Приглашение создано!
//                     <br>
//                     Код: <strong>${data.code}</strong>
//                     <br>
//                     <small>Скопируйте ссылку:</small>
//                     <br>
//                     <input type="text" value="${data.link}" style="width: 100%; margin-top: 5px; padding: 8px; border: 1px solid #e2e8f0; border-radius: 4px; font-size: 12px;" readonly onclick="this.select()">
//                 </div>
//             `;
//             input.value = '';
//             await loadInvites(currentTutorId);
//         } else {
//             resultDiv.innerHTML = `<p class="error">❌ ${data.detail || 'Ошибка создания приглашения'}</p>`;
//         }

//     } catch (error) {
//         console.error('Ошибка создания приглашения:', error);
//         resultDiv.innerHTML = '<p class="error">Ошибка подключения к серверу</p>';
//     } finally {
//         btn.disabled = false;
//     }
// }

// // ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

// function formatDate(dateString) {
//     const date = new Date(dateString);
//     return date.toLocaleDateString('ru-RU', {
//         day: '2-digit',
//         month: '2-digit',
//         year: 'numeric'
//     });
// }

// ========== ВЫХОД ==========

document.getElementById('logout-btn')?.addEventListener('click', function() {
    // Удаляем пользователя из localStorage
    localStorage.removeItem('tutor_user');
    localStorage.removeItem('telegram_user');
    
    // Очищаем текущую сессию
    currentTutorId = null;
    
    // Перезагружаем страницу
    window.location.href = '/';
});

document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, есть ли пользователь в localStorage
    const savedUser = localStorage.getItem('tutor_user');
    if (savedUser) {
        try {
            const user = JSON.parse(savedUser);
            currentTutorId = user.telegram_id;
            
            // Сразу показываем дашборд
            document.getElementById('auth-section').style.display = 'none';
            document.getElementById('dashboard-section').style.display = 'block';
            loadDashboard(currentTutorId);
        } catch (e) {
            console.error('Ошибка восстановления сессии:', e);
            localStorage.removeItem('tutor_user');
        }
    }
});