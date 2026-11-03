import type { Comment } from '~/types/api'

export function useComments() {
  const api = useApi()

  function list(postId: number | string) {
    return api.get<Comment[]>(`/api/posts/${postId}/comments`)
  }
  function create(postId: number | string, content: string) {
    return api.post<Comment>(`/api/posts/${postId}/comments`, { content })
  }
  function remove(commentId: number | string) {
    return api.del<void>(`/api/comments/${commentId}`)
  }

  return { list, create, remove }
}