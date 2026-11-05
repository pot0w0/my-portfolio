<script setup lang="ts">
import type { Post, Series } from '~/types/api'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'created', series: Series): void
}>()

const api = useApi()
const { user } = useAuth()

const title = ref('')
const slug = ref('')
const description = ref('')
const cover = ref('')
const introPostId = ref<number | null>(null)

const myPosts = ref<Post[]>([])
const loadingPosts = ref(false)
const saving = ref(false)
const error = ref('')

watch(() => props.open, async (v) => {
  if (!v) return
  title.value = ''
  slug.value = ''
  description.value = ''
  cover.value = ''
  introPostId.value = null
  error.value = ''
  // 拉自己的文章作为介绍文候选
  loadingPosts.value = true
  try {
    if (user.value) {
      const res = await api.get<{ data: Post[] }>(
        '/api/posts',
        { user_id: user.value.id, limit: 100 },
        { silent: true },
      )
      myPosts.value = res.data
    }
  } catch {
    myPosts.value = []
  } finally {
    loadingPosts.value = false
  }
})

// 标题 → 自动 slug（仅英文/数字可转，中文留空手填）
watch(title, (t) => {
  if (slug.value) return
  slug.value = t
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '')
})

async function submit() {
  error.value = ''
  if (!title.value.trim() || !slug.value.trim()) {
    error.value = '标题和 slug 必填'
    return
  }
  saving.value = true
  try {
    const s = await api.post<Series>('/api/series', {
      title: title.value.trim(),
      slug: slug.value.trim(),
      description: description.value,
      cover: cover.value || null,
      intro_post_id: introPostId.value,
    })
    emit('created', s)
    emit('close')
  } catch (e: any) {
    error.value = e?.message ?? '创建失败'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[60] bg-black/50 flex items-center justify-center p-4"
      @click.self="emit('close')"
    >
      <div class="bg-surface border border-border rounded-lg w-full max-w-lg p-5 space-y-4 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between">
          <h3 class="font-semibold text-lg">新建系列</h3>
          <button class="text-faint hover:text-danger" @click="emit('close')">✕</button>
        </div>

        <label class="block">
          <span class="text-sm mb-1 block">标题</span>
          <input v-model="title" class="w-full border border-border rounded px-3 py-2 bg-surface" placeholder="如：Nuxt 从零开始" />
        </label>

        <label class="block">
          <span class="text-sm mb-1 block">slug（URL 标识）</span>
          <input v-model="slug" class="w-full border border-border rounded px-3 py-2 bg-surface font-mono text-sm" placeholder="nuxt-from-scratch" />
        </label>

        <label class="block">
          <span class="text-sm mb-1 block">简介</span>
          <textarea v-model="description" rows="2" class="w-full border border-border rounded px-3 py-2 bg-surface" placeholder="一句话说明这个系列" />
        </label>

        <label class="block">
          <span class="text-sm mb-1 block">封面图 URL（可选）</span>
          <input v-model="cover" class="w-full border border-border rounded px-3 py-2 bg-surface text-sm" placeholder="/static/xxx.png" />
        </label>

        <label class="block">
          <span class="text-sm mb-1 block">介绍文（可选，从我的文章里选一篇）</span>
          <select v-model="introPostId" class="w-full border border-border rounded px-3 py-2 bg-surface text-sm" :disabled="loadingPosts">
            <option :value="null">{{ loadingPosts ? '加载中…' : '不设介绍文' }}</option>
            <option v-for="p in myPosts" :key="p.id" :value="p.id">{{ p.title }}</option>
          </select>
          <span class="text-xs text-faint mt-1 block">
            选中的文章会作为系列首页的"介绍"，它本身仍是一篇独立文章。
          </span>
        </label>

        <p v-if="error" class="text-sm text-danger">{{ error }}</p>

        <div class="flex justify-end gap-2 pt-2 border-t border-border">
          <button class="px-4 py-1.5 border border-border rounded" @click="emit('close')">取消</button>
          <button class="px-4 py-1.5 bg-primary text-white rounded disabled:opacity-50" :disabled="saving" @click="submit">
            {{ saving ? '创建中…' : '创建' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>