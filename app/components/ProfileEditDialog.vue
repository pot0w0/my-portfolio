<script setup lang="ts">
import type { User } from '~/types/api'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'updated', user: User): void
}>()

const { user, updateProfile, uploadAvatar, removeAvatar } = useAuth()
const mediaUrl = useMediaUrl()

// 表单字段
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

// 头像
const fileInput = ref<HTMLInputElement | null>(null)
const avatarPreview = ref<string | null>(null)
const avatarFile = ref<File | null>(null)
const avatarBusy = ref(false)
const avatarRemove = ref(false)   // 标记"移除头像"

const saving = ref(false)
const error = ref('')

// 打开时初始化
watch(() => props.open, (v) => {
  if (!v) return
  username.value = user.value?.username ?? ''
  email.value = user.value?.email ?? ''
  password.value = ''
  confirmPassword.value = ''
  avatarFile.value = null
  avatarRemove.value = false
  if (avatarPreview.value) URL.revokeObjectURL(avatarPreview.value)
  avatarPreview.value = null
  error.value = ''
})

function pickAvatar() { fileInput.value?.click() }

function onAvatarPick(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (!f) return
  if (!['image/png', 'image/jpeg', 'image/webp', 'image/gif'].includes(f.type)) {
    error.value = '头像仅支持 png/jpeg/webp/gif'; return
  }
  if (f.size > 2 * 1024 * 1024) { error.value = '头像不能超过 2MB'; return }
  avatarFile.value = f
  avatarRemove.value = false
  if (avatarPreview.value) URL.revokeObjectURL(avatarPreview.value)
  avatarPreview.value = URL.createObjectURL(f)
}

function clearAvatar() {
  avatarFile.value = null
  if (avatarPreview.value) URL.revokeObjectURL(avatarPreview.value)
  avatarPreview.value = null
  avatarRemove.value = true
}

onBeforeUnmount(() => { if (avatarPreview.value) URL.revokeObjectURL(avatarPreview.value) })

async function submit() {
  error.value = ''
  if (!username.value.trim()) { error.value = '用户名不能为空'; return }
  if (password.value && password.value.length < 6) { error.value = '密码至少 6 位'; return }
  if (password.value && password.value !== confirmPassword.value) {
    error.value = '两次密码不一致'; return
  }

  saving.value = true
  try {
    // 1. 更新基本信息（用户名/邮箱/密码）
    const payload: any = { username: username.value.trim() }
    payload.email = email.value.trim() || null
    if (password.value) payload.password = password.value
    let updated = await updateProfile(payload)

    // 2. 头像：有文件就传，标记移除就删
    if (avatarFile.value) {
      avatarBusy.value = true
      updated = await uploadAvatar(avatarFile.value)
    } else if (avatarRemove.value && user.value?.avatar) {
      updated = await removeAvatar()
    }

    emit('updated', updated)
    emit('close')
  } catch (e: any) {
    error.value = e?.message ?? '保存失败'
  } finally {
    saving.value = false
    avatarBusy.value = false
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
      <div class="bg-surface border border-border rounded-lg w-full max-w-md p-5 space-y-4 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between">
          <h3 class="font-semibold text-lg">编辑资料</h3>
          <button class="text-faint hover:text-danger" @click="emit('close')">✕</button>
        </div>

        <!-- 头像 -->
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-full overflow-hidden border border-border bg-surface-2 shrink-0">
            <img
              v-if="avatarPreview || (user?.avatar && !avatarRemove)"
              :src="avatarPreview || mediaUrl(user?.avatar)"
              class="w-full h-full object-cover"
              alt=""
            />
            <div v-else class="w-full h-full flex items-center justify-center text-faint text-xs">
              无
            </div>
          </div>
          <div class="flex flex-col gap-1.5">
            <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onAvatarPick" />
            <button type="button" class="px-3 py-1 border border-border rounded text-sm hover:bg-surface-2" @click="pickAvatar">
              更换头像
            </button>
            <button
              v-if="avatarPreview || (user?.avatar && !avatarRemove)"
              type="button"
              class="px-3 py-1 border border-danger text-danger rounded text-sm"
              @click="clearAvatar"
            >
              移除头像
            </button>
          </div>
        </div>

        <!-- 用户名 -->
        <label class="block">
          <span class="text-sm mb-1 block">用户名</span>
          <input v-model="username" class="w-full border border-border rounded px-3 py-2 bg-surface" />
        </label>

        <!-- 邮箱 -->
        <label class="block">
          <span class="text-sm mb-1 block">邮箱（可选）</span>
          <input v-model="email" type="email" class="w-full border border-border rounded px-3 py-2 bg-surface" />
        </label>

        <hr class="border-border" />

        <!-- 改密码 -->
        <p class="text-xs text-faint">不修改密码可留空</p>
        <label class="block">
          <span class="text-sm mb-1 block">新密码</span>
          <input v-model="password" type="password" class="w-full border border-border rounded px-3 py-2 bg-surface" placeholder="至少 6 位" />
        </label>
        <label class="block">
          <span class="text-sm mb-1 block">确认新密码</span>
          <input v-model="confirmPassword" type="password" class="w-full border border-border rounded px-3 py-2 bg-surface" />
        </label>

        <p v-if="error" class="text-sm text-danger">{{ error }}</p>

        <div class="flex justify-end gap-2 pt-2 border-t border-border">
          <button class="px-4 py-1.5 border border-border rounded" @click="emit('close')">取消</button>
          <button
            class="px-4 py-1.5 bg-primary text-white rounded disabled:opacity-50"
            :disabled="saving"
            @click="submit"
          >
            {{ saving ? '保存中…' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>