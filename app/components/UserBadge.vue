<script setup lang="ts">
import type { User } from '~/types/api'

defineProps<{ user?: User; userId?: number }>()
</script>

<template>
  <NuxtLink
    v-if="user"
    :to="`/user/${user.id}`"
    class="inline-flex items-center gap-2 text-sm text-muted hover:text-blue-600"
  >
    <img
      v-if="user.avatar"
      :src="user.avatar"
      class="w-5 h-5 rounded-full object-cover"
      alt=""
    />
    <span class="w-5 h-5 rounded-full bg-surface-2 inline-flex items-center justify-center text-xs" v-else>
      {{ user.username?.[0]?.toUpperCase() }}
    </span>
    {{ user.username }}
  </NuxtLink>
  <span v-else-if="userId" class="text-sm text-faint">用户 #{{ userId }}</span>
</template>