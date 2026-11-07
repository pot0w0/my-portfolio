<script setup lang="ts">
import type { SearchItem } from '~/types/api'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const router = useRouter()
const api = useApi()

const q = ref('')
const items = ref<SearchItem[]>([])
const postFilters = ref<Record<string, string>>({})
const activeIndex = ref(-1)
const loading = ref(false)
let timer: ReturnType<typeof setTimeout> | null = null

const inputEl = ref<HTMLInputElement | null>(null)

watch(() => props.open, async (v) => {
  if (v) {
    q.value = ''
    items.value = []
    activeIndex.value = -1
    await nextTick()
    inputEl.value?.focus()
  }
})

watch(q, (v) => {
  if (timer) clearTimeout(timer)
  if (!v.trim()) {
    items.value = []
    activeIndex.value = -1
    return
  }
  timer = setTimeout(() => runSearch(v), 200)
})

async function runSearch(kw: string) {
  loading.value = true
  try {
    const res = await api.get<{ items: SearchItem[]; post_filters: Record<string, string> }>(
      '/api/search',
      { q: kw, limit: 12 },
      { silent: true },
    )
    items.value = res.items
    postFilters.value = res.post_filters
    activeIndex.value = res.items.length ? 0 : -1
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeIndex.value = Math.min(activeIndex.value + 1, items.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIndex.value = Math.max(activeIndex.value - 1, 0)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    const item = items.value[activeIndex.value]
    if (item) go(item)
    else goList()
  } else if (e.key === 'Escape') {
    emit('close')
  }
}

function go(item: SearchItem) {
  emit('close')
  router.push(item.url)
}

function goList() {
  emit('close')
  router.push({ path: '/posts', query: postFilters.value })
}

const grouped = computed(() => {
  const map: Record<string, SearchItem[]> = {}
  for (const it of items.value) {
    ;(map[it.type] ||= []).push(it)
  }
  return map
})

const typeLabels: Record<string, string> = {
  post: '文章', series: '系列', tag: '标签', user: '用户',
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[70] bg-black/50 flex items-start justify-center pt-[15vh] px-4"
      @click.self="emit('close')"
    >
      <div class="bg-surface border border-border rounded-lg w-full max-w-xl shadow-2xl overflow-hidden">
        <div class="flex items-center gap-2 px-4 py-3 border-b border-border">
          <span class="text-faint">🔍</span>
          <input
            ref="inputEl"
            v-model="q"
            class="flex-1 bg-transparent outline-none"
            placeholder="搜索文章、系列、标签、用户…（回车查看全部结果）"
            @keydown="onKeydown"
          />
          <button v-if="q" class="text-faint hover:text-text" @click="q = ''">✕</button>
        </div>

        <div class="max-h-[60vh] overflow-y-auto">
          <p v-if="loading" class="px-4 py-3 text-sm text-faint">搜索中…</p>
          <p v-else-if="!items.length" class="px-4 py-3 text-sm text-faint">
            {{ q ? '没有匹配项' : '输入关键词开始搜索' }}
          </p>

          <template v-else>
            <template v-for="(group, type) in grouped" :key="type">
              <p class="px-4 pt-3 pb-1 text-xs text-faint">{{ typeLabels[type] || type }}</p>
              <button
                v-for="it in group"
                :key="`${it.type}-${it.id}`"
                class="w-full text-left px-4 py-2 hover:bg-surface-2 flex items-center justify-between"
                :class="{ 'bg-surface-2': items.indexOf(it) === activeIndex }"
                @click="go(it)"
                @mouseenter="activeIndex = items.indexOf(it)"
              >
                <div class="min-w-0">
                  <p class="truncate">{{ it.title }}</p>
                  <p class="text-xs text-faint truncate">{{ it.subtitle }}</p>
                </div>
                <span class="text-xs text-faint shrink-0 ml-2">↵</span>
              </button>
            </template>

            <button
              class="w-full text-left px-4 py-3 border-t border-border text-sm text-primary hover:bg-surface-2"
              @click="goList"
            >
              查看「{{ q }}」的全部结果 →
            </button>
          </template>
        </div>
      </div>
    </div>
  </Teleport>
</template>