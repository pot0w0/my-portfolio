<script setup lang="ts">
const router = useRouter()
const { register, login } = useAuth()

const error = ref('')

async function onSubmit(payload: any) {
  error.value = ''
  try {
    const res: any = await register(payload)
    // 注册接口若返回 token 则已自动登录；否则用账号密码登一次
    if (!res?.token) {
      await login({ username: payload.username, password: payload.password })
    }
    await router.push('/')
  } catch (e: any) {
    error.value = e?.message ?? '注册失败'
  }
}
</script>

<template>
  <div class="max-w-sm mx-auto bg-surface border-border rounded-lg p-6 space-y-4">
    <h1 class="text-2xl font-bold">注册</h1>
    <AuthForm mode="register" @submitted="onSubmit" />
    <p v-if="error" class="text-sm text-danger">{{ error }}</p>
    <p class="text-sm text-faint">
      已有账号？
      <NuxtLink to="/login" class="text-primary">去登录</NuxtLink>
    </p>
  </div>
</template>