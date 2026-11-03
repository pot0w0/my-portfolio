export interface User {
  id: number
  username: string
  email?: string
  avatar?: string
  created_at?: string
}

export interface Post {
  id: number
  title: string
  content: string
  user_id: number
  author?: User
  created_at?: string
  updated_at?: string
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