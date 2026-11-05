import type {
  Paginated,
  Post,
  PostListQuery,
  PostPayload,
} from '~/types/api'

export function usePosts() {
  const api = useApi()

  function list(query: PostListQuery = {}) {
    return api.get<Paginated<Post>>('/api/posts', query)
  }

  function get(id: number | string) {
    return api.get<Post>(`/api/posts/${id}`, {silent: true} as any)
  }

  // function create(payload: PostPayload) {
  //   return api.post<Post>('/api/posts', payload)
  // }

  // function update(id: number | string, payload: PostPayload) {
  //   return api.put<Post>(`/api/posts/${id}`, payload)
  // }
  function create(payload: PostPayload) { return api.post<Post>('/api/posts', payload) }
  function update(id: number | string, payload: PostPayload) { return api.put<Post>(`/api/posts/${id}`, payload) }

  function remove(id: number | string) {
    return api.del<void>(`/api/posts/${id}`)
  }

  return { list, get, create, update, remove }
}