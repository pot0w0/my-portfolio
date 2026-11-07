export interface User {
  id: number
  username: string
  role?: 'user' | 'admin'
  email?: string
  avatar?: string | null
  created_at?: string
}

export interface Tag {
  id: number
  name: string
  slug: string
}

export interface Series {
  id: number
  title: string
  slug: string
  description?: string
  cover?: string | null
  user_id: number
  intro_post_id?: number | null
  author?: User
  post_count?: number
  created_at?: string
  updated_at?: string
}

export interface SeriesDetail {
  series: Series
  intro: Post | null
  posts: Post[]
}

export interface Post {
  id: number
  title: string
  content: string
  user_id: number
  series_id?: number | null
  series_order?: number | null
  series?: Series | null
  tags?: Tag[]
  featured?: boolean
  author?: User
  created_at?: string
  updated_at?: string
  cover?: string | null
}

export interface Comment {
  id: number
  post_id: number
  user_id: number
  content: string
  author?: User
  created_at?: string
}

export interface Paginated<T> {
  data: T[]
  total: number
  page: number
  limit: number
}

export interface ApiError {
  status: number
  message: string
}

export interface LoginPayload { username: string; password: string }
export interface RegisterPayload { username: string; password: string; email?: string }
export interface AuthResponse { token: string; user: User }

export interface PostPayload {
  title: string
  content: string
  tag_ids?: number[]
  featured?: boolean
  series_id?: number | null
  series_order?: number | null
  cover?: string | null
}

export interface PostListQuery {
  page?: number
  limit?: number
  user_id?: number
  tag?: string
  featured?: boolean
  series_id?: number
  standalone?: boolean
  q?: string
  year?: number
  sort?: string
  order?: string
}

export interface ProfilePayload {
  username?: string
  email?: string
  password?: string
}

export interface SearchItem {
  type: 'post' | 'series' | 'tag' | 'user'
  id: number
  title: string
  subtitle: string
  url: string
  matched: string
}

export interface SearchOut {
  items: SearchItem[]
  post_filters: Record<string, string>
}
