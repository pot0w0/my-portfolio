<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const { login } = useAuth()

const error = ref('')
const submitting = ref(false)

async function onSubmit(payload: any) {
  error.value = ''
  submitting.value = true
  try {
    await login(payload)
    const redirect = (route.query.redirect as string) || '/'
    await router.push(redirect)
  } catch (e: any) {
    error.value = e?.message ?? '登录失败'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="max-w-sm mx-auto bg-white border rounded-lg p-6 space-y-4">
    <h1 class="text-2xl font-bold">登录</h1>
    <AuthForm mode="login" @submitted="onSubmit" />
    <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
    <p class="text-sm text-slate-500">
      还没有账号？
      <NuxtLink to="/register" class="text-blue-600">去注册</NuxtLink>
    </p>
  </div>
</template>