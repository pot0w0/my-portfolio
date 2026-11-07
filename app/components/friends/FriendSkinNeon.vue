<script setup lang="ts">
import type { FriendLink } from '~/types/api'

defineProps<{ friend: FriendLink }>()
const mediaUrl = useMediaUrl()
</script>

<template>
  <a
    :href="friend.url"
    target="_blank"
    rel="noopener"
    class="neon-card group block relative rounded-lg p-4 bg-[#0b0f1a] overflow-hidden"
    :style="{ '--c': friend.theme_color }"
  >
    <!-- 流光边框 -->
    <span class="neon-border" aria-hidden="true" />
    <!-- 呼吸光晕 -->
    <span class="neon-glow" aria-hidden="true" />

    <div class="relative flex items-center gap-3">
      <img
        v-if="friend.avatar"
        :src="mediaUrl(friend.avatar)"
        class="w-12 h-12 rounded-full object-cover ring-2 shrink-0"
        :style="{ boxShadow: `0 0 12px ${friend.theme_color}` }"
        alt=""
      />
      <div
        v-else
        class="w-12 h-12 rounded-full shrink-0 flex items-center justify-center font-bold text-white"
        :style="{ background: friend.theme_color, boxShadow: `0 0 16px ${friend.theme_color}` }"
      >
        {{ friend.name[0]?.toUpperCase() }}
      </div>
      <div class="min-w-0 flex-1">
        <p
          class="font-semibold truncate"
          :style="{ color: friend.theme_color, textShadow: `0 0 8px ${friend.theme_color}` }"
        >{{ friend.name }}</p>
        <p class="text-xs text-slate-300/70 truncate">{{ friend.description }}</p>
      </div>
    </div>
  </a>
</template>

<style scoped>
.neon-card { color: white; }
.neon-border {
  position: absolute; inset: 0; border-radius: inherit; padding: 1px;
  background: linear-gradient(120deg,
    transparent 20%,
    var(--c) 40%,
    transparent 60%,
    var(--c) 80%,
    transparent 100%);
  background-size: 200% 200%;
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
          mask-composite: exclude;
  animation: neon-flow 4s linear infinite;
  opacity: .7;
}
.neon-glow {
  position: absolute; inset: -20%;
  background: radial-gradient(circle at 50% 50%, var(--c), transparent 60%);
  opacity: .15;
  animation: neon-breathe 3s ease-in-out infinite;
  pointer-events: none;
}
.neon-card:hover .neon-border { opacity: 1; }
.neon-card:hover .neon-glow { opacity: .3; }

@keyframes neon-flow {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}
@keyframes neon-breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
</style>