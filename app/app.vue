<script setup lang="ts">
useHead({
  script: [
    {
      innerHTML: `(function(){try{var t=localStorage.getItem('theme');var dark=t==='dark'||((!t||t==='system')&&window.matchMedia('(prefers-color-scheme: dark)').matches);if(dark)document.documentElement.classList.add('dark');}catch(e){}})();`,
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