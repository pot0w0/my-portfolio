<script setup lang="ts">
/**
 * 首屏加载遮罩：纯展示层。
 * 显隐由 app.vue 中的 head 内联脚本（1s 延迟显示）和
 * plugins/loading.client.ts（加载完成后隐藏）控制。
 * 默认不可见，SSR 下只是一个透明的空层，不会挡住内容。
 */
</script>

<template>
  <div id="app-loading" role="status" aria-live="polite">
    <div class="flex flex-col items-center gap-4">
      <div class="app-loading__spinner" />
      <p class="text-sm text-muted tracking-widest">加载中…</p>
    </div>
  </div>
</template>
