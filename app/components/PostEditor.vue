<script setup lang="ts">
import type { PageOut, Post, PostPayload, Series } from '~/types/api'

const props = defineProps<{
  post?: Post | null
  /** 锁定所属系列（从系列页新建文章时使用） */
  lockSeries?: boolean
  /** 锁定时预置的系列 id */
  presetSeriesId?: number | null
  /** 锁定时预置的系列序号 */
  presetSeriesOrder?: number | null
  /** 锁定时展示的系列标题（系列列表还没加载时用） */
  presetSeriesTitle?: string
}>()
const emit = defineEmits<{
  (e: 'saved', post: Post): void
  (e: 'cancel'): void
}>()

const { create, update } = usePosts()
const { tags, load, createTag } = useTaxonomy()
const { isAdmin } = useAuth()
const { uploadImage } = useUpload()
const api = useApi()
const mediaUrl = useMediaUrl()

const saving = ref(false)
const saveError = ref('')

const title = ref(props.post?.title ?? '')
const content = ref(props.post?.content ?? '')
const preview = ref(false)
const tagIds = ref<number[]>(props.post?.tags?.map(t => t.id) ?? [])
const featured = ref(props.post?.featured ?? false)

const seriesList = ref<Series[]>([])
const seriesId = ref<number | null>(
  props.post?.series_id ?? props.presetSeriesId ?? null,
)
const seriesOrder = ref<number | null>(
  props.post?.series_order ?? props.presetSeriesOrder ?? null,
)

// 状态：已有文章沿用原状态，新文章默认发布
const status = ref<'draft' | 'published'>(
  props.post?.status === 'draft' ? 'draft' : 'published',
)
const lockedSeriesTitle = computed(() =>
  props.presetSeriesTitle
  || seriesList.value.find(s => s.id === seriesId.value)?.title
  || '当前系列',
)

// 封面
const coverUrl = ref<string | null>(props.post?.cover ?? null)
const coverFile = ref<File | null>(null)
const coverPreview = ref<string | null>(null)
const coverInput = ref<HTMLInputElement | null>(null)
const coverRemove = ref(false)
const showCoverPicker = ref(false)

// 标签
const newTagName = ref('')
const creatingTag = ref(false)

// 正文图
const bodyImgInput = ref<HTMLInputElement | null>(null)
const uploadingImage = ref(false)
const contentEl = ref<HTMLTextAreaElement | null>(null)
const showBodyPicker = ref(false)

onMounted(async () => {
  const [, seriesRes] = await Promise.allSettled([
    load(),
    // 后端返回分页结构 { data, total, page, limit }，不是数组
    api.get<PageOut<Series>>('/api/series', { page: 1, limit: 100 }, { silent: true }),
  ])
  if (seriesRes.status === 'fulfilled') seriesList.value = seriesRes.value.data
})

async function suggestOrder() {
  if (!seriesId.value) { seriesOrder.value = null; return }
  const s = seriesList.value.find(x => x.id === seriesId.value)
  // 先用篇数兜底，再按实际最大序号修正（篇数可能小于最大序号）
  seriesOrder.value = (s?.post_count ?? 0) + 1
  if (!s?.slug) return
  try {
    const res = await api.get<{ posts: Post[] }>(
      `/api/series/${s.slug}`,
      undefined,
      { silent: true },
    )
    const maxOrder = res.posts.reduce((m, p) => Math.max(m, p.series_order ?? 0), 0)
    seriesOrder.value = maxOrder + 1
  } catch {}
}
function onSeriesChange() {
  if (seriesId.value) suggestOrder()
  else seriesOrder.value = null
}

// 封面：选文件
function onCoverPick(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (!f) return
  if (!['image/png', 'image/jpeg', 'image/webp', 'image/gif'].includes(f.type)) {
    saveError.value = '封面仅支持 png/jpeg/webp/gif'; return
  }
  if (f.size > 2 * 1024 * 1024) { saveError.value = '封面不能超过 2MB'; return }
  coverFile.value = f
  coverRemove.value = false
  if (coverPreview.value) URL.revokeObjectURL(coverPreview.value)
  coverPreview.value = URL.createObjectURL(f)
  if (coverInput.value) coverInput.value.value = ''
}
// 封面：从池中选
function onCoverPicked(url: string) {
  coverUrl.value = url
  coverFile.value = null
  coverRemove.value = false
  if (coverPreview.value) URL.revokeObjectURL(coverPreview.value)
  coverPreview.value = null
}
function clearCover() {
  coverFile.value = null
  if (coverPreview.value) URL.revokeObjectURL(coverPreview.value)
  coverPreview.value = null
  coverRemove.value = true
}
function undoRemoveCover() { coverRemove.value = false }
onBeforeUnmount(() => { if (coverPreview.value) URL.revokeObjectURL(coverPreview.value) })

