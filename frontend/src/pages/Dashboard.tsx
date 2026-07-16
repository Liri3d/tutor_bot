import React, { useEffect, useState } from 'react'
import { storage } from '../services/api'

interface DashboardProps {
  onLogout: () => void
}

function Dashboard({ onLogout }: DashboardProps) {
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const userData = storage.getUser()
    setUser(userData)
  }, [])

  if (!user) {
    return <div>Загрузка...</div>
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>🎓 Tutor Bot</h1>
        <button onClick={onLogout} style={styles.logoutButton}>
          🚪 Выйти
        </button>
      </div>

      <div style={styles.content}>
        <div style={styles.welcomeCard}>
          <h2>👋 Добро пожаловать, {user.first_name}!</h2>
          <p style={styles.info}>
            <strong>Роль:</strong> {user.role === 'tutor' ? '👨‍🏫 Репетитор' : '👨‍🎓 Ученик'}
          </p>
          <p style={styles.info}>
            <strong>Логин:</strong> {user.login}
          </p>
          <p style={styles.info}>
            <strong>ID:</strong> {user.id}
          </p>
        </div>

        <div style={styles.grid}>
          <div style={styles.card}>
            <h3>📊 Статистика</h3>
            <p>Здесь будет ваша статистика</p>
          </div>
          <div style={styles.card}>
            <h3>📅 Расписание</h3>
            <p>Здесь будет ваше расписание</p>
          </div>
        </div>
      </div>
    </div>
  )
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    minHeight: '100vh',
    background: '#f0f2f5',
  },
  header: {
    background: 'white',
    padding: '20px 40px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  title: {
    margin: 0,
    fontSize: '24px',
    color: '#2d3748',
  },
  logoutButton: {
    padding: '10px 20px',
    background: '#e53e3e',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    transition: 'background 0.2s',
  },
  content: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '40px 20px',
  },
  welcomeCard: {
    background: 'white',
    borderRadius: '16px',
    padding: '30px',
    marginBottom: '30px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
  },
  info: {
    margin: '8px 0',
    fontSize: '16px',
    color: '#4a5568',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '20px',
  },
  card: {
    background: 'white',
    borderRadius: '16px',
    padding: '24px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
  },
}

export default Dashboard