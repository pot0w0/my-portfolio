<script setup lang="ts">
import type { Post, PostPayload, Series } from '~/types/api'

const props = defineProps<{ post?: Post | null }>()
const emit = defineEmits<{
  (e: 'saved', post: Post): void
  (e: 'cancel'): void
}>()

const { create, update } = usePosts()
const saving = ref(false)
const saveError = ref('')
const { tags, load } = useTaxonomy()
const { isAdmin } = useAuth()
const api = useApi()

const mediaUrl = useMediaUrl()
const { uploadPostCover, removePostCover, uploadBodyImage } = useUpload()

const title = ref(props.post?.title ?? '')
const content = ref(props.post?.content ?? '')
const preview = ref(false)
const tagIds = ref<number[]>(props.post?.tags?.map(t => t.id) ?? [])
const featured = ref(props.post?.featured ?? false)

const seriesList = ref<Series[]>([])
const seriesId = ref<number | null>(props.post?.series_id ?? null)
const seriesOrder = ref<number | null>(props.post?.series_order ?? null)

// 封面
const coverUrl = ref<string | null>(props.post?.cover ?? null)
const coverFile = ref<File | null>(null)
const coverPreview = ref<string | null>(null)
const coverInput = ref<HTMLInputElement | null>(null)

onMounted(async () => {
  await load()
  try {
    seriesList.value = await api.get<Series[]>('/api/series', undefined, { silent: true })
  } catch { seriesList.value = [] }
})

function suggestOrder() {
  if (!seriesId.value) { seriesOrder.value = null; return }
  const s = seriesList.value.find(x => x.id === seriesId.value)
  seriesOrder.value = (s?.post_count ?? 0) + 1
}
function onSeriesChange() {
  if (seriesId.value) suggestOrder()
  else seriesOrder.value = null
}

function onCoverPick(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (!f) return
  coverFile.value = f
  if (coverPreview.value) URL.revokeObjectURL(coverPreview.value)
  coverPreview.value = URL.createObjectURL(f)
}
function clearCover() {
  coverFile.value = null
  if (coverPreview.value) URL.revokeObjectURL(coverPreview.value)
  coverPreview.value = null
  coverUrl.value = null
}

// 正文图
const bodyImgInput = ref<HTMLInputElement | null>(null)
const uploadingImage = ref(false)
const contentEl = ref<HTMLTextAreaElement | null>(null)

async function onBodyImagePick(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (!f) return
  uploadingImage.value = true
  try {
    const { url } = await uploadBodyImage(f)
    insertAtCursor(`![图片](${mediaUrl(url)})`)
  } catch {} finally {
    uploadingImage.value = false
    if (bodyImgInput.value) bodyImgInput.value.value = ''
  }
}

function insertAtCursor(text: string) {
  const el = contentEl.value
  if (!el) { content.value += `\n${text}\n`; return }
  const start = el.selectionStart ?? content.value.length
  const end = el.selectionEnd ?? content.value.length
  content.value = content.value.slice(0, start) + text + content.value.slice(end)
  nextTick(() => {
    el.focus()
    const pos = start + text.length
    el.setSelectionRange(pos, pos)
  })
}

