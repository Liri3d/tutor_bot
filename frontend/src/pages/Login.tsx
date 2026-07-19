// src/pages/Login.tsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../services/api';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.login({ login, password });
      
      if (response.data.status === 'authenticated') {
        // Сохраняем данные пользователя
        localStorage.setItem('tutor_token', response.data.id.toString());
        localStorage.setItem('tutor_user', JSON.stringify({
          id: response.data.id,
          login: response.data.login,
          first_name: response.data.first_name,
          role: response.data.role,
        }));
        
        navigate('/dashboard');
      } else {
        setError('Ошибка входа. Проверьте логин и пароль.');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка подключения к серверу');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <h1 style={styles.title}>📚 Tutor Flow</h1>
          <p style={styles.subtitle}>Вход в систему управления расписанием</p>
        </div>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Логин</label>
            <input
              type="text"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              placeholder="Введите логин"
              style={styles.input}
              required
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Введите пароль"
              style={styles.input}
              required
            />
          </div>

          {error && <div style={styles.error}>{error}</div>}

          <button
            type="submit"
            style={styles.button}
            disabled={loading}
          >
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>

        <div style={styles.footer}>
          <span>Нет аккаунта? </span>
          <Link to="/register" style={styles.link}>Зарегистрироваться</Link>
        </div>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#F8FAFC',
    padding: '20px',
  },
  card: {
    background: '#FFFFFF',
    borderRadius: '16px',
    padding: '40px',
    maxWidth: '420px',
    width: '100%',
    boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
  },
  header: {
    textAlign: 'center',
    marginBottom: '32px',
  },
  title: {
    fontSize: '28px',
    fontWeight: 600,
    color: '#1E293B',
    margin: '0 0 8px 0',
  },
  subtitle: {
    fontSize: '14px',
    color: '#64748B',
    margin: 0,
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  label: {
    fontSize: '14px',
    fontWeight: 500,
    color: '#1E293B',
  },
  input: {
    padding: '10px 14px',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
    fontSize: '14px',
    transition: 'border-color 0.2s',
    outline: 'none',
  },
  inputFocus: {
    borderColor: '#3B82F6',
    boxShadow: '0 0 0 3px rgba(59,130,246,0.1)',
  },
  button: {
    padding: '12px',
    borderRadius: '8px',
    border: 'none',
    background: '#3B82F6',
    color: '#FFFFFF',
    fontSize: '16px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'background 0.2s',
  },
  buttonHover: {
    background: '#2563EB',
  },
  error: {
    padding: '10px',
    borderRadius: '8px',
    background: '#FEE2E2',
    color: '#991B1B',
    fontSize: '14px',
    textAlign: 'center',
  },
  footer: {
    marginTop: '24px',
    textAlign: 'center',
    fontSize: '14px',
    color: '#64748B',
  },
  link: {
    color: '#3B82F6',
    textDecoration: 'none',
    fontWeight: 500,
  },
};

export default Login;