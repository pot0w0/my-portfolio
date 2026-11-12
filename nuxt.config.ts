import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxtjs/mdc'],
  mdc: {
    components: {
      // 代码块改用自定义组件：折叠/展开 + html 运行预览
      map: {
        pre: 'MdcCodeBlock',
      },
    },
  },
  devServer: {
    port: 3001,
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:3000',
    },
  },
  css: ['~/assets/css/main.css'],
  vite: {
    plugins: [tailwindcss()],
  },
})