import { useState, useEffect } from 'react'

interface User {
  id: number
  name: string
  email: string
}

function UserInfo() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // useEffect - выполняется при монтировании компонента
  useEffect(() => {
    // Имитация запроса к API
    const fetchUser = async () => {
      try {
        setLoading(true)
        // Здесь будет реальный запрос к API
        // const response = await fetch('/api/user')
        // const data = await response.json()

        // Пока используем mock-данные
        setTimeout(() => {
          setUser({
            id: 1,
            name: 'Иван Петров',
            email: 'ivan@example.com'
          })
          setLoading(false)
        }, 1500)
      } catch (err) {
        setError('Ошибка загрузки данных')
        setLoading(false)
      }
    }

    fetchUser()
  }, []) // Пустой массив = выполнить один раз при монтировании

  if (loading) {
    return <div style={{ padding: '20px', textAlign: 'center' }}>⏳ Загрузка...</div>
  }

  if (error) {
    return <div style={{ padding: '20px', color: 'red', textAlign: 'center' }}>❌ {error}</div>
  }

  return (
    <div style={{ padding: '20px' }}>
      <h3>👤 Информация о пользователе</h3>
      <p><strong>Имя:</strong> {user?.name}</p>
      <p><strong>Email:</strong> {user?.email}</p>
    </div>
  )
}

export default UserInfo