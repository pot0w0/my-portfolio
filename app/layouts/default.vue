<script setup lang="ts">
const { user, isLoggedIn, logout } = useAuth()
const router = useRouter()

async function onLogout() {
  await logout()
  await router.push('/')
}
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <header class="border-b bg-white">
      <div class="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
        <NuxtLink to="/" class="font-bold text-lg">Portfolio</NuxtLink>
        <nav class="flex items-center gap-4 text-sm">
          <NuxtLink to="/" class="hover:text-blue-600">首页</NuxtLink>
          <NuxtLink to="/posts" class="hover:text-blue-600">博客</NuxtLink>
          <template v-if="isLoggedIn">
            <NuxtLink to="/posts" class="text-blue-600">写文章</NuxtLink>
            <NuxtLink :to="`/user/${user!.id}`" class="hover:text-blue-600">
              {{ user!.username }}
            </NuxtLink>
            <NuxtLink to="/user" class="hover:text-blue-600">我的</NuxtLink>
            <button class="text-slate-500 hover:text-red-600" @click="onLogout">
              登出
            </button>
          </template>
          <template v-else>
            <NuxtLink to="/login" class="hover:text-blue-600">登录</NuxtLink>
            <NuxtLink to="/register" class="hover:text-blue-600">注册</NuxtLink>
          </template>
        </nav>
      </div>
    </header>

    <main class="flex-1 max-w-4xl w-full mx-auto px-4 py-8">
      <slot />
    </main>

    <footer class="border-t bg-white">
      <div class="max-w-4xl mx-auto px-4 py-4 text-sm text-slate-500">
        © {{ new Date().getFullYear() }} Portfolio
      </div>
    </footer>
  </div>
</template>