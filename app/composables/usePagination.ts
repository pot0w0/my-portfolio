import { computed } from 'vue'

export function usePagination(
  page: Ref<number>,
  limit: Ref<number>,
  total: Ref<number>,
) {
  const totalPages = computed(() =>
    Math.max(1, Math.ceil(total.value / limit.value)),
  )
  const canPrev = computed(() => page.value > 1)
  const canNext = computed(() => page.value < totalPages.value)

  function go(p: number) {
    const clamped = Math.min(Math.max(1, p), totalPages.value)
    page.value = clamped
  }

  return { totalPages, canPrev, canNext, go }
}