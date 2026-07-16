import React, { useState } from 'react'
import { authApi, storage } from '../services/api'

interface LoginProps {
  onLoginSuccess: (user: any) => void
  onSwitchToRegister: () => void
}

function Login({ onLoginSuccess, onSwitchToRegister }: LoginProps) {
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await authApi.login({ login, password })
      
      // Сохраняем пользователя
      storage.setUser(response)
      
      // Вызываем callback успешного входа
      onLoginSuccess(response)
    } catch (err: any) {
      setError(err.message || 'Ошибка при входе')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <h1 style={styles.title}>🎓 Tutor Bot</h1>
          <p style={styles.subtitle}>Вход в систему</p>
        </div>

        {error && (
          <div style={styles.errorBox}>
            ❌ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Логин</label>
            <input
              type="text"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              placeholder="Введите логин"
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
              placeholder="Введите пароль"
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
            {loading ? '⏳ Вход...' : '🚀 Войти'}
          </button>
        </form>

        <div style={styles.footer}>
          <span style={styles.footerText}>Нет аккаунта?</span>
          <button
            onClick={onSwitchToRegister}
            style={styles.linkButton}
            disabled={loading}
          >
            Зарегистрироваться
          </button>
        </div>

        <div style={styles.demoInfo}>
          <p style={styles.demoText}>Демо-данные:</p>
          <p style={styles.demoText}>Логин: <strong>tutor</strong> | Пароль: <strong>123456</strong></p>
        </div>
      </div>
    </div>
  )
}

// Стили (вынесены отдельно для чистоты)
const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
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
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
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
    color: '#667eea',
    fontSize: '14px',
    fontWeight: 600,
    cursor: 'pointer',
    textDecoration: 'underline',
    padding: 0,
  },
  demoInfo: {
    marginTop: '20px',
    padding: '12px',
    background: '#f7fafc',
    borderRadius: '8px',
    textAlign: 'center',
  },
  demoText: {
    margin: '4px 0',
    fontSize: '13px',
    color: '#4a5568',
  },
}

export default Login