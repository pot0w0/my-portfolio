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
    {
      // 首屏加载遮罩：从导航开始计时，超过 1s 才显示（避免快速加载时闪一下）。
      // 隐藏与淡入由 plugins/loading.client.ts 在加载完成后处理。
      innerHTML: `(function(){try{
        function show(){if(window.__appReady)return;var el=document.getElementById('app-loading');if(el)el.classList.add('is-visible');}
        var delay=1000-performance.now();
        if(delay>0){setTimeout(show,delay);}else{show();}
        document.addEventListener('DOMContentLoaded',function(){if(performance.now()>=1000)show();});
        // 兜底：JS 始终加载失败时，20s 后也要把页面放出来
        setTimeout(function(){if(window.__appReady)return;window.__appReady=true;var el=document.getElementById('app-loading');if(el){if(el.classList.contains('is-visible'))document.documentElement.classList.add('app-reveal');el.classList.remove('is-visible');}},20000);
      }catch(e){}})();`,
      tagPosition: 'head',
    },
  ],
})
onMounted(() => { useTheme().init() })
</script>

<template>
  <div id="app-content">
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
  <AppToaster />
  <AppLoading />
</template>