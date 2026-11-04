<script setup lang="ts">
const { user, isLoggedIn, logout } = useAuth()
const { hidden, show } = useAutoHideHeader({ topZone: 60 })
const { isDark, toggleWithTransition } = useTheme()
const router = useRouter()
const route = useRoute()

async function onLogout() {
  await logout()
  await router.push('/')
}

// 路由变化时顶栏复位显示
watch(() => route.fullPath, () => show())

// 桌面端：鼠标进入顶部热区就显示
function onMouseMove(e: MouseEvent) {
  if (e.clientY <= 60) show()
}
onMounted(() => {
  if (window.matchMedia('(hover: hover)').matches) {
    window.addEventListener('mousemove', onMouseMove, { passive: true })
  }
})
onBeforeUnmount(() => {
  window.removeEventListener('mousemove', onMouseMove)
})
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <header
      class="fixed top-0 inset-x-0 z-40 border-b border-border bg-surface/90 backdrop-blur
             transition-transform duration-300 will-change-transform"
      :class="hidden ? '-translate-y-full' : 'translate-y-0'"
    >
      <div class="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
        <NuxtLink to="/" class="font-bold text-lg">Portfolio</NuxtLink>
        <nav class="flex items-center gap-4 text-sm">
          <NuxtLink to="/" class="hover:text-primary">首页</NuxtLink>
          <NuxtLink to="/posts" class="hover:text-primary">博客</NuxtLink>
          <template v-if="isLoggedIn">
            <NuxtLink to="/posts" class="hover:text-primary">写文章</NuxtLink>
            <NuxtLink :to="`/user/${user!.id}`" class="hover:text-primary">
              {{ user!.username }}
            </NuxtLink>
            <NuxtLink to="/user" class="hover:text-primary">我的</NuxtLink>
            <button class="text-faint hover:text-danger" @click="onLogout">登出</button>
          </template>
          <template v-else>
            <NuxtLink to="/login" class="hover:text-primary">登录</NuxtLink>
            <NuxtLink to="/register" class="hover:text-primary">注册</NuxtLink>
          </template>
          <button
            class="text-primary hover:opacity-80"
            :title="isDark ? '切换到日间' : '切换到夜间'"
            @click="toggleWithTransition($event)"
          >
            {{ isDark ? '☀️' : '🌙' }}
          </button>
        </nav>
      </div>
    </header>

    <!-- pt-20 = 给 fixed header 留位（h-14=56px + 间距） -->
    <main class="flex-1 max-w-4xl w-full mx-auto px-4 pt-20 pb-8">
      <slot />
    </main>

    <footer class="border-t border-border bg-surface">
      <div class="max-w-4xl mx-auto px-4 py-4 text-sm text-faint">
        © {{ new Date().getFullYear() }} Portfolio
      </div>
    </footer>
  </div>
</template>