import type { AuthResponse, LoginPayload, RegisterPayload, User } from '~/types/api'

export function useAuth() {
  const api = useApi()
  const token = useState<string | null>('auth:token', () => null)
  const user = useState<User | null>('auth:user', () => null)
  const initialized = useState<boolean>('auth:initialized', () => false)

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  function setAuth(t: string, u: User) {
    token.value = t
    user.value = u
    if (import.meta.client) localStorage.setItem('auth:token', t)
  }

  function clearAuth() {
    token.value = null
    user.value = null
    if (import.meta.client) localStorage.removeItem('auth:token')
  }

  async function login(payload: LoginPayload) {
    const res = await api.post<AuthResponse>('/api/user/login', payload)
    setAuth(res.token, res.user)
    return res.user
  }

  async function register(payload: RegisterPayload) {
    const res = await api.post<AuthResponse>('/api/user/register', payload, { silent: true })
    if (res.token) setAuth(res.token, res.user)
    return res
  }

  async function fetchMe() {
    try {
      const me = await api.get<User>('/api/user/me', undefined, { silent: true })
      user.value = me
      return me
    } catch (e: any) {
      if (e?.status === 401) clearAuth()
      return null
    }
  }

  async function logout() {
    try {
      await api.post('/api/user/logout', undefined, { silent: true })
    } finally {
      clearAuth()
    }
  }

  async function init() {
    if (initialized.value) return
    initialized.value = true
    if (import.meta.client) {
      const saved = localStorage.getItem('auth:token')
      if (saved) token.value = saved
    }
    if (token.value) await fetchMe()
  }

  async function uploadAvatar(file: File) {
    const form = new FormData()
    form.append('file', file)
    const res = await api.post<User>('/api/user/me/avatar', form)
    user.value = res
    return res
  }

  async function removeAvatar() {
    const res = await api.del<User>('/api/user/me/avatar')
    user.value = res
    return res
  }

  async function updateProfile(payload: ProfilePayload) {
    const res = await api.put<User>('/api/user/me', payload)
    user.value = res
    return res
  }

  return {
    token, user, isLoggedIn, isAdmin,
    login, register, fetchMe, logout, init,
    setAuth, clearAuth, uploadAvatar, removeAvatar,
    updateProfile, 
  }
}