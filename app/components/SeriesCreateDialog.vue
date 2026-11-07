<script setup lang="ts">
import type { Post, Series } from '~/types/api'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'created', series: Series): void
}>()

const api = useApi()
const { user } = useAuth()

// 介绍文来源
const mode = ref<'existing' | 'new'>('existing')
const selectedIntroId = ref<number | null>(null)
const newTitle = ref('')
const newContent = ref('')

const slug = ref('')
const myPosts = ref<Post[]>([])
const loadingPosts = ref(false)
const saving = ref(false)
const error = ref('')

watch(() => props.open, async (v) => {
  if (!v) return
  mode.value = 'existing'
  selectedIntroId.value = null
  newTitle.value = ''
  newContent.value = ''
  slug.value = ''
  error.value = ''
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

const selectedIntro = computed(() =>
  myPosts.value.find(p => p.id === selectedIntroId.value) ?? null,
)

// 最终系列标题 = 选中文章的标题 或 新建介绍文的标题
const finalTitle = computed(() =>
  mode.value === 'existing'
    ? (selectedIntro.value?.title ?? '')
    : newTitle.value.trim(),
)

// 新建介绍文时，标题 → 自动 slug
watch(newTitle, (t) => {
  if (slug.value) return
  slug.value = t
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '')
})

async function submit() {
  error.value = ''
  if (!finalTitle.value) {
    error.value = '介绍文必填（选一篇或新建）'
    return
  }
  if (!slug.value.trim()) {
    error.value = 'slug 必填'
    return
  }

  saving.value = true
  try {
    let introPostId: number

    if (mode.value === 'existing') {
      if (!selectedIntroId.value) {
        error.value = '请选择介绍文'
        saving.value = false
        return
      }
      introPostId = selectedIntroId.value
    } else {
      // 新建介绍文：先 POST /api/posts，正文可空
      const p = await api.post<Post>('/api/posts', {
        title: newTitle.value.trim(),
        content: newContent.value,
        tag_ids: [],
        featured: false,
        series_id: null,
        series_order: null,
      })
      introPostId = p.id
    }

    const s = await api.post<Series>('/api/series', {
      slug: slug.value.trim(),
      description: '',
      intro_post_id: introPostId,
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

        <!-- 介绍文来源切换 -->
        <div class="flex gap-2 text-sm">
          <button
            class="px-3 py-1 rounded border"
            :class="mode === 'existing' ? 'border-primary text-primary' : 'border-border text-muted'"
            @click="mode = 'existing'"
          >选已有文章</button>
          <button
            class="px-3 py-1 rounded border"
            :class="mode === 'new' ? 'border-primary text-primary' : 'border-border text-muted'"
            @click="mode = 'new'"
          >新建介绍文</button>
        </div>

        <!-- 选已有 -->
        <template v-if="mode === 'existing'">
          <label class="block">
            <span class="text-sm mb-1 block">介绍文（必选，标题将作为系列标题）</span>
            <select
              v-model="selectedIntroId"
              class="w-full border border-border rounded px-3 py-2 bg-surface text-sm"
              :disabled="loadingPosts"
            >
              <option :value="null">{{ loadingPosts ? '加载中…' : '请选择…' }}</option>
              <option v-for="p in myPosts" :key="p.id" :value="p.id">{{ p.title }}</option>
            </select>
          </label>
          <p v-if="selectedIntro" class="text-sm text-faint">
            系列标题：<span class="text-text font-medium">{{ selectedIntro.title }}</span>
          </p>
        </template>

        <!-- 新建 -->
        <template v-else>
          <label class="block">
            <span class="text-sm mb-1 block">介绍文标题（= 系列标题）</span>
            <input
              v-model="newTitle"
              class="w-full border border-border rounded px-3 py-2 bg-surface"
              placeholder="如：Nuxt 从零开始"
            />
          </label>
          <label class="block">
            <span class="text-sm mb-1 block">介绍文正文（可空）</span>
            <textarea
              v-model="newContent"
              rows="6"
              class="w-full border border-border rounded px-3 py-2 bg-surface font-mono text-sm"
              placeholder="Markdown，可留空"
            />
          </label>
        </template>

        <label class="block">
          <span class="text-sm mb-1 block">slug（URL 标识）</span>
          <input
            v-model="slug"
            class="w-full border border-border rounded px-3 py-2 bg-surface font-mono text-sm"
            placeholder="nuxt-from-scratch"
          />
        </label>

        <p v-if="error" class="text-sm text-danger">{{ error }}</p>

        <div class="flex justify-end gap-2 pt-2 border-t border-border">
          <button class="px-4 py-1.5 border border-border rounded" @click="emit('close')">取消</button>
          <button
            class="px-4 py-1.5 bg-primary text-white rounded disabled:opacity-50"
            :disabled="saving"
            @click="submit"
          >
            {{ saving ? '创建中…' : '创建' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>