async function save() {
  if (!title.value.trim() || !content.value.trim()) return
  saving.value = true
  saveError.value = ''
  try {
    const payload: PostPayload = {
      title: title.value.trim(),
      content: content.value,
      tag_ids: tagIds.value,
      featured: featured.value,
      series_id: seriesId.value,
      series_order: seriesId.value ? seriesOrder.value : null,
    }

    // 1. 建/改文章
    let p: Post
    if (props.post) {
      p = await update(props.post.id, payload)
    } else {
      p = await create(payload)
    }

    // 2. 封面：有文件就传，编辑时移除就删
    if (coverFile.value) {
      p = await uploadPostCover(p.id, coverFile.value)
    } else if (props.post?.cover && !coverUrl.value) {
      p = await removePostCover(p.id)
    }

    emit('saved', p)
  } catch (e: any) {
    saveError.value = e?.message ?? '保存失败'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="bg-surface border border-border rounded-lg p-5 space-y-5">
    <div class="flex items-center justify-between">
      <h3 class="font-semibold">{{ post ? '编辑文章' : '写文章' }}</h3>
      <button class="text-sm text-primary hover:underline" type="button" @click="preview = !preview">
        {{ preview ? '返回编辑' : '预览' }}
      </button>
    </div>

    <template v-if="!preview">
      <input v-model="title" placeholder="标题" class="w-full border border-border rounded px-3 py-2 font-medium text-lg bg-surface" />
      <textarea v-model="content" placeholder="正文（支持 Markdown）" rows="14" class="w-full border border-border rounded px-3 py-2 font-mono text-sm bg-surface" />
    </template>
    <div v-else class="border border-border rounded p-5 bg-surface">
      <h1 class="text-2xl font-bold mb-4">{{ title || '（无标题）' }}</h1>
      <div class="prose prose-sm max-w-none"><MDC :value="content || '（无内容）'" /></div>
    </div>

    <!-- 封面选择（新建时先本地预览，保存后上传；编辑时直接上传） -->
    <div v-if="!preview" class="space-y-2">
      <span class="text-xs text-faint">封面图（可选）</span>
      <div class="flex items-center gap-3">
        <div class="w-32 aspect-video rounded border border-border overflow-hidden bg-surface-2">
          <img v-if="coverPreview || coverUrl" :src="coverPreview || mediaUrl(coverUrl)" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex items-center justify-center text-faint text-xs">无封面</div>
        </div>
        <input ref="coverInput" type="file" accept="image/*" class="hidden" @change="onCoverPick" />
        <button type="button" class="px-2 py-1 border border-border rounded text-xs" @click="coverInput?.click()">选择封面</button>
        <button v-if="coverPreview || coverUrl" type="button" class="px-2 py-1 border border-danger text-danger rounded text-xs" @click="clearCover">移除</button>
      </div>
    </div>
    <hr class="border-border" />

    <div class="grid gap-3 md:grid-cols-2">
      <label class="block">
        <span class="text-xs text-faint mb-1 block">系列</span>
        <select v-model="seriesId" class="w-full border border-border rounded px-3 py-2 bg-surface text-sm" @change="onSeriesChange">
          <option :value="null">散篇（不属于系列）</option>
          <option v-for="s in seriesList" :key="s.id" :value="s.id">{{ s.title }}</option>
        </select>
      </label>
      <label v-if="seriesId" class="block">
        <span class="text-xs text-faint mb-1 block">系列内序号</span>
        <input v-model.number="seriesOrder" type="number" min="1" class="w-full border border-border rounded px-3 py-2 bg-surface text-sm" />
      </label>
    </div>

    <div v-if="tags.length" class="space-y-2">
      <h4 class="text-sm font-medium text-muted">标签</h4>
      <div class="flex flex-wrap gap-2">
        <label v-for="t in tags" :key="t.id"
          class="flex items-center gap-1.5 text-sm px-2 py-1 rounded border cursor-pointer"
          :class="tagIds.includes(t.id) ? 'border-primary/40 bg-primary/10 text-primary' : 'border-border text-muted'">
          <input v-model="tagIds" type="checkbox" :value="t.id" class="hidden" />
          #{{ t.name }}
        </label>
      </div>
    </div>

    <div v-if="!preview" class="flex gap-2">
      <input ref="bodyImgInput" type="file" accept="image/*" class="hidden" @change="onBodyImagePick" />
      <button type="button" class="px-2 py-1 border border-border rounded text-xs" @click="bodyImgInput?.click()" :disabled="uploadingImage">
        {{ uploadingImage ? '上传中…' : '插入正文图' }}
      </button>
    </div>

    <label v-if="isAdmin" class="flex items-center gap-2 text-sm">
      <input v-model="featured" type="checkbox" /> 设为精选（首页展示）
    </label>

    <div class="flex gap-2 justify-end pt-2 border-t border-border">
      <button type="button" class="px-4 py-1.5 border border-border rounded hover:bg-surface-2" @click="emit('cancel')">取消</button>
      <button
        type="button"
        class="px-4 py-1.5 bg-primary text-white rounded hover:opacity-90 disabled:opacity-50"
        :disabled="saving || !title.trim() || !content.trim()"
        @click="save"
      >
        {{ saving ? '保存中…' : '保存' }}
      </button>

      <p v-if="saveError" class="text-sm text-danger">{{ saveError }}</p>
    </div>
  </div>
</template>