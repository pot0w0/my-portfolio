import type {
  AuthResponse,
  LoginPayload,
  RegisterPayload,
  User,
} from '~/types/api'

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
    const res = await api.post<AuthResponse>('/api/user/register', payload)
    // 兼容：注册接口可能只返回 user 不返回 token
    if ((res as any).token) setAuth((res as any).token, (res as any).user ?? res)
    return res
  }

  async function fetchMe() {
    try {
      const me = await api.get<User>('/api/user/me')
      user.value = me
      return me
    } catch (e: any) {
      if (e?.status === 401) clearAuth()
      return null
    }
  }

  async function logout() {
    try {
      await api.post('/api/user/logout')
    } catch {
      // 忽略登出接口错误，本地必须清掉
    } finally {
      clearAuth()
    }
  }

  /** 应用启动时调用一次：恢复 token 并拉取 me */
  async function init() {
    if (initialized.value) return
    initialized.value = true
    if (import.meta.client) {
      const saved = localStorage.getItem('auth:token')
      if (saved) token.value = saved
    }
    if (token.value) await fetchMe()
  }

  return {
    token,
    user,
    isLoggedIn,
    isAdmin,
    login,
    register,
    fetchMe,
    logout,
    init,
    setAuth,
    clearAuth,
  }
}