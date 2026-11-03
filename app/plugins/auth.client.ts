export default defineNuxtRouteMiddleware(async (to) => {
  const { isLoggedIn, init } = useAuth()
  await init()
  if (!isLoggedIn.value) {
    return navigateTo({ path: '/login', query: { redirect: to.fullPath } })
  }
})