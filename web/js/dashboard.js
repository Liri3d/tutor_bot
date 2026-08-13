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
                console.log('❌ Нет данных пользователя или JWT токена');
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
                const token = localStorage.getItem('tutor_jwt_token');
                const headers = {
                    'Authorization': `Bearer ${token}`
                };
                
                const response = await fetch(`/api/tutors/${this.user.user_id}/stats`, { headers });
                const data = await response.json();
                this.stats = data;
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
