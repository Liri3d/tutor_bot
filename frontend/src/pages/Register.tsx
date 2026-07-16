import React, { useState } from 'react'
import { authApi, storage } from '../services/api'

interface RegisterProps {
  onRegisterSuccess: (user: any) => void
  onSwitchToLogin: () => void
}

function Register({ onRegisterSuccess, onSwitchToLogin }: RegisterProps) {
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [firstName, setFirstName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Валидация
    if (password !== confirmPassword) {
      setError('Пароли не совпадают')
      return
    }

    if (password.length < 6) {
      setError('Пароль должен содержать минимум 6 символов')
      return
    }

    setLoading(true)

    try {
      const response = await authApi.register({
        login,
        password,
        first_name: firstName || login,
      })
      
      // Сохраняем пользователя
      storage.setUser(response)
      
      // Вызываем callback успешной регистрации
      onRegisterSuccess(response)
    } catch (err: any) {
      setError(err.message || 'Ошибка при регистрации')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <h1 style={styles.title}>🎓 Tutor Bot</h1>
          <p style={styles.subtitle}>Регистрация репетитора</p>
        </div>

        {error && (
          <div style={styles.errorBox}>
            ❌ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Имя</label>
            <input
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              placeholder="Введите ваше имя"
              style={styles.input}
              disabled={loading}
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Логин</label>
            <input
              type="text"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              placeholder="Придумайте логин"
              style={styles.input}
              required
              disabled={loading}
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Минимум 6 символов"
              style={styles.input}
              required
              disabled={loading}
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Подтверждение пароля</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Повторите пароль"
              style={styles.input}
              required
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              ...styles.button,
              ...(loading ? styles.buttonDisabled : {})
            }}
          >
            {loading ? '⏳ Регистрация...' : '📝 Зарегистрироваться'}
          </button>
        </form>

        <div style={styles.footer}>
          <span style={styles.footerText}>Уже есть аккаунт?</span>
          <button
            onClick={onSwitchToLogin}
            style={styles.linkButton}
            disabled={loading}
          >
            Войти
          </button>
        </div>
      </div>
    </div>
  )
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    padding: '20px',
  },
  card: {
    background: 'white',
    borderRadius: '20px',
    padding: '40px',
    maxWidth: '400px',
    width: '100%',
    boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
  },
  header: {
    textAlign: 'center',
    marginBottom: '30px',
  },
  title: {
    margin: 0,
    fontSize: '28px',
    color: '#2d3748',
  },
  subtitle: {
    margin: '8px 0 0 0',
    color: '#718096',
    fontSize: '16px',
  },
  errorBox: {
    background: '#fed7d7',
    color: '#c53030',
    padding: '12px',
    borderRadius: '8px',
    marginBottom: '20px',
    fontSize: '14px',
    textAlign: 'center',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  inputGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  label: {
    fontSize: '14px',
    fontWeight: 600,
    color: '#2d3748',
  },
  input: {
    padding: '12px 16px',
    border: '2px solid #e2e8f0',
    borderRadius: '10px',
    fontSize: '16px',
    transition: 'border-color 0.2s',
    outline: 'none',
  },
  button: {
    padding: '14px',
    background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    fontSize: '16px',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'transform 0.2s, box-shadow 0.2s',
  },
  buttonDisabled: {
    opacity: 0.6,
    cursor: 'not-allowed',
  },
  footer: {
    marginTop: '20px',
    textAlign: 'center',
    display: 'flex',
    justifyContent: 'center',
    gap: '8px',
  },
  footerText: {
    color: '#718096',
    fontSize: '14px',
  },
  linkButton: {
    background: 'none',
    border: 'none',
    color: '#f5576c',
    fontSize: '14px',
    fontWeight: 600,
    cursor: 'pointer',
    textDecoration: 'underline',
    padding: 0,
  },
}

export default Register