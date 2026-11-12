<script setup lang="ts">
const props = defineProps<{ mode: 'login' | 'register' }>()
const emit = defineEmits<{ (e: 'submitted', payload: any): void }>()
const username = ref('')
const password = ref('')
const email = ref('')
const error = ref('')

function submit() {
  error.value = ''
  if (!username.value || !password.value) { error.value = '用户名和密码必填'; return }
  const payload: any = { username: username.value, password: password.value }
  if (props.mode === 'register') {
    const mail = email.value.trim()
    if (!mail) { error.value = '邮箱必填，用于接收验证邮件'; return }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mail)) { error.value = '邮箱格式不正确'; return }
    payload.email = mail
  }
  emit('submitted', payload)
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <div>
      <label class="block text-sm mb-1">用户名</label>
      <input v-model="username" class="w-full border border-border rounded px-3 py-2 bg-surface" />
    </div>
    <div v-if="mode === 'register'">
      <label class="block text-sm mb-1">邮箱 <span class="text-danger">*</span></label>
      <input
        v-model="email"
        type="email"
        required
        placeholder="用于接收验证邮件"
        class="w-full border border-border rounded px-3 py-2 bg-surface"
      />
    </div>
    <div>
      <label class="block text-sm mb-1">密码</label>
      <input v-model="password" type="password" class="w-full border border-border rounded px-3 py-2 bg-surface" />
    </div>
    <p v-if="error" class="text-sm text-danger">{{ error }}</p>
    <button class="w-full bg-primary text-white rounded py-2 hover:opacity-90">
      {{ mode === 'login' ? '登录' : '注册' }}
    </button>
  </form>
</template>