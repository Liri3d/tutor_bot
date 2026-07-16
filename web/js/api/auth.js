import { ApiClient } from './client.js';

const api = new ApiClient();

export const AuthAPI = {
    register(data) {
        return api.post('/auth/register', data);
    },

    login(data) {
        return api.post('/auth/login', data);
    },

    logout() {
        return api.post('/auth/logout');
    },

    checkUser(telegramId) {
        return api.get(`/tutors/${telegramId}/check`);
    },

    getBotInfo() {
        return api.get('/bot/info');
    },
};