<script setup lang="ts">
const props = defineProps<{ content: string }>()

interface Part {
  text: string
  mention?: string
}

// @用户名 → 指向用户主页的超链接
// 支持字母/数字/下划线/中划线/中文；建议用户名后跟空格或标点
const MENTION_RE = /@([A-Za-z0-9_\-一-鿿]+)/g

const parts = computed<Part[]>(() => {
  const text = props.content ?? ''
  const out: Part[] = []
  let last = 0
  let m: RegExpExecArray | null
  MENTION_RE.lastIndex = 0
  while ((m = MENTION_RE.exec(text))) {
    // 排除邮箱这类 "a@b.com"：@ 前是字母/数字/下划线时不当作提及
    const prev = m.index > 0 ? text[m.index - 1] : ''
    if (prev && /[A-Za-z0-9_]/.test(prev)) continue

    if (m.index > last) out.push({ text: text.slice(last, m.index) })
    out.push({ text: m[0], mention: m[1] })
    last = m.index + m[0].length
  }
  if (last < text.length) out.push({ text: text.slice(last) })
  return out
})
</script>

<template>
  <p class="text-sm text-muted whitespace-pre-wrap">
    <template v-for="(part, i) in parts" :key="i">
      <NuxtLink
        v-if="part.mention"
        :to="`/user/${encodeURIComponent(part.mention)}`"
        class="text-primary hover:underline"
      >{{ part.text }}</NuxtLink>
      <template v-else>{{ part.text }}</template>
    </template>
  </p>
</template>
