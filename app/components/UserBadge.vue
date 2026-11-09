<script setup lang="ts">
import type { User } from '~/types/api'

defineProps<{ user?: User | null; userId?: number }>()
const avatarUrl = useAvatarUrl()
</script>

<template>
  <NuxtLink
    v-if="user"
    :to="`/user/${user.id}`"
    class="inline-flex items-center gap-2 text-sm text-muted hover:text-primary"
  >
    <img :src="avatarUrl(user.avatar)" class="w-5 h-5 rounded-full object-cover border border-border" alt="" />
    {{ user.username }}
  </NuxtLink>
  <span v-else-if="userId" class="text-sm text-faint">用户 #{{ userId }}</span>
</template>