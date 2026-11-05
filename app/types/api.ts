export interface User {
  id: number
  username: string
  role?: 'user' | 'admin'
  email?: string
  avatar?: string
  created_at?: string
}

export interface Category { id: number; name: string; slug: string }
export interface Tag { id: number; name: string; slug: string }

export interface Post {
  id: number
  title: string
  content: string
  user_id: number
  category?: Category | null
  tags?: Tag[]
  featured?: boolean
  author?: User
  created_at?: string
  updated_at?: string
}

export interface PostPayload {
  title: string
  content: string
  category_id?: number | null
  tag_ids?: number[]
  featured?: boolean
}

export interface PostListQuery {
  page?: number
  limit?: number
  user_id?: number
  category?: string     // slug
  tag?: string          // slug
  featured?: boolean
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

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  username: string
  password: string
  email?: string
}

export interface AuthResponse {
  token: string
  user: User
}

export interface PostPayload {
  title: string
  content: string
}

export interface PostListQuery {
  page?: number
  limit?: number
  user_id?: number
}
