<script setup lang="ts">
const { user, isLoggedIn, logout } = useAuth()
const router = useRouter()
const { isDark, toggleWithTransition } = useTheme()

async function onLogout() {
  await logout()
  await router.push('/')
}
</script>


<template>
  <div class="min-h-screen flex flex-col">
    <header class="border-border dark:border-slate-700-b bg-surface dark:bg-slate-800">
      <div class="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
        <NuxtLink to="/" class="font-bold text-lg dark:text-slate-300">Portfolio</NuxtLink>
        <nav class="flex items-center gap-4 text-sm">
          <NuxtLink to="/" class="hover:text-blue-600 dark:text-slate-300">首页</NuxtLink>
          <NuxtLink to="/posts" class="hover:text-blue-600 dark:text-slate-300">博客</NuxtLink>
          <template v-if="isLoggedIn">
            <NuxtLink to="/posts" class="hover:text-blue-600 dark:text-slate-300">写文章</NuxtLink>
            <NuxtLink :to="`/user/${user!.id}`" class="hover:text-blue-600 dark:text-slate-300">
              {{ user!.username }}
            </NuxtLink>
            <NuxtLink to="/user" class="hover:text-blue-600 dark:text-orange-300">我的</NuxtLink>
            <button
              class="text-blue-600 dark:text-red-300 hover:text-green-600 dark:hover:text-orange-600"
              :title="isDark ? '切换到日间' : '切换到夜间'"
              @click="toggleWithTransition($event)"
            >
              {{ isDark ? '日️' : '月' }}
            </button>
            <button class="text-faint dark:text-state-300 hover:text-red-600" @click="onLogout">
              登出
            </button>
          </template>
          <template v-else>
            <NuxtLink to="/login" class="hover:text-blue-600 dark:text-slate-300">登录</NuxtLink>
            <NuxtLink to="/register" class="hover:text-blue-600 dark:text-slate-300">注册</NuxtLink>
          </template>
        </nav>
      </div>
    </header>

    <main class="flex-1 max-w-4xl w-full mx-auto px-4 py-8">
      <slot />
    </main>

    <footer class="border-border dark:border-slate-700-t bg-surface dark:bg-slate-800 dark:border">
      <div class="max-w-4xl mx-auto px-4 py-4 text-sm text-faint dark:text-slate-500">
        © {{ new Date().getFullYear() }} Portfolio
      </div>
    </footer>
  </div>
</template>