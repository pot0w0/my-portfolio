/**
 * 首屏加载结束：隐藏遮罩，并让页面内容整体淡入。
 * 遮罩何时出现由 app.vue 里的 head 内联脚本负责（超过 1s 才显示），
 * 这里只处理"加载成功"这一侧。
 */
export default defineNuxtPlugin((nuxtApp) => {
  let done = false

  function finish() {
    if (done) return
    done = true

    ;(window as unknown as { __appReady?: boolean }).__appReady = true

    const el = document.getElementById('app-loading')
    if (!el) return

    // 只有遮罩真的出现过才让内容淡入；
    // 快速加载时内容本来就已可见，再淡入一次反而会闪。
    if (el.classList.contains('is-visible')) {
      document.documentElement.classList.add('app-reveal')
    }
    el.classList.remove('is-visible')
  }

  nuxtApp.hook('app:suspense:resolve', finish)
  nuxtApp.hook('app:mounted', finish)
  nuxtApp.hook('app:error', finish)
})
