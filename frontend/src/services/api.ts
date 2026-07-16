const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:80'

export interface LoginData {
  login: string
  password: string
}

export interface RegisterData {
  login: string
  password: string
  first_name: string
}

export interface AuthResponse {
  status: string
  id: number
  login: string
  first_name: string
  role: string
  message: string
}

// API функции
export const authApi = {
  // Вход
  login: async (data: LoginData): Promise<AuthResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Ошибка входа')
    }

    return response.json()
  },

  // Регистрация
  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...data,
        role: 'tutor'
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Ошибка регистрации')
    }

    return response.json()
  },

  // Проверка статуса (для будущих сессий)
  checkAuth: async (): Promise<boolean> => {
    // Здесь можно добавить проверку токена
    return !!localStorage.getItem('user')
  }
}

// Хранилище для пользователя (простая замена сессии)
export const storage = {
  getUser: () => {
    const user = localStorage.getItem('user')
    return user ? JSON.parse(user) : null
  },
  setUser: (user: any) => {
    localStorage.setItem('user', JSON.stringify(user))
  },
  clearUser: () => {
    localStorage.removeItem('user')
  }
}