<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getChildRouteList } from '@/router/admin/utils'

const route = useRoute()
const router = useRouter()
const items = getChildRouteList('workspace')
const activeKeys = computed(
  () => new Set(route.matched.flatMap((item) => (item.name ? [String(item.name)] : []))),
)
</script>

<template>
  <nav class="px-1.5 py-2">
    <button
      v-for="item in items"
      :key="item.key"
      type="button"
      class="flex min-h-[55px] w-full cursor-pointer flex-col items-center justify-center gap-[3px] rounded-lg border-0 bg-transparent px-0.5 py-[7px] hover:bg-white/70"
      :class="activeKeys.has(item.key) && 'bg-white font-semibold'"
      @click="item.route && router.push(item.route)"
    >
      <MkIcon v-if="item.icon" :name="item.icon" />
      <span>{{ item.label }}</span>
    </button>
  </nav>
</template>
