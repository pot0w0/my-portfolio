<script setup lang="ts">
import type { FriendLink } from '~/types/api'
import FriendSkinMinimal from './friends/FriendSkinMinimal.vue'
import FriendSkinNeon from './friends/FriendSkinNeon.vue'
import FriendSkinTilt from './friends/FriendSkinTilt.vue'

const props = defineProps<{ friend: FriendLink }>()

const skinMap = {
  minimal: FriendSkinMinimal,
  neon: FriendSkinNeon,
  tilt: FriendSkinTilt,
} as const

const skinComp = computed(() => skinMap[props.friend.skin] ?? FriendSkinMinimal)
</script>

<template>
  <component :is="skinComp" :friend="friend" />
</template>