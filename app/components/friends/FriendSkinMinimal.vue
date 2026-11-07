<script setup lang="ts">
import type { FriendLink } from '~/types/api'

const props = defineProps<{ friend: FriendLink }>()
const mediaUrl = useMediaUrl()
</script>

<template>
  <a
    :href="friend.url"
    target="_blank"
    rel="noopener"
    class="block rounded-lg p-4 border border-border bg-surface hover:shadow-md transition"
    :style="{ '--c': friend.theme_color }"
  >
    <div class="flex items-center gap-3">
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
        <div v-if="friend.tags?.length" class="flex gap-1 mt-1 flex-wrap">
          <span
            v-for="t in friend.tags" :key="t"
            class="text-[10px] px-1.5 py-0.5 rounded bg-surface-2 text-faint"
          >{{ t }}</span>
        </div>
      </div>
    </div>
  </a>
</template>