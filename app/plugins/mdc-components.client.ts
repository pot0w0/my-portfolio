import Slider from '~/components/content/Slider.vue'
import SpinningCube from '~/components/content/SpinningCube.vue'
import BouncyBoxes from '~/components/content/BouncyBoxes.vue'
import DragBox from '~/components/content/DragBox.vue'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.component('Slider', Slider)
  nuxtApp.vueApp.component('SpinningCube', SpinningCube)
  nuxtApp.vueApp.component('BouncyBoxes', BouncyBoxes)
  nuxtApp.vueApp.component('DragBox', DragBox)
})