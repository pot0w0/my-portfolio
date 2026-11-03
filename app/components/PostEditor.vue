<script setup lang="ts">
import type { Post } from '~/types/api'

const props = defineProps<{ post?: Post | null }>()
const emit = defineEmits<{
  (e: 'save', payload: { title: string; content: string }): void
  (e: 'cancel'): void
}>()

const title = ref(props.post?.title ?? '')
const content = ref(props.post?.content ?? '')
const preview = ref(false)

function save() {
  if (!title.value.trim() || !content.value.trim()) return
  emit('save', { title: title.value.trim(), content: content.value })
}
</script>

<template>
  <div class="bg-white border rounded-lg p-5">
    <div class="flex items-center justify-between mb-3">
      <h3 class="font-semibold">{{ post ? '编辑文章' : '写文章' }}</h3>
      <button class="text-sm text-blue-600" @click="preview = !preview">
        {{ preview ? '编辑' : '预览' }}
      </button>
    </div>

    <div v-if="!preview" class="space-y-3">
      <input
        v-model="title"
        placeholder="标题"
        class="w-full border rounded px-3 py-2 font-medium"
      />
      <textarea
        v-model="content"
        placeholder="正文（Markdown）"
        rows="12"
        class="w-full border rounded px-3 py-2 font-mono text-sm"
      />
    </div>

    <div v-else class="prose prose-sm max-w-none">
      <h1>{{ title || '（无标题）' }}</h1>
      <MDC :value="content || '（无内容）'" />
    </div>

    <div class="flex gap-2 justify-end mt-4">
      <button class="px-3 py-1 border rounded" @click="emit('cancel')">取消</button>
      <button class="px-3 py-1 bg-blue-600 text-white rounded" @click="save">
        保存
      </button>
    </div>
  </div>
</template>