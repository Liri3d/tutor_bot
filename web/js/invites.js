function invitesApp() {
    return {
        user: null,
        invites: [],
        inviteCode: '',
        modalOpen: false,
        newInvite: {
            student_name: '',
        },

        async init() {
            await this.loadUser();
            if (this.user) {
                await this.loadInvites();
            }
        },
        
        openModal() {
            this.modalOpen = true;
            this.newInvite = { student_name: '' };
        },
        
        closeModal() {
            this.modalOpen = false;
        },
        
        // loadUser() {
        //     const userData = localStorage.getItem('tutor_user');
        //     if (userData) {
        //         this.user = JSON.parse(userData);
        //     } else {
        //         window.location.href = '/static/index.html';
        //     }
        // },
        
        // async loadInvites() {
        //     try {
        //         const response = await fetch(`/api/tutors/${this.user.id}/invites`);
        //         const data = await response.json();
        //         this.invites = data;
        //     } catch (e) {
        //         console.error('Ошибка загрузки приглашений:', e);
        //         this.invites = [];
        //     }
        // },
        




        async addInvite() {
            if (!this.newInvite.student_name) {
                alert('Введите имя ученика');
                return;
            }
            
            try {
                const response = await fetch(`/api/tutors/${this.user.id}/invites`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.newInvite)
                });
                
                if (response.ok) {
                    
                    const data = await response.json();
                    this.inviteCode = data.code;
                    await this.loadInvites();

                    this.closeModal();
                }
            } catch (e) {
                console.error('Ошибка создания приглашения:', e);
            }
        },
        
        // copyInvite() {
        //     const link = `${window.location.origin}/api/invite/${this.inviteCode}`;
        //     navigator.clipboard?.writeText(link);
        //     alert('Ссылка скопирована!');
        // },
        
        // copyInviteLink(code) {
        //     const link = `${window.location.origin}/api/invite/${code}`;
        //     navigator.clipboard?.writeText(link);
        //     alert('Ссылка скопирована!');
        // },
        
        // formatDate(dateStr) {
        //     if (!dateStr) return '';
        //     const d = new Date(dateStr);
        //     return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' });
        // },
        
        // logout() {
        //     localStorage.removeItem('tutor_token');
        //     localStorage.removeItem('tutor_user');
        //     window.location.href = '/static/index.html';
        // }
    };
}