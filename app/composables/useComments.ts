import type { Comment } from '~/types/api'

export function useComments() {
  const api = useApi()
  return {
    list: (postId: number | string) =>
      api.get<Comment[]>(`/api/posts/${postId}/comments`),
    create: (postId: number | string, content: string) =>
      api.post<Comment>(`/api/posts/${postId}/comments`, { content }),
    remove: (commentId: number | string) =>
      api.del<void>(`/api/comments/${commentId}`),
  }
}