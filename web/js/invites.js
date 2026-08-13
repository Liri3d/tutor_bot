// web/js/invites.js — с поддержкой JWT
function invitesApp() {
    return {
        user: null,
        invites: [],
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
            await this.loadInvites();
            this.loading = false;
        },
        
        async loadInvites() {
            try {
                const token = localStorage.getItem('tutor_jwt_token');
                const headers = { 'Authorization': `Bearer ${token}` };
                const response = await fetch(`/api/tutors/${this.user.user_id}/invites`, { headers });
                
                if (response.status === 401) {
                    localStorage.removeItem('tutor_jwt_token');
                    window.location.href = '/';
                    return;
                }
                
                const data = await response.json();
                this.invites = data;
            } catch (e) {
                console.error('Ошибка загрузки приглашений:', e);
                this.error = 'Не удалось загрузить приглашения';
            }
        },
        
        logout() {
            localStorage.removeItem('tutor_jwt_token');
            localStorage.removeItem('tutor_user');
            window.location.href = '/';
        }
    };
}
