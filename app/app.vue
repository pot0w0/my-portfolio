<script setup lang="ts">
useHead({
  script: [
    {
      // 在 CSS 加载前同步执行，避免首屏闪烁
      innerHTML: `
        (function(){
          try {
            var t = localStorage.getItem('theme');
            var dark = t === 'dark' ||
              ((!t || t === 'system') &&
               window.matchMedia('(prefers-color-scheme: dark)').matches);
            if (dark) document.documentElement.classList.add('dark');
          } catch(e){}
        })();
      `,
      tagPosition: 'head',
    },
  ],
})

// 客户端初始化（恢复 state + 监听系统变化）
onMounted(() => {
  useTheme().init()
})

// 鼠标
useMouseParallax()
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
  <AppToaster />
</template>