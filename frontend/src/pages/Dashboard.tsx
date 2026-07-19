// src/pages/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { tutorAPI, authAPI } from '../services/api';

interface User {
  id: number;
  login: string;
  first_name: string;
  role: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState({
    total_students: 0,
    active_students: 0,
    lessons_this_week: 0,
    lessons_this_month: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const userData = localStorage.getItem('tutor_user');
    if (!userData) {
      navigate('/login');
      return;
    }

    const parsedUser = JSON.parse(userData);
    setUser(parsedUser);
    loadStats(parsedUser.id);
  }, []);

  const loadStats = async (telegramId: number) => {
    try {
      const response = await tutorAPI.getStats(telegramId);
      setStats(response.data);
    } catch (err: any) {
      setError('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    authAPI.logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div style={styles.loading}>
        <p>Загрузка...</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <h1 style={styles.logo}>📚 Tutor Flow</h1>
          <div style={styles.userInfo}>
            <span style={styles.userName}>👋 {user?.first_name}</span>
            <button onClick={handleLogout} style={styles.logoutBtn}>
              Выйти
            </button>
          </div>
        </div>
      </header>

      <main style={styles.main}>
        <h2 style={styles.greeting}>Добро пожаловать, {user?.first_name}! 👋</h2>

        {error && <div style={styles.error}>{error}</div>}

        <div style={styles.statsGrid}>
          <div style={styles.statCard}>
            <div style={styles.statIcon}>👥</div>
            <div>
              <div style={styles.statLabel}>Всего учеников</div>
              <div style={styles.statValue}>{stats.total_students}</div>
            </div>
          </div>

          <div style={styles.statCard}>
            <div style={styles.statIcon}>📅</div>
            <div>
              <div style={styles.statLabel}>Занятий на неделе</div>
              <div style={styles.statValue}>{stats.lessons_this_week}</div>
            </div>
          </div>

          <div style={styles.statCard}>
            <div style={styles.statIcon}>📊</div>
            <div>
              <div style={styles.statLabel}>Занятий за месяц</div>
              <div style={styles.statValue}>{stats.lessons_this_month}</div>
            </div>
          </div>

          <div style={styles.statCard}>
            <div style={styles.statIcon}>✅</div>
            <div>
              <div style={styles.statLabel}>Активных учеников</div>
              <div style={styles.statValue}>{stats.active_students}</div>
            </div>
          </div>
        </div>

        <div style={styles.actionsGrid}>
          <button style={styles.actionCard}>
            <span style={styles.actionIcon}>👥</span>
            Мои ученики
          </button>
          <button style={styles.actionCard}>
            <span style={styles.actionIcon}>📅</span>
            Расписание
          </button>
          <button style={styles.actionCard}>
            <span style={styles.actionIcon}>➕</span>
            Создать урок
          </button>
          <button style={styles.actionCard}>
            <span style={styles.actionIcon}>🔗</span>
            Пригласить ученика
          </button>
        </div>
      </main>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    minHeight: '100vh',
    background: '#F8FAFC',
  },
  loading: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    fontSize: '18px',
    color: '#64748B',
  },
  header: {
    background: '#FFFFFF',
    borderBottom: '1px solid #E2E8F0',
    padding: '16px 32px',
  },
  headerContent: {
    maxWidth: '1200px',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logo: {
    fontSize: '20px',
    fontWeight: 600,
    color: '#1E293B',
    margin: 0,
  },
  userInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  userName: {
    fontSize: '14px',
    fontWeight: 500,
    color: '#1E293B',
  },
  logoutBtn: {
    padding: '6px 16px',
    borderRadius: '6px',
    border: '1px solid #E2E8F0',
    background: 'transparent',
    color: '#64748B',
    cursor: 'pointer',
    fontSize: '14px',
    transition: 'all 0.2s',
  },
  main: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '32px',
  },
  greeting: {
    fontSize: '24px',
    fontWeight: 500,
    color: '#1E293B',
    margin: '0 0 24px 0',
  },
  error: {
    padding: '12px',
    borderRadius: '8px',
    background: '#FEE2E2',
    color: '#991B1B',
    marginBottom: '20px',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
    marginBottom: '32px',
  },
  statCard: {
    background: '#FFFFFF',
    padding: '20px',
    borderRadius: '12px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  statIcon: {
    fontSize: '32px',
  },
  statLabel: {
    fontSize: '14px',
    color: '#64748B',
  },
  statValue: {
    fontSize: '24px',
    fontWeight: 600,
    color: '#1E293B',
  },
  actionsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
  },
  actionCard: {
    background: '#FFFFFF',
    padding: '20px',
    borderRadius: '12px',
    border: 'none',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    fontSize: '16px',
    fontWeight: 500,
    color: '#1E293B',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  actionIcon: {
    fontSize: '24px',
  },
};

export default Dashboard;