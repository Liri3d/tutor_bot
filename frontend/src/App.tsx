import React, { useState, useEffect } from 'react'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import { storage } from './services/api'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showRegister, setShowRegister] = useState(false)
  const [user, setUser] = useState(null)

  // Проверяем, есть ли сохранённый пользователь
  useEffect(() => {
    const savedUser = storage.getUser()
    if (savedUser) {
      setUser(savedUser)
      setIsAuthenticated(true)
    }
  }, [])

  const handleLoginSuccess = (userData: any) => {
    setUser(userData)
    setIsAuthenticated(true)
    setShowRegister(false)
  }

  const handleRegisterSuccess = (userData: any) => {
    setUser(userData)
    setIsAuthenticated(true)
    setShowRegister(false)
  }

  const handleLogout = () => {
    storage.clearUser()
    setUser(null)
    setIsAuthenticated(false)
  }

  // Если пользователь авторизован - показываем дашборд
  if (isAuthenticated) {
    return <Dashboard onLogout={handleLogout} />
  }

  // Если страница регистрации
  if (showRegister) {
    return (
      <Register
        onRegisterSuccess={handleRegisterSuccess}
        onSwitchToLogin={() => setShowRegister(false)}
      />
    )
  }

  // Страница входа
  return (
    <Login
      onLoginSuccess={handleLoginSuccess}
      onSwitchToRegister={() => setShowRegister(true)}
    />
  )
}

export default App