<script setup lang="ts">
import type { RegisterResponse } from '~/types/api'

const { register } = useAuth()
const api = useApi()

const error = ref('')
const sentTo = ref('')
const resending = ref(false)
const resendMsg = ref('')

async function onSubmit(payload: any) {
  error.value = ''
  resendMsg.value = ''
  try {
    const res = await register(payload)
    sentTo.value = res.email || payload.email
  } catch (e: any) {
    error.value = e?.message ?? '注册失败'
  }
}

async function resend() {
  if (!sentTo.value) return
  resending.value = true
  resendMsg.value = ''
  error.value = ''
  try {
    const res = await api.post<RegisterResponse>(
      '/api/user/resend-verification',
      { email: sentTo.value },
      { silent: true },
    )
    resendMsg.value = res.message
  } catch (e: any) {
    error.value = e?.message ?? '发送失败'
  } finally {
    resending.value = false
  }
}
</script>

<template>
  <div class="max-w-sm mx-auto bg-surface border-border rounded-lg p-6 space-y-4">
    <template v-if="sentTo">
      <h1 class="text-2xl font-bold">验证邮箱</h1>
      <p class="text-sm text-muted leading-relaxed">
        注册成功。验证邮件已发送到
        <strong class="text-text">{{ sentTo }}</strong>，
        请点击邮件中的链接完成验证后才能登录。
      </p>
      <p class="text-xs text-faint">
        没收到？请检查垃圾邮件；也可以
        <button
          class="text-primary hover:underline disabled:opacity-50"
          :disabled="resending"
          @click="resend"
        >{{ resending ? '发送中…' : '重新发送验证邮件' }}</button>。
      </p>
      <p v-if="resendMsg" class="text-sm text-emerald-600">{{ resendMsg }}</p>
      <p v-if="error" class="text-sm text-danger">{{ error }}</p>
      <p class="text-sm text-faint">
        已点过邮件里的链接？
        <NuxtLink to="/login" class="text-primary">去登录</NuxtLink>
      </p>
    </template>

    <template v-else>
      <h1 class="text-2xl font-bold">注册</h1>
      <AuthForm mode="register" @submitted="onSubmit" />
      <p v-if="error" class="text-sm text-danger">{{ error }}</p>
      <p class="text-sm text-faint">
        已有账号？
        <NuxtLink to="/login" class="text-primary">去登录</NuxtLink>
      </p>
    </template>
  </div>
</template>
