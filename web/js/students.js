function studentsApp() {
    return {
        user: null,
        students: [],
        filteredStudents: [],
        search: '',
        filterStatus: 'all',
        modalOpen: false,
        newStudent: {
            name: '',
            telegram: '',
            subject: '',
            lessons: 10,
            price: 1500
        },
        
        async init() {
            await this.loadUser();
            if (this.user) {
                await this.loadStudents();
            }
        },
        
        // loadUser() {
        //     const userData = localStorage.getItem('tutor_user');
        //     if (userData) {
        //         this.user = JSON.parse(userData);
        //     } else {
        //         window.location.href = '/static/index.html';
        //     }
        // },
        
        // async loadStudents() {
        //     try {
        //         const response = await fetch(`/api/tutors/${this.user.id}/students`);
        //         const data = await response.json();
        //         this.students = data;
        //         this.filterStudents();
        //     } catch (e) {
        //         console.error('Ошибка загрузки учеников:', e);
        //         this.students = [];
        //     }
        // },
        
        // filterStudents() {
        //     const searchLower = this.search.toLowerCase();
        //     this.filteredStudents = this.students.filter(s => {
        //         const matchSearch = s.name.toLowerCase().includes(searchLower) ||
        //             (s.telegram && s.telegram.toLowerCase().includes(searchLower));
        //         const matchStatus = this.filterStatus === 'all' || s.status === this.filterStatus;
        //         return matchSearch && matchStatus;
        //     });
        // },
        
        // getStatusText(status) {
        //     const map = {
        //         'active': 'Активен',
        //         'paused': 'Приостановлен',
        //         'inactive': 'Неактивен'
        //     };
        //     return map[status] || status;
        // },
        
        // openModal() {
        //     this.modalOpen = true;
        //     this.newStudent = { name: '', telegram: '', subject: '', lessons: 10, price: 1500 };
        // },
        
        // closeModal() {
        //     this.modalOpen = false;
        // },
        
        // async addStudent() {
        //     if (!this.newStudent.name) {
        //         alert('Введите имя ученика');
        //         return;
        //     }
            
        //     try {
        //         const response = await fetch(`/api/tutors/${this.user.id}/students`, {
        //             method: 'POST',
        //             headers: { 'Content-Type': 'application/json' },
        //             body: JSON.stringify(this.newStudent)
        //         });
                
        //         if (response.ok) {
        //             await this.loadStudents();
        //             this.closeModal();
        //         }
        //     } catch (e) {
        //         console.error('Ошибка добавления ученика:', e);
        //     }
        // },
        
        // viewStudent(id) {
        //     window.location.href = `/static/student.html?id=${id}`;
        // },
        
        // async deleteStudent(id) {
        //     if (!confirm('Удалить ученика?')) return;
            
        //     try {
        //         await fetch(`/api/tutors/${this.user.id}/students/${id}`, {
        //             method: 'DELETE'
        //         });
        //         await this.loadStudents();
        //     } catch (e) {
        //         console.error('Ошибка удаления ученика:', e);
        //     }
        // },
        
        // logout() {
        //     localStorage.removeItem('tutor_token');
        //     localStorage.removeItem('tutor_user');
        //     window.location.href = '/static/index.html';
        // }
    };
}