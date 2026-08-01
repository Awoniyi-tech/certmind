import { create } from 'zustand'

const API_BASE = '/api'

export const useAuthStore = create((set, get) => ({
  user: null,
  token: localStorage.getItem('certmind_token') || null,
  isAuthenticated: !!localStorage.getItem('certmind_token'),
  loading: true,

  // Initialize — check if stored token is still valid
  init: async () => {
    const token = localStorage.getItem('certmind_token')
    if (!token) {
      set({ loading: false, isAuthenticated: false })
      return
    }
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        const user = await res.json()
        set({ user, token, isAuthenticated: true, loading: false })
      } else {
        localStorage.removeItem('certmind_token')
        set({ user: null, token: null, isAuthenticated: false, loading: false })
      }
    } catch {
      set({ loading: false })
    }
  },

  register: async (email, password, name) => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Registration failed')

    localStorage.setItem('certmind_token', data.token)
    set({ user: data.user, token: data.token, isAuthenticated: true })
    return data
  },

  login: async (email, password) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Login failed')

    localStorage.setItem('certmind_token', data.token)
    set({ user: data.user, token: data.token, isAuthenticated: true })
    return data
  },

  logout: () => {
    localStorage.removeItem('certmind_token')
    set({ user: null, token: null, isAuthenticated: false })
  },

  updateProfile: async (updates) => {
    const token = get().token
    const res = await fetch(`${API_BASE}/auth/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(updates),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Update failed')
    set({ user: data })
    return data
  },
}))
