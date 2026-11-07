// types/content.ts
import type { Post, Series, User, Tag } from '~/types/api'

export interface ContentItem {
  kind: 'post' | 'series'
  title: string
  to: string
  summary?: string
  cover?: string | null
  tags?: Tag[]
  featured?: boolean
  seriesName?: string       // post 所属系列名
  metaText?: string         // series 的 "N 篇"
  createdAt?: string
  author?: User
  authorId?: number
}