// 标签
async function addTag() {
  const name = newTagName.value.trim()
  if (!name) return
  const exist = tags.value.find(t => t.name === name)
  if (exist) {
    if (!tagIds.value.includes(exist.id)) tagIds.value.push(exist.id)
    newTagName.value = ''
    return
  }
  creatingTag.value = true
  try {
    const t = await createTag(name)
    tagIds.value.push(t.id)
    newTagName.value = ''
  } catch {} finally { creatingTag.value = false }
}

// 正文图：从池中选
function onBodyPicked(url: string) {
  insertAtCursor(`![图片](${mediaUrl(url)})`)
}
// 正文图：选文件上传（如果仍保留"直接上传"按钮）
async function onBodyImagePick(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (!f) return
  uploadingImage.value = true
  try {
    const url = await uploadImage(f)
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

async function save(target: 'draft' | 'published' = status.value) {
  // 草稿允许空正文，发布要求正文非空
  if (!title.value.trim()) return
  if (target === 'published' && !content.value.trim()) return
  saving.value = true
  saveError.value = ''
  try {
    let finalCover: string | null | undefined = undefined
    if (coverFile.value) {
      finalCover = await uploadImage(coverFile.value)
    } else if (coverRemove.value) {
      finalCover = null
    }
    // coverPreview 有值但 coverFile 为空 = 从池中选了图，coverUrl 已更新，finalCover 应取 coverUrl
    else if (coverUrl.value) {
      finalCover = coverUrl.value
    }

    const payload: PostPayload = {
      title: title.value.trim(),
      content: content.value,
      tag_ids: tagIds.value,
      featured: featured.value,
      series_id: seriesId.value,
      series_order: seriesId.value ? seriesOrder.value : null,
      status: target,
    }
    if (finalCover !== undefined) payload.cover = finalCover

    const p = props.post
      ? await update(props.post.id, payload)
      : await create(payload)

    status.value = target
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
    <!-- 头部 -->
    <div class="flex items-center justify-between">
      <h3 class="font-semibold flex items-center gap-2">
        {{ post ? '编辑文章' : '写文章' }}
        <span
          v-if="status === 'draft'"
          class="text-xs font-normal px-2 py-0.5 rounded bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300"
        >草稿</span>
      </h3>
      <button class="text-sm text-primary hover:underline" type="button" @click="preview = !preview">
        {{ preview ? '返回编辑' : '预览' }}
      </button>
    </div>

    <!-- 写作区 -->
    <template v-if="!preview">
      <input
        v-model="title"
        placeholder="标题"
        class="w-full border border-border rounded px-3 py-2 font-medium text-lg bg-surface"
      />
      <textarea
        ref="contentEl"
        v-model="content"
        placeholder="正文（支持 Markdown）"
        rows="14"
        class="w-full border border-border rounded px-3 py-2 font-mono text-sm bg-surface"
      />
    </template>
    <div v-else class="border border-border rounded p-5 bg-surface">
      <h1 class="text-2xl font-bold mb-4">{{ title || '（无标题）' }}</h1>
      <div class="prose prose-sm max-w-none"><MDC :value="content || '（无内容）'" /></div>
    </div>

    <!-- 封面 -->
    <div v-if="!preview" class="space-y-2">
      <span class="text-xs text-faint">封面图（可选）</span>
      <div class="flex items-center gap-3 flex-wrap">
        <div class="w-32 aspect-video rounded border border-border overflow-hidden bg-surface-2">
          <img
            v-if="coverPreview || (coverUrl && !coverRemove)"
            :src="coverPreview || mediaUrl(coverUrl)"
            class="w-full h-full object-cover"
            alt=""
          />
          <div v-else class="w-full h-full flex items-center justify-center text-faint text-xs">无封面</div>
        </div>

        <input ref="coverInput" type="file" accept="image/*" class="hidden" @change="onCoverPick" />

        <button
          type="button"
          class="px-2 py-1 border border-border rounded text-xs hover:bg-surface-2"
          @click="showCoverPicker = true"
        >从图片池选</button>
        <button
          type="button"
          class="px-2 py-1 border border-border rounded text-xs hover:bg-surface-2"
          @click="coverInput?.click()"
        >上传新图</button>

        <button
          v-if="coverPreview || (coverUrl && !coverRemove)"
          type="button"
          class="px-2 py-1 border border-danger text-danger rounded text-xs"
          @click="clearCover"
        >移除</button>
        <button
          v-else-if="coverRemove && coverUrl"
          type="button"
          class="px-2 py-1 border border-border rounded text-xs"
          @click="undoRemoveCover"
        >取消移除</button>
      </div>
    </div>
    <hr class="border-border" />

    <!-- 系列 -->
    <div class="grid gap-3 md:grid-cols-2">
      <label class="block">
        <span class="text-xs text-faint mb-1 block">系列</span>
        <div
          v-if="lockSeries"
          class="w-full border border-border rounded px-3 py-2 bg-surface-2 text-sm text-muted"
        >
          系列 · {{ lockedSeriesTitle }}
        </div>
        <select
          v-else
          v-model="seriesId"
          class="w-full border border-border rounded px-3 py-2 bg-surface text-sm"
          @change="onSeriesChange"
        >
          <option :value="null">散篇（不属于系列）</option>
          <option v-for="s in seriesList" :key="s.id" :value="s.id">{{ s.title }}</option>
        </select>
      </label>
      <label v-if="seriesId" class="block">
        <span class="text-xs text-faint mb-1 block">系列内序号</span>
        <input
          v-model.number="seriesOrder"
          type="number"
          min="1"
          class="w-full border border-border rounded px-3 py-2 bg-surface text-sm"
        />
      </label>
    </div>

    <!-- 标签 -->
    <div class="space-y-2">
      <h4 class="text-sm font-medium text-muted">标签</h4>
      <div class="flex flex-wrap gap-2 items-center">
        <label
          v-for="t in tags" :key="t.id"
          class="flex items-center gap-1.5 text-sm px-2 py-1 rounded border cursor-pointer"
          :class="tagIds.includes(t.id) ? 'border-primary/40 bg-primary/10 text-primary' : 'border-border text-muted'"
        >
          <input v-model="tagIds" type="checkbox" :value="t.id" class="hidden" />
          #{{ t.name }}
          <span v-if="t.post_count" class="text-[10px] text-faint">({{ t.post_count }})</span>
        </label>

        <div class="flex items-center gap-1 border border-dashed border-border rounded px-2 py-0.5">
          <span class="text-xs text-faint">#</span>
          <input
            v-model="newTagName"
            placeholder="新标签"
            class="w-20 text-sm bg-transparent outline-none"
            :disabled="creatingTag"
            @keydown.enter.prevent="addTag"
          />
          <button
            type="button"
            class="text-xs text-primary disabled:opacity-50"
            :disabled="creatingTag || !newTagName.trim()"
            @click="addTag"
          >{{ creatingTag ? '…' : '+' }}</button>
        </div>
      </div>
    </div>

    <!-- 正文图 -->
    <div v-if="!preview" class="flex gap-2 flex-wrap">
      <input ref="bodyImgInput" type="file" accept="image/*" class="hidden" @change="onBodyImagePick" />
      <button
        type="button"
        class="px-2 py-1 border border-border rounded text-xs hover:bg-surface-2"
        @click="showBodyPicker = true"
      >从图片池插入</button>
      <button
        type="button"
        class="px-2 py-1 border border-border rounded text-xs hover:bg-surface-2 disabled:opacity-50"
        :disabled="uploadingImage"
        @click="bodyImgInput?.click()"
      >{{ uploadingImage ? '上传中…' : '上传并插入' }}</button>
    </div>

    <!-- 精选（admin） -->
    <label v-if="isAdmin" class="flex items-center gap-2 text-sm">
      <input v-model="featured" type="checkbox" /> 设为精选（首页展示）
    </label>

    <!-- 错误 -->
    <p v-if="saveError" class="text-sm text-danger">{{ saveError }}</p>

    <!-- 操作栏 -->
    <div class="flex gap-2 justify-end pt-2 border-t border-border">
      <button
        type="button"
        class="px-4 py-1.5 border border-border rounded hover:bg-surface-2"
        @click="emit('cancel')"
      >取消</button>
      <button
        type="button"
        class="px-4 py-1.5 border border-border rounded hover:bg-surface-2 disabled:opacity-50"
        :disabled="saving || !title.trim()"
        @click="save('draft')"
      >{{ saving ? '保存中…' : (status === 'draft' ? '保存草稿' : '转为草稿') }}</button>
      <button
        type="button"
        class="px-4 py-1.5 bg-primary text-white rounded hover:opacity-90 disabled:opacity-50"
        :disabled="saving || !title.trim() || !content.trim()"
        @click="save('published')"
      >{{ saving ? '保存中…' : (status === 'draft' ? '发布' : '保存') }}</button>
    </div>

    <!-- 弹窗 -->
    <ImagePickerDialog
      :open="showCoverPicker"
      title="选择封面"
      @close="showCoverPicker = false"
      @picked="onCoverPicked"
    />
    <ImagePickerDialog
      :open="showBodyPicker"
      title="插入正文图"
      @close="showBodyPicker = false"
      @picked="onBodyPicked"
    />
  </div>
</template>