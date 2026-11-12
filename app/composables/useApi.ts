import type { ApiError } from '~/types/api'

export function useApi() {
  const config = useRuntimeConfig()
  const token = useState<string | null>('auth:token', () => null)
  const toast = useToast()

  async function request<T>(
    path: string,
    options: Parameters<typeof $fetch>[1] & { silent?: boolean } = {},
  ): Promise<T> {
    const { silent, ...fetchOpts } = options as any

    const headers: Record<string, string> = {
      ...(fetchOpts.headers as Record<string, string> | undefined),
    }
    if (token.value) headers.Authorization = `Bearer ${token.value}`

    try {
      return await $fetch<T>(path, {
        baseURL: config.public.apiBase,
        ...fetchOpts,
        headers,
      })
    } catch (err: any) {
      const status: number = err?.status ?? err?.statusCode ?? 0
      const message: string =
        err?.data?.detail ?? err?.data?.message ?? err?.data?.error ?? err?.message ?? '请求失败'

      if (!silent && status !== 401) toast.error(message)

      const e: ApiError = { status, message }
      throw e
    }
  }

  return {
    get: <T>(path: string, query?: Record<string, any>, opts?: { silent?: boolean }) =>
      request<T>(path, { method: 'GET', query, ...opts }),
    post: <T>(path: string, body?: any, opts?: { silent?: boolean }) =>
      request<T>(path, { method: 'POST', body, ...opts }),
    put: <T>(path: string, body?: any, opts?: { silent?: boolean }) =>
      request<T>(path, { method: 'PUT', body, ...opts }),
    del: <T>(path: string, opts?: { silent?: boolean }) =>
      request<T>(path, { method: 'DELETE', ...opts }),
  }
}