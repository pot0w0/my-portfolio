<script setup lang="ts">
useHead({
  script: [
    {
      innerHTML: `(function(){try{var t=localStorage.getItem('theme');var dark=t==='dark'||((!t||t==='system')&&window.matchMedia('(prefers-color-scheme: dark)').matches);if(dark)document.documentElement.classList.add('dark');}catch(e){}})();`,
      tagPosition: 'head',
    },
    {
      // 首帧前随机挑一张背景图，避免先渲染默认图再切换的闪烁
      innerHTML: `(function(){try{var b=['/bg0.png','/bg1.jpg','/bg2.png'];var p=b[Math.floor(Math.random()*b.length)];document.documentElement.style.setProperty('--bg-image',"url('"+p+"')");}catch(e){}})();`,
      tagPosition: 'head',
    },
  ],
})
onMounted(() => { useTheme().init() })
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
  <AppToaster />
</template>