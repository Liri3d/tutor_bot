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
                    
            if (!userData) {
                console.log('❌ Нет данных пользователя');
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

            // ✅ ЗАГРУЖАЕМ СТАТИСТИКУ
            this.loadStats();
            this.loading = false;
            
            // Проверяем токен
            const token = localStorage.getItem('tutor_token');
            if (!token) {
                window.location.href = '/';
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
        
        async loadStats() {
            try {
                const response = await fetch(`/api/tutors/${this.user.id}/stats`);
                const data = await response.json();
                this.stats = data;
            } catch (e) {
                console.error('Ошибка загрузки статистики:', e);
            }
        },
        
        logout() {
            localStorage.removeItem('tutor_token');
            localStorage.removeItem('tutor_user');
            window.location.href = '/static/index.html';
        }
    };
}