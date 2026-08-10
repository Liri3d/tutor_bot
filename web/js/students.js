// web/js/students.js — с поддержкой JWT
function studentsApp() {
    return {
        user: null,
        students: [],
        loading: true,
        error: '',
        
        async init() {
            const userData = localStorage.getItem('tutor_user');
            const token = localStorage.getItem('tutor_jwt_token');
            
            if (!userData || !token) {
                window.location.href = '/';
                return;
            }
            
            this.user = JSON.parse(userData);
            await this.loadStudents();
            this.loading = false;
        },
        
        async loadStudents() {
            try {
                const token = localStorage.getItem('tutor_jwt_token');
                const headers = { 'Authorization': `Bearer ${token}` };
                const response = await fetch(`/api/tutors/${this.user.user_id}/students`, { headers });
                
                if (response.status === 401) {
                    localStorage.removeItem('tutor_jwt_token');
                    window.location.href = '/';
                    return;
                }
                
                const data = await response.json();
                this.students = data;
            } catch (e) {
                console.error('Ошибка загрузки учеников:', e);
                this.error = 'Не удалось загрузить учеников';
            }
        },
        
        logout() {
            localStorage.removeItem('tutor_jwt_token');
            localStorage.removeItem('tutor_user');
            window.location.href = '/';
        }
    };
}
