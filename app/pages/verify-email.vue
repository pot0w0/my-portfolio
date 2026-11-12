<script setup lang="ts">
import type { AuthResponse } from '~/types/api'

const route = useRoute()
const api = useApi()
const { setAuth } = useAuth()

const status = ref<'verifying' | 'ok' | 'error'>('verifying')
const message = ref('')

onMounted(async () => {
  const token = String(route.query.token ?? '').trim()
  if (!token) {
    status.value = 'error'
    message.value = '验证链接缺少令牌'
    return
  }
  try {
    const res = await api.post<AuthResponse>(
      '/api/user/verify-email',
      { token },
      { silent: true },
    )
    setAuth(res.token, res.user)
    status.value = 'ok'
    message.value = `邮箱验证成功，欢迎你，${res.user.username}！`
    setTimeout(() => navigateTo('/'), 1500)
  } catch (e: any) {
    status.value = 'error'
    message.value = e?.message ?? '验证失败'
  }
})
</script>

<template>
  <div class="max-w-sm mx-auto bg-surface border-border rounded-lg p-6 space-y-4 text-center">
    <template v-if="status === 'verifying'">
      <h1 class="text-2xl font-bold">正在验证邮箱…</h1>
      <p class="text-sm text-faint">请稍候</p>
    </template>

    <template v-else-if="status === 'ok'">
      <h1 class="text-2xl font-bold text-emerald-600">验证成功</h1>
      <p class="text-sm text-muted">{{ message }}</p>
      <p class="text-xs text-faint">正在跳转首页…</p>
    </template>

    <template v-else>
      <h1 class="text-2xl font-bold text-danger">验证失败</h1>
      <p class="text-sm text-muted">{{ message }}</p>
      <p class="text-sm">
        <NuxtLink to="/register" class="text-primary hover:underline">重新注册</NuxtLink>
        <span class="text-faint mx-2">·</span>
        <NuxtLink to="/login" class="text-primary hover:underline">去登录</NuxtLink>
      </p>
    </template>
  </div>
</template>
