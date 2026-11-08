<script setup lang="ts">
import type { PoolImage } from '~/types/api'

const props = defineProps<{
  open: boolean
  title?: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'picked', url: string): void
}>()

const api = useApi()
const { uploadImage } = useUpload()
const mediaUrl = useMediaUrl()

const images = ref<PoolImage[]>([])
const loading = ref(false)
const uploading = ref(false)
const error = ref('')

const fileInput = ref<HTMLInputElement | null>(null)

async function fetchImages() {
  loading.value = true
  error.value = ''
  try {
    images.value = await api.get<PoolImage[]>('/api/uploads/images', { limit: 60 }, { silent: true })
  } catch (e: any) {
    error.value = e?.message ?? '加载失败'
  } finally {
    loading.value = false
  }
}

watch(() => props.open, (v) => {
  if (v) fetchImages()
})

function pick(url: string) {
  emit('picked', url)
  emit('close')
}

function pickFile() {
  fileInput.value?.click()
}

async function onFilePick(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (!f) return
  uploading.value = true
  error.value = ''
  try {
    const url = await uploadImage(f)
    emit('picked', url)
    emit('close')
  } catch (e: any) {
    error.value = e?.message ?? '上传失败'
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[70] bg-black/50 flex items-center justify-center p-4"
      @click.self="emit('close')"
    >
      <div class="bg-surface border border-border rounded-lg w-full max-w-2xl p-5 space-y-4 max-h-[85vh] flex flex-col">
        <div class="flex items-center justify-between">
          <h3 class="font-semibold text-lg">{{ title || '选择图片' }}</h3>
          <button class="text-faint hover:text-danger" @click="emit('close')">✕</button>
        </div>

        <!-- 上传新图 -->
        <div class="flex items-center gap-2">
          <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFilePick" />
          <button
            class="px-3 py-1.5 border border-border rounded text-sm hover:bg-surface-2 disabled:opacity-50"
            :disabled="uploading"
            @click="pickFile"
          >{{ uploading ? '上传中…' : '上传新图片' }}</button>
          <span class="text-xs text-faint">支持 png/jpeg/webp/gif，≤2MB</span>
        </div>

        <p v-if="error" class="text-sm text-danger">{{ error }}</p>

        <!-- 图片池 -->
        <div class="flex-1 overflow-y-auto min-h-[200px]">
          <p v-if="loading" class="text-sm text-faint">加载中…</p>
          <p v-else-if="!images.length" class="text-sm text-faint">图片池还是空的，上传一张吧</p>
          <div v-else class="grid grid-cols-3 md:grid-cols-4 gap-2">
            <button
              v-for="img in images"
              :key="img.url"
              class="group relative aspect-square rounded border border-border overflow-hidden bg-surface-2 hover:ring-2 hover:ring-primary transition"
              @click="pick(img.url)"
              :title="`${img.filename} · ${formatSize(img.size)}`"
            >
              <img
                :src="mediaUrl(img.url)"
                class="w-full h-full object-cover"
                loading="lazy"
                alt=""
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>