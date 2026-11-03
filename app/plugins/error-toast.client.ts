export default defineNuxtPlugin((nuxtApp) => {
  const toast = useToast()

  nuxtApp.vueApp.config.errorHandler = (err: any) => {
    console.error(err)
    toast.error(err?.message ?? '发生未知错误')
  }

  window.addEventListener('unhandledrejection', (e) => {
    // 避免和 useApi 重复弹：useApi 抛的是普通对象 {status,message}
    const reason = e.reason
    if (reason && typeof reason === 'object' && 'status' in reason) return
    toast.error(reason?.message ?? '请求异常')
  })
})