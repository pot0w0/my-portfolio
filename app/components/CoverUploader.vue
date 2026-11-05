<script setup lang="ts">
import type { Series } from '~/types/api'

const props = defineProps<{ seriesId: number; current?: string | null }>()
const emit = defineEmits<{
  (e: 'updated', series: Series): void
  (e: 'removed', series: Series): void
}>()

const { uploadSeriesCover, removeSeriesCover } = useUpload()
const mediaUrl = useMediaUrl()

const fileInput = ref<HTMLInputElement | null>(null)
const preview = ref<string | null>(null)
const pending = ref<File | null>(null)
const busy = ref(false)
const errorMsg = ref('')

function pick() { fileInput.value?.click() }

function onFile(e: Event) {
  errorMsg.value = ''
  const f = (e.target as HTMLInputElement).files?.[0]
  if (!f) return
  if (!['image/png','image/jpeg','image/webp','image/gif'].includes(f.type)) {
    errorMsg.value = '仅支持 png/jpeg/webp/gif'; return
  }
  if (f.size > 2 * 1024 * 1024) { errorMsg.value = '文件不能超过 2MB'; return }
  pending.value = f
  if (preview.value) URL.revokeObjectURL(preview.value)
  preview.value = URL.createObjectURL(f)
}

async function confirm() {
  if (!pending.value) return
  busy.value = true
  try {
    const s = await uploadSeriesCover(props.seriesId, pending.value)
    emit('updated', s)
    reset()
  } catch {} finally { busy.value = false }
}

async function onRemove() {
  busy.value = true
  try {
    const s = await removeSeriesCover(props.seriesId)
    emit('removed', s)
    reset()
  } catch {} finally { busy.value = false }
}

function reset() {
  if (preview.value) URL.revokeObjectURL(preview.value)
  preview.value = null
  pending.value = null
  if (fileInput.value) fileInput.value.value = ''
}
onBeforeUnmount(() => { if (preview.value) URL.revokeObjectURL(preview.value) })
</script>

<template>
  <div class="space-y-2">
    <div class="aspect-video bg-surface-2 rounded border border-border overflow-hidden">
      <img v-if="preview || current" :src="preview || mediaUrl(current)" class="w-full h-full object-cover" alt="" />
      <div v-else class="w-full h-full flex items-center justify-center text-faint text-sm">无封面</div>
    </div>
    <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFile" />
    <div class="flex gap-2 flex-wrap">
      <button class="px-3 py-1 border border-border rounded text-sm hover:bg-surface-2" @click="pick">选择封面</button>
      <button v-if="pending" class="px-3 py-1 bg-primary text-white rounded text-sm disabled:opacity-50" :disabled="busy" @click="confirm">
        {{ busy ? '上传中…' : '上传' }}
      </button>
      <button v-if="pending" class="px-3 py-1 border border-border rounded text-sm" @click="reset">取消</button>
      <button v-if="current && !pending" class="px-3 py-1 border border-danger text-danger rounded text-sm" :disabled="busy" @click="onRemove">删除封面</button>
    </div>
    <p v-if="errorMsg" class="text-sm text-danger">{{ errorMsg }}</p>
  </div>
</template>