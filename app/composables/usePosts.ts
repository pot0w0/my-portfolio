import type { PageOut, Post, PostListQuery, PostPayload } from '~/types/api'

export function usePosts() {
  const api = useApi()

  function list(query: ListQuery = {}) {
    return api.get<PageOut<Post>>('/api/posts', query)
  }
  function get(id: number | string, opts?: { silent?: boolean }) {
    return api.get<Post>(`/api/posts/${id}`, undefined, opts)
  }
  function create(payload: PostPayload) {
    return api.post<Post>('/api/posts', payload)
  }
  function update(id: number | string, payload: PostPayload) {
    return api.put<Post>(`/api/posts/${id}`, payload)
  }
  function remove(id: number | string) {
    return api.del<void>(`/api/posts/${id}`)
  }

  return { list, get, create, update, remove }
}