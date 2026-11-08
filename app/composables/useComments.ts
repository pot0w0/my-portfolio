import type { Comment } from '~/types/api'

export function useComments() {
  const api = useApi()
  return {
    list: (postId: number | string, query?: ListQuery) =>
      api.get<PageOut<Comment>>(`/api/posts/${postId}/comments`, query),
    create: (postId: number | string, content: string) =>
      api.post<Comment>(`/api/posts/${postId}/comments`, { content }),
    remove: (commentId: number | string) =>
      api.del<void>(`/api/comments/${commentId}`),
  }
}