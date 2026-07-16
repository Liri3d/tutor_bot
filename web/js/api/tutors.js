import { ApiClient } from './client.js';

const api = new ApiClient();

export const TutorsAPI = {
    getStudents(tutorId) {
        return api.get(`/tutors/${tutorId}/students`);
    },

    getStats(tutorId) {
        return api.get(`/tutors/${tutorId}/stats`);
    },

    getInvites(tutorId) {
        return api.get(`/tutors/${tutorId}/invites`);
    },

    createInvite(tutorId, studentName) {
        return api.post(`/tutors/${tutorId}/invites`, null, {
            params: { student_name: studentName },
        });
    },
};