<script setup lang="ts">
import type { User } from '~/types/api'

defineProps<{ user?: User | null; userId?: number }>()
const mediaUrl = useMediaUrl()
</script>

<template>
  <NuxtLink
    v-if="user"
    :to="`/user/${user.id}`"
    class="inline-flex items-center gap-2 text-sm text-muted hover:text-primary"
  >
    <img v-if="user.avatar" :src="mediaUrl(user.avatar)" class="w-5 h-5 rounded-full object-cover border border-border" alt="" />
    <span v-else class="w-5 h-5 rounded-full bg-surface-2 inline-flex items-center justify-center text-xs">
      {{ user.username?.[0]?.toUpperCase() }}
    </span>
    {{ user.username }}
  </NuxtLink>
  <span v-else-if="userId" class="text-sm text-faint">用户 #{{ userId }}</span>
</template>