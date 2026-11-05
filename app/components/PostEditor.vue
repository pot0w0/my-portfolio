<script setup lang="ts">
import type { Post, PostPayload } from '~/types/api'

const props = defineProps<{ post?: Post | null }>()
const emit = defineEmits<{
  (e: 'save', payload: PostPayload): void
  (e: 'cancel'): void
}>()

const { categories, tags, load } = useTaxonomy()
const { isAdmin } = useAuth()
onMounted(() => load())

const title = ref(props.post?.title ?? '')
const content = ref(props.post?.content ?? '')
const preview = ref(false)
const categoryId = ref<number | null>(props.post?.category?.id ?? null)
const tagIds = ref<number[]>(props.post?.tags?.map(t => t.id) ?? [])
const featured = ref(props.post?.featured ?? false)

function save() {
  if (!title.value.trim() || !content.value.trim()) return
  emit('save', {
    title: title.value.trim(),
    content: content.value,
    category_id: categoryId.value,
    tag_ids: tagIds.value,
    featured: featured.value,
  })
}
</script>

<template>
  <div class="bg-surface border-border rounded-lg p-5">
    <select v-model.number="categoryId" class="w-full border border-border rounded px-3 py-2 bg-surface">
      <option :value="null">未分类</option>
      <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
    </select>

    <div class="flex flex-wrap gap-2">
      <label v-for="t in tags" :key="t.id" class="flex items-center gap-1 text-sm">
        <input type="checkbox" :value="t.id" v-model="tagIds" />
        {{ t.name }}
      </label>
    </div>

    <label v-if="isAdmin" class="flex items-center gap-2 text-sm">
      <input type="checkbox" v-model="featured" /> 设为精选
    </label>

    <div class="flex items-center justify-between mb-3">
      <h3 class="font-semibold">{{ post ? '编辑文章' : '写文章' }}</h3>
      <button class="text-sm text-primary" @click="preview = !preview">
        {{ preview ? '编辑' : '预览' }}
      </button>
    </div>

    <div v-if="!preview" class="space-y-3">
      <input
        v-model="title"
        placeholder="标题"
        class="w-full border-border rounded px-3 py-2 font-medium"
      />
      <textarea
        v-model="content"
        placeholder="正文（Markdown）"
        rows="12"
        class="w-full border-border rounded px-3 py-2 font-mono text-sm"
      />
    </div>

    <div v-else class="prose prose-sm max-w-none">
      <h1>{{ title || '（无标题）' }}</h1>
      <MDC :value="content || '（无内容）'" />
    </div>

    <div class="flex gap-2 justify-end mt-4">
      <button class="px-3 py-1 border-border rounded" @click="emit('cancel')">取消</button>
      <button class="px-3 py-1 bg-primary text-white rounded" @click="save">
        保存
      </button>
    </div>
  </div>
</template>