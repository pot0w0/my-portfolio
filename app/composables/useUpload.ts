import type { Series, User } from '~/types/api'

export function useUpload() {
  const api = useApi()

  async function uploadAvatar(file: File) {
    const form = new FormData()
    form.append('file', file)
    const user = await api.post<User>('/api/user/me/avatar', form)
    // 同步全局 user
    const { user: authUser } = useAuth()
    authUser.value = user
    return user
  }

  async function removeAvatar() {
    const user = await api.del<User>('/api/user/me/avatar')
    const { user: authUser } = useAuth()
    authUser.value = user
    return user
  }

  // async function uploadSeriesCover(seriesId: number, file: File) {
  //   const form = new FormData()
  //   form.append('file', file)
  //   return api.post<Series>(`/api/series/${seriesId}/cover`, form)
  // }

  // async function removeSeriesCover(seriesId: number) {
  //   return api.del<Series>(`/api/series/${seriesId}/cover`)
  // }

  async function uploadPostImage(postId: number, file: File) {
    const form = new FormData()
    form.append('file', file)
    return api.post<{ url: string }>(`/api/posts/${postId}/images`, form)
  }

  async function uploadPostCover(postId: number, file: File) {
    const form = new FormData()
    form.append('file', file)
    return api.post<Post>(`/api/posts/${postId}/cover`, form)
  }

  async function removePostCover(postId: number) {
    return api.del<Post>(`/api/posts/${postId}/cover`)
  }

  async function uploadBodyImage(file: File) {
    const form = new FormData()
    form.append('file', file)
    return api.post<{ url: string }>('/api/uploads/images', form)
  }

  return {
    uploadAvatar, removeAvatar,
    uploadPostImage,
    uploadPostCover, removePostCover, uploadBodyImage
  }
}