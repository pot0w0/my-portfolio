import type { ApiError } from '~/types/api'

export function useApi() {
  const config = useRuntimeConfig()
  const token = useState<string | null>('auth:token', () => null)

  async function request<T>(
    path: string,
    options: Parameters<typeof $fetch>[1] = {},
  ): Promise<T> {
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> | undefined),
    }
    if (token.value) headers.Authorization = `Bearer ${token.value}`

    try {
      return await $fetch<T>(path, {
        baseURL: config.public.apiBase,
        ...options,
        headers,
      })
    } catch (err: any) {
      const status: number = err?.status ?? err?.statusCode ?? 0
      const message: string =
        err?.data?.message ?? err?.data?.error ?? err?.message ?? '请求失败'
      const e: ApiError = { status, message }
      throw e
    }
  }

  return {
    get: <T>(path: string, query?: Record<string, any>) =>
      request<T>(path, { method: 'GET', query }),
    post: <T>(path: string, body?: any) =>
      request<T>(path, { method: 'POST', body }),
    put: <T>(path: string, body?: any) =>
      request<T>(path, { method: 'PUT', body }),
    del: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
  }
}