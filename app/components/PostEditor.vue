<script setup lang="ts">
import type { Post, PostPayload, Series } from '~/types/api'

const props = defineProps<{ post?: Post | null }>()
const emit = defineEmits<{
  (e: 'save', payload: PostPayload): void
  (e: 'cancel'): void
}>()

const { categories, tags, load } = useTaxonomy()
const { isAdmin } = useAuth()
const api = useApi()

const title = ref(props.post?.title ?? '')
const content = ref(props.post?.content ?? '')
const preview = ref(false)

const categoryId = ref<number | null>(props.post?.category?.id ?? null)
const tagIds = ref<number[]>(props.post?.tags?.map(t => t.id) ?? [])
const featured = ref(props.post?.featured ?? false)

const seriesList = ref<Series[]>([])
const seriesId = ref<number | null>(props.post?.series_id ?? null)
const seriesOrder = ref<number | null>(props.post?.series_order ?? null)

onMounted(async () => {
  await load()
  try {
    seriesList.value = await api.get<Series[]>('/api/series', undefined, { silent: true })
  } catch {
    seriesList.value = []
  }

  // 编辑已有系列文章：序号保留；新建且选了系列：默认建议"下一篇"
  if (!props.post && seriesId.value) {
    suggestOrder()
  }
})

// 选了系列后，序号默认取该系列现有最大 order + 1
function suggestOrder() {
  if (!seriesId.value) {
    seriesOrder.value = null
    return
  }
  const s = seriesList.value.find((x) => x.id === seriesId.value)
  const count = s?.post_count ?? 0
  seriesOrder.value = count + 1
}

function onSeriesChange() {
  if (seriesId.value) suggestOrder()
  else seriesOrder.value = null
}

function save() {
  if (!title.value.trim() || !content.value.trim()) return
  emit('save', {
    title: title.value.trim(),
    content: content.value,
    category_id: categoryId.value,
    tag_ids: tagIds.value,
    featured: featured.value,
    series_id: seriesId.value,
    series_order: seriesId.value ? seriesOrder.value : null,
  })
}
</script>

<template>
  <div class="bg-surface border border-border rounded-lg p-5 space-y-5">
    <!-- 头部：标题 + 预览切换 -->
    <div class="flex items-center justify-between">
      <h3 class="font-semibold">{{ post ? '编辑文章' : '写文章' }}</h3>
      <button
        class="text-sm text-primary hover:underline"
        type="button"
        @click="preview = !preview"
      >
        {{ preview ? '返回编辑' : '预览' }}
      </button>
    </div>

    <!-- 写作区：标题 + 正文 / 预览 -->
    <template v-if="!preview">
      <input
        v-model="title"
        placeholder="标题"
        class="w-full border border-border rounded px-3 py-2 font-medium text-lg bg-surface"
      />
      <textarea
        v-model="content"
        placeholder="正文（支持 Markdown）"
        rows="14"
        class="w-full border border-border rounded px-3 py-2 font-mono text-sm bg-surface"
      />
    </template>
    <div v-else class="border border-border rounded p-5 bg-surface">
      <h1 class="text-2xl font-bold mb-4">{{ title || '（无标题）' }}</h1>
      <div class="prose prose-sm max-w-none">
        <MDC :value="content || '（无内容）'" />
      </div>
    </div>

    <!-- 分隔线 -->
    <hr class="border-border" />

    <!-- 归属区 -->
    <div class="space-y-3">
      <h4 class="text-sm font-medium text-muted">归属</h4>

      <div class="grid gap-3 md:grid-cols-2">
        <!-- 分类 -->
        <label class="block">
          <span class="text-xs text-faint mb-1 block">分类</span>
          <select
            v-model="categoryId"
            class="w-full border border-border rounded px-3 py-2 bg-surface text-sm"
          >
            <option :value="null">未分类</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </label>

        <!-- 系列 -->
        <label class="block">
          <span class="text-xs text-faint mb-1 block">系列</span>
          <select
            v-model="seriesId"
            class="w-full border border-border rounded px-3 py-2 bg-surface text-sm"
            @change="onSeriesChange"
          >
            <option :value="null">散篇（不属于系列）</option>
            <option v-for="s in seriesList" :key="s.id" :value="s.id">{{ s.title }}</option>
          </select>
        </label>
      </div>

      <!-- 系列序号：选了系列才显示 -->
      <label v-if="seriesId" class="block md:w-1/2">
        <span class="text-xs text-faint mb-1 block">系列内序号</span>
        <input
          v-model.number="seriesOrder"
          type="number"
          min="1"
          class="w-full border border-border rounded px-3 py-2 bg-surface text-sm"
        />
      </label>
    </div>

    <!-- 标签区 -->
    <div v-if="tags.length" class="space-y-2">
      <h4 class="text-sm font-medium text-muted">标签</h4>
      <div class="flex flex-wrap gap-2">
        <label
          v-for="t in tags"
          :key="t.id"
          class="flex items-center gap-1.5 text-sm px-2 py-1 rounded border cursor-pointer"
          :class="tagIds.includes(t.id)
            ? 'border-primary/40 bg-primary/10 text-primary'
            : 'border-border text-muted'"
        >
          <input v-model="tagIds" type="checkbox" :value="t.id" class="hidden" />
          #{{ t.name }}
        </label>
      </div>
    </div>

    <!-- 高级（admin） -->
    <label v-if="isAdmin" class="flex items-center gap-2 text-sm">
      <input v-model="featured" type="checkbox" />
      设为精选（首页展示）
    </label>

    <!-- 操作栏 -->
    <div class="flex gap-2 justify-end pt-2 border-t border-border">
      <button
        type="button"
        class="px-4 py-1.5 border border-border rounded hover:bg-surface-2"
        @click="emit('cancel')"
      >
        取消
      </button>
      <button
        type="button"
        class="px-4 py-1.5 bg-primary text-white rounded hover:opacity-90 disabled:opacity-50"
        :disabled="!title.trim() || !content.trim()"
        @click="save"
      >
        保存
      </button>
    </div>
  </div>
</template>