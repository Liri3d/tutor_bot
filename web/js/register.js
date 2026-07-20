function registerApp() {
            return {
                form: {
                    first_name: '',
                    login: '',
                    password: '',
                    confirmPassword: ''
                },
                loading: false,
                error: '',
                message: '',

                init() {
                    // Проверяем, есть ли сообщение от предыдущей страницы
                    const urlParams = new URLSearchParams(window.location.search);
                    const msg = urlParams.get('message');
                    if (msg) {
                        this.message = decodeURIComponent(msg);
                        // Убираем сообщение через 3 секунды
                        setTimeout(() => {
                            this.message = '';
                        }, 5000);
                    }
                },

                async register() {
                    // Валидация
                    if (!this.form.first_name || this.form.first_name.length < 2) {
                        this.error = 'Имя должно содержать минимум 2 символа';
                        return;
                    }

                    if (!this.form.login || this.form.login.length < 3) {
                        this.error = 'Логин должен содержать минимум 3 символа';
                        return;
                    }

                    if (!this.form.password || this.form.password.length < 6) {
                        this.error = 'Пароль должен содержать минимум 6 символов';
                        return;
                    }

                    if (this.form.password !== this.form.confirmPassword) {
                        this.error = 'Пароли не совпадают';
                        return;
                    }

                    this.loading = true;
                    this.error = '';

                    try {
                        const response = await fetch('/api/auth/register', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                login: this.form.login,
                                password: this.form.password,
                                first_name: this.form.first_name
                            })
                        });

                        const data = await response.json();

                        if (response.ok && data.status === 'registered') {
                            // Успешная регистрация
                            const login = this.form.login;
                            this.message = '✅ ' + (data.message || 'Регистрация успешна!');
                            
                            // Очищаем форму
                            this.form = {
                                first_name: '',
                                login: '',
                                password: '',
                                confirmPassword: ''
                            };

                            console.log('Редирект на главную с логином:', login); 
                            
                            // Перенаправляем на страницу входа через 2 секунды
                            setTimeout(() => {
                                window.location.href = '/?message=' + 
                                    encodeURIComponent('Регистрация успешна! Теперь войдите в систему.') + '&login=' + encodeURIComponent(login);
                            }, 2000);

                        } else {
                            this.error = data.detail || 'Ошибка регистрации';
                        }

                    } catch (e) {
                        console.error('Ошибка регистрации:', e);
                        this.error = 'Ошибка подключения к серверу';
                    } finally {
                        this.loading = false;
                    }
                }
            };
        }