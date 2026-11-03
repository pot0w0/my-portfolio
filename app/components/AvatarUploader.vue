<script setup lang="ts">
const props = defineProps<{ current?: string | null }>()
const emit = defineEmits<{
  (e: 'uploaded', user: any): void
  (e: 'removed', user: any): void
}>()

const { uploadAvatar, removeAvatar } = useAuth()
const mediaUrl = useMediaUrl()

const fileInput = ref<HTMLInputElement | null>(null)
const preview = ref<string | null>(null)
const pending = ref<File | null>(null)
const busy = ref(false)
const errorMsg = ref('')

function pick() {
  fileInput.value?.click()
}

function onFile(e: Event) {
  errorMsg.value = ''
  const f = (e.target as HTMLInputElement).files?.[0]
  if (!f) return
  if (!['image/png', 'image/jpeg', 'image/webp', 'image/gif'].includes(f.type)) {
    errorMsg.value = '仅支持 png/jpeg/webp/gif'
    return
  }
  if (f.size > 2 * 1024 * 1024) {
    errorMsg.value = '文件不能超过 2MB'
    return
  }
  pending.value = f
  if (preview.value) URL.revokeObjectURL(preview.value)
  preview.value = URL.createObjectURL(f)
}

async function confirm() {
  if (!pending.value) return
  busy.value = true
  errorMsg.value = ''
  try {
    const user = await uploadAvatar(pending.value)
    emit('uploaded', user)
    reset()
  } catch (e: any) {
    errorMsg.value = e?.message ?? '上传失败'
  } finally {
    busy.value = false
  }
}

async function onRemove() {
  busy.value = true
  errorMsg.value = ''
  try {
    const user = await removeAvatar()
    emit('removed', user)
    reset()
  } catch (e: any) {
    errorMsg.value = e?.message ?? '删除失败'
  } finally {
    busy.value = false
  }
}

function reset() {
  if (preview.value) URL.revokeObjectURL(preview.value)
  preview.value = null
  pending.value = null
  if (fileInput.value) fileInput.value.value = ''
}

onBeforeUnmount(() => {
  if (preview.value) URL.revokeObjectURL(preview.value)
})
</script>

<template>
  <div class="flex items-center gap-4">
    <img
      v-if="preview || current"
      :src="preview || mediaUrl(current)"
      class="w-16 h-16 rounded-full object-cover border border-border"
      alt="avatar"
    />
    <div v-else class="w-16 h-16 rounded-full bg-surface-2 flex items-center justify-center text-faint">
      无
    </div>

    <div class="space-y-2">
      <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFile" />
      <div class="flex gap-2">
        <button class="px-3 py-1 border border-border rounded text-sm" @click="pick">
          选择图片
        </button>
        <button
          v-if="pending"
          class="px-3 py-1 bg-primary text-white rounded text-sm disabled:opacity-50"
          :disabled="busy"
          @click="confirm"
        >
          {{ busy ? '上传中…' : '上传' }}
        </button>
        <button
          v-if="pending"
          class="px-3 py-1 border border-border rounded text-sm"
          @click="reset"
        >
          取消
        </button>
        <button
          v-if="current && !pending"
          class="px-3 py-1 border border-danger text-danger rounded text-sm"
          :disabled="busy"
          @click="onRemove"
        >
          删除头像
        </button>
      </div>
      <p v-if="errorMsg" class="text-sm text-danger">{{ errorMsg }}</p>
    </div>
  </div>
</template>