// web/js/app.js
// Обновлённый файл с поддержкой JWT аутентификации

// ========== Auth App (Страница входа) ==========
function authApp() {
    return {
        // Данные формы
        loginData: {
            username: '',
            password: ''
        },
        
        // Состояния
        loading: false,
        error: '',
        message: '',
        
        // Функция входа
        async login() {
            // 1. Включаем состояние загрузки
            this.loading = true;
            this.error = '';
            
            try {
                // 2. Отправляем POST запрос на сервер
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        login: this.loginData.username,
                        password: this.loginData.password
                    })
                });
                
                // 3. Получаем ответ от сервера
                const data = await response.json();

                // 4. Проверяем успешность
                if (response.ok && data.access_token) {
                    // 4a. Сохраняем JWT токен и данные пользователя
                    localStorage.setItem('tutor_jwt_token', data.access_token);
                    localStorage.setItem('tutor_user', JSON.stringify({
                        user_id: data.user_id,
                        login: data.login,
                        first_name: data.first_name,
                        role: data.role
                    }));
                    
                    // 4b. Переходим на дашборд
                    window.location.href = '/dashboard.html';
                    
                } else {
                    // 4c. Показываем ошибку
                    this.error = data.detail || 'Неверный логин или пароль';
                }
                
            } catch (error) {
                // 5. Обработка ошибок сети
                console.error('Ошибка входа:', error);
                this.error = 'Ошибка подключения к серверу';
                
            } finally {
                // 6. Выключаем состояние загрузки
                this.loading = false;
            }
        },
        
        // Вспомогательная функция для получения JWT токена
        getJwtToken() {
            return localStorage.getItem('tutor_jwt_token');
        },
        
        // Вспомогательная функция для получения заголовков авторизации
        getAuthHeaders() {
            const token = this.getJwtToken();
            return {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            };
        },
        
        // Проверка аутентификации
        isAuthenticated() {
            return !!this.getJwtToken();
        },
        
        // Инициализация
        init() {
            // Проверяем, есть ли сообщение
            const urlParams = new URLSearchParams(window.location.search);
            const msg = urlParams.get('message');
            if (msg) {
                this.message = decodeURIComponent(msg);
            }
            
            // Автозаполнение логина
            const login = urlParams.get('login');
            if (login) {
                this.loginData.username = decodeURIComponent(login);
                setTimeout(() => {
                    const passwordInput = document.querySelector('input[type="password"]');
                    if (passwordInput) passwordInput.focus();
                }, 100);
            }

            // Проверяем, залогинен ли пользователь (есть ли JWT токен)
            const token = localStorage.getItem('tutor_jwt_token');
            if (token) {
                window.location.href = '/dashboard.html';
            }
        }
    };
}


// ========== Утилиты для API запросов ==========
const API = {
    async get(endpoint) {
        const token = localStorage.getItem('tutor_jwt_token');
        const headers = {
            'Authorization': `Bearer ${token}`
        };
        
        const response = await fetch(endpoint, { headers });
        
        if (response.status === 401) {
            // Токен истёк или невалиден — перенаправляем на вход
            localStorage.removeItem('tutor_jwt_token');
            localStorage.removeItem('tutor_user');
            window.location.href = '/';
            return null;
        }
        
        return response.json();
    },
    
    async post(endpoint, data) {
        const token = localStorage.getItem('tutor_jwt_token');
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers,
            body: JSON.stringify(data)
        });
        
        if (response.status === 401) {
            localStorage.removeItem('tutor_jwt_token');
            localStorage.removeItem('tutor_user');
            window.location.href = '/';
            return null;
        }
        
        return response.json();
    },
    
    async delete(endpoint) {
        const token = localStorage.getItem('tutor_jwt_token');
        const headers = {
            'Authorization': `Bearer ${token}`
        };
        
        const response = await fetch(endpoint, {
            method: 'DELETE',
            headers
        });
        
        if (response.status === 401) {
            localStorage.removeItem('tutor_jwt_token');
            localStorage.removeItem('tutor_user');
            window.location.href = '/';
            return null;
        }
        
        return response.json();
    }
};


// ========== Dashboard App ==========
function dashboardApp() {
    return {
        user: null,
        stats: {
            total_students: 0,
            active_students: 0,
            lessons_this_week: 0,
            lessons_this_month: 0
        },
        loading: true,
        error: '',
        
        async init() {
            const userData = localStorage.getItem('tutor_user');
            const token = localStorage.getItem('tutor_jwt_token');
            
            if (!userData || !token) {
                console.log('❌ Нет данных пользователя или токена');
                window.location.href = '/';
                return;
            }

            try {
                this.user = JSON.parse(userData);
                console.log('✅ Пользователь загружен:', this.user);
                console.log('👤 Имя:', this.user.first_name);
            } catch (e) {
                console.error('❌ Ошибка парсинга:', e);
                window.location.href = '/';
                return;
            }

            // Загружаем статистику
            await this.loadStats();
            this.loading = false;
        },
        
        async loadStats() {
            try {
                const data = await API.get(`/api/tutors/${this.user.user_id}/stats`);
                if (data) {
                    this.stats = data;
                }
            } catch (e) {
                console.error('Ошибка загрузки статистики:', e);
            }
        },
        
        logout() {
            localStorage.removeItem('tutor_jwt_token');
            localStorage.removeItem('tutor_user');
            window.location.href = '/';
        }
    };
}
