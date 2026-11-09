import type { Comment, CommentPage, LikeStats } from '~/types/api'

export function useComments() {
  const api = useApi()
  return {
    list: (postId: number | string, query?: ListQuery) =>
      api.get<CommentPage>(`/api/posts/${postId}/comments`, query),
    create: (postId: number | string, content: string, parentId?: number | null) =>
      api.post<Comment>(`/api/posts/${postId}/comments`, {
        content,
        ...(parentId ? { parent_id: parentId } : {}),
      }),
    remove: (commentId: number | string) =>
      api.del<void>(`/api/comments/${commentId}`),
    like: (commentId: number | string) =>
      api.post<LikeStats>(`/api/comments/${commentId}/like`),
    unlike: (commentId: number | string) =>
      api.del<LikeStats>(`/api/comments/${commentId}/like`),
  }
}
