<script setup lang="ts">
const props = defineProps<{ mode: 'login' | 'register' }>()
const emit = defineEmits<{ (e: 'submitted', payload: any): void }>()

const username = ref('')
const password = ref('')
const email = ref('')
const error = ref('')

function submit() {
  error.value = ''
  if (!username.value || !password.value) {
    error.value = '用户名和密码必填'
    return
  }
  const payload: any = { username: username.value, password: password.value }
  if (props.mode === 'register' && email.value) payload.email = email.value
  emit('submitted', payload)
}

defineExpose({ error })
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <div>
      <label class="block text-sm mb-1">用户名</label>
      <input v-model="username" class="w-full border rounded px-3 py-2" />
    </div>
    <div v-if="mode === 'register'">
      <label class="block text-sm mb-1">邮箱（可选）</label>
      <input v-model="email" type="email" class="w-full border rounded px-3 py-2" />
    </div>
    <div>
      <label class="block text-sm mb-1">密码</label>
      <input v-model="password" type="password" class="w-full border rounded px-3 py-2" />
    </div>
    <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
    <button class="w-full bg-blue-600 text-white rounded py-2 hover:bg-blue-700">
      {{ mode === 'login' ? '登录' : '注册' }}
    </button>
  </form>
</template>