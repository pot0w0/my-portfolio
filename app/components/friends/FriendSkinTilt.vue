<script setup lang="ts">
import type { FriendLink } from '~/types/api'

defineProps<{ friend: FriendLink }>()
const mediaUrl = useMediaUrl()

const el = ref<HTMLElement | null>(null)
const styleObj = ref<Record<string, string>>({})

function onMove(e: MouseEvent) {
  if (!el.value) return
  const r = el.value.getBoundingClientRect()
  const x = (e.clientX - r.left) / r.width - 0.5
  const y = (e.clientY - r.top) / r.height - 0.5
  styleObj.value = {
    transform: `perspective(700px) rotateX(${-y * 12}deg) rotateY(${x * 12}deg) scale(1.03)`,
    '--mx': `${(x + 0.5) * 100}%`,
    '--my': `${(y + 0.5) * 100}%`,
  }
}
function onLeave() {
  styleObj.value = { transform: 'perspective(700px) rotateX(0) rotateY(0) scale(1)' }
}
</script>

<template>
  <a
    ref="el"
    :href="friend.url"
    target="_blank"
    rel="noopener"
    class="tilt-card block relative rounded-lg p-4 border border-border bg-surface overflow-hidden"
    :style="{ ...styleObj, '--c': friend.theme_color }"
    @mousemove="onMove"
    @mouseleave="onLeave"
  >
    <span class="glare" aria-hidden="true" />
    <div class="relative flex items-center gap-3">
      <img
        v-if="friend.avatar"
        :src="mediaUrl(friend.avatar)"
        class="w-12 h-12 rounded-full object-cover border border-border shrink-0"
        alt=""
      />
      <div
        v-else
        class="w-12 h-12 rounded-full shrink-0 flex items-center justify-center font-bold text-white"
        :style="{ background: friend.theme_color }"
      >
        {{ friend.name[0]?.toUpperCase() }}
      </div>
      <div class="min-w-0 flex-1">
        <p class="font-medium truncate" :style="{ color: friend.theme_color }">
          {{ friend.name }}
        </p>
        <p class="text-xs text-faint truncate">{{ friend.description }}</p>
      </div>
    </div>
  </a>
</template>

<style scoped>
.tilt-card {
  transform-style: preserve-3d;
  transition: transform .15s ease-out, box-shadow .2s;
  will-change: transform;
}
.tilt-card:hover {
  box-shadow: 0 12px 30px -8px color-mix(in srgb, var(--c) 50%, transparent);
}
.glare {
  position: absolute; inset: 0;
  background: radial-gradient(circle at var(--mx, 50%) var(--my, 50%),
    rgba(255,255,255,.3), transparent 45%);
  opacity: 0; transition: opacity .2s; pointer-events: none;
}
.tilt-card:hover .glare { opacity: 1; }
</style>