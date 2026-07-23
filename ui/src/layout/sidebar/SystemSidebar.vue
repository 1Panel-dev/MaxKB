<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'
import { getChildRouteList } from '@/router/admin/utils'

defineProps<{
  collapsed?: boolean
}>()

const route = useRoute()
const router = useRouter()
const items = getChildRouteList('system')
const activeKeys = computed(
  () => new Set(route.matched.flatMap((item) => (item.name ? [String(item.name)] : []))),
)
</script>

<template>
  <nav :class="collapsed ? 'px-2.5 pt-3.5' : 'px-5 pt-3.5 max-md:px-2.5'">
    <template v-for="item in items" :key="item.key">
      <button
        type="button"
        class="flex w-full cursor-pointer items-center gap-2.5 rounded-lg border-0 bg-transparent font-[inherit] text-[15px] text-[#303846] hover:bg-white/70"
        :class="[
          collapsed
            ? 'min-h-11 justify-center p-0'
            : 'min-h-11 px-3 text-left max-md:justify-center max-md:p-0',
          activeKeys.has(item.key) || item.children?.some((child) => activeKeys.has(child.key)),
        ]"
      >
        <MkIcon v-if="item.icon" :name="item.icon" />
        <span class="max-md:hidden">{{ item.label }}</span>
        <MkIcon
          v-if="item.children?.length && !collapsed"
          :icon="ArrowDown"
          class="ml-auto max-md:hidden"
        />
      </button>

      <div v-if="item.children?.length && !collapsed" class="pb-2 pt-0.5 max-md:hidden">
        <button
          v-for="child in item.children"
          :key="child.key"
          type="button"
          class="flex min-h-11 w-full cursor-pointer items-center rounded-lg border-0 pl-[42px] text-left"
          :class="activeKeys.has(child.key) && 'bg-white font-semibold'"
          @click="child.route && router.push(child.route)"
        >
          {{ child.label }}
        </button>
      </div>
    </template>
  </nav>
</template>
