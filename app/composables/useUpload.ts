export function useUpload() {
  const api = useApi()

  async function uploadImage(file: File): Promise<string> {
    const form = new FormData()
    form.append('file', file)
    const res = await api.post<{ url: string }>('/api/uploads/images', form)
    return res.url
  }

  return { uploadImage }
}
