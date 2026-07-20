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
                if (response.ok && data.status === 'authenticated') {
                    // 4a. Сохраняем данные пользователя
                    localStorage.setItem('tutor_token', data.id.toString());
                    localStorage.setItem('tutor_user', JSON.stringify({
                        id: data.id,
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
        
        // Инициализация
        init() {
            // Проверяем, есть ли сообщение
            const urlParams = new URLSearchParams(window.location.search);
            const msg = urlParams.get('message');
            if (msg) {
                this.message = decodeURIComponent(msg);
                // setTimeout(() => {
                //     this.message = '';
                // }, 5000);
            }
            
            // Автозаполнение логина
            const login = urlParams.get('login');
                if (login) {
                    this.loginData.username = decodeURIComponent(login);
                    // Можно автоматически поставить фокус на поле пароля
                    setTimeout(() => {
                        const passwordInput = document.querySelector('input[type="password"]');
                        if (passwordInput) passwordInput.focus();
                    }, 100);
                }

            // Проверяем, залогинен ли пользователь
            const token = localStorage.getItem('tutor_token');
            if (token) {
                window.location.href = '/dashboard.html';
            }
        }
    };
}


// ========== Уроки ==========
function lessonsApp() {
    return {
        user: null,
        lessons: [],
        filteredLessons: [],
        search: '',
        filterStatus: 'all',
        modalOpen: false,
        editingId: null,
        form: {
            title: '',
            student: '',
            date: '',
            time: '',
            duration: 60,
            status: 'scheduled',
            notes: ''
        },
        
        async init() {
            await this.loadUser();
            if (this.user) {
                await this.loadLessons();
                this.form.date = new Date().toISOString().split('T')[0];
                this.form.time = '10:00';
            }
        },
        
        loadUser() {
            const userData = localStorage.getItem('tutor_user');
            if (userData) {
                this.user = JSON.parse(userData);
            } else {
                window.location.href = '/static/index.html';
            }
        },
        
        async loadLessons() {
            try {
                const response = await fetch(`/api/tutors/${this.user.id}/lessons`);
                const data = await response.json();
                this.lessons = data;
                this.filterLessons();
            } catch (e) {
                console.error('Ошибка загрузки уроков:', e);
                this.lessons = [];
            }
        },
        
        filterLessons() {
            const searchLower = this.search.toLowerCase();
            this.filteredLessons = this.lessons.filter(l => {
                const matchSearch = (l.title || '').toLowerCase().includes(searchLower) ||
                    (l.student || '').toLowerCase().includes(searchLower);
                const matchStatus = this.filterStatus === 'all' || l.status === this.filterStatus;
                return matchSearch && matchStatus;
            });
        },
        
        getLessonStatus(status) {
            const map = {
                'scheduled': 'Запланирован',
                'completed': 'Завершён',
                'cancelled': 'Отменён',
                'missed': 'Пропущен'
            };
            return map[status] || status;
        },
        
        openModal() {
            this.modalOpen = true;
            this.editingId = null;
            this.form = {
                title: '',
                student: '',
                date: new Date().toISOString().split('T')[0],
                time: '10:00',
                duration: 60,
                status: 'scheduled',
                notes: ''
            };
        },
        
        closeModal() {
            this.modalOpen = false;
        },
        
        editLesson(id) {
            const lesson = this.lessons.find(l => l.id === id);
            if (lesson) {
                this.editingId = id;
                this.form = {
                    title: lesson.title || lesson.subject || '',
                    student: lesson.student || lesson.student_name || '',
                    date: lesson.date || lesson.start_time?.split('T')[0] || '',
                    time: lesson.time || lesson.start_time?.split('T')[1]?.substring(0, 5) || '',
                    duration: lesson.duration || lesson.duration_minutes || 60,
                    status: lesson.status || 'scheduled',
                    notes: lesson.notes || ''
                };
                this.modalOpen = true;
            }
        },
        
        async saveLesson() {
            if (!this.form.title || !this.form.student || !this.form.date || !this.form.time) {
                alert('Заполните все обязательные поля');
                return;
            }
            
            try {
                const url = this.editingId ? 
                    `/api/tutors/${this.user.id}/lessons/${this.editingId}` :
                    `/api/tutors/${this.user.id}/lessons`;
                const method = this.editingId ? 'PUT' : 'POST';
                
                const response = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.form)
                });
                
                if (response.ok) {
                    await this.loadLessons();
                    this.closeModal();
                }
            } catch (e) {
                console.error('Ошибка сохранения урока:', e);
            }
        },
        
        async deleteLesson(id) {
            if (!confirm('Удалить урок?')) return;
            
            try {
                await fetch(`/api/tutors/${this.user.id}/lessons/${id}`, {
                    method: 'DELETE'
                });
                await this.loadLessons();
            } catch (e) {
                console.error('Ошибка удаления урока:', e);
            }
        },
        
        formatDate(dateStr) {
            if (!dateStr) return '';
            const d = new Date(dateStr);
            return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' });
        },
        
        formatTime(timeStr) {
            if (!timeStr) return '';
            const d = new Date(timeStr);
            return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
        },
        
        logout() {
            localStorage.removeItem('tutor_token');
            localStorage.removeItem('tutor_user');
            window.location.href = '/static/index.html';
        }
    };
}

