// 未设置头像时使用的默认头像（public/akari.png）
export const DEFAULT_AVATAR = '/akari.png'

export function useAvatarUrl() {
  const mediaUrl = useMediaUrl()
  return (path?: string | null) => mediaUrl(path) || DEFAULT_AVATAR
}
