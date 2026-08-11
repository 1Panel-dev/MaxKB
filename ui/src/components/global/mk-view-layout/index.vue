<script setup lang="ts">
import type { FunctionalComponent } from 'vue'
import { useRoute } from 'vue-router'
import LayoutAside from './layout-aside.vue'

defineOptions({ name: 'MkViewLayout', inheritAttrs: false })

const props = defineProps<{
  title?: string
}>()

defineSlots<{
  aside?: (props: { Header: FunctionalComponent; title: string }) => unknown
  default?: () => unknown
  header?: (props: { title: string }) => unknown
  top?: () => unknown
}>()

const route = useRoute()
const title = computed(() => props.title || route.meta.title || '')
</script>

<template>
  <div class="flex h-full min-h-0 flex-col" v-bind="$attrs">
    <div v-if="$slots.top" class="shrink-0 border-b px-4 py-3">
      <slot name="top" />
    </div>

    <div class="flex min-h-0 flex-1">
      <LayoutAside v-if="$slots.aside" :title="title">
        <template #default="{ Header, title: asideTitle }">
          <slot name="aside" :Header="Header" :title="asideTitle" />
        </template>
      </LayoutAside>

      <main class="flex min-w-0 flex-1 flex-col px-6">
        <header class="flex-between shrink-0 py-4">
          <slot name="header" :title="title">
            <h4>{{ title }}</h4>
          </slot>
        </header>

        <el-scrollbar class="min-h-0 flex-1">
          <slot />
        </el-scrollbar>
      </main>
    </div>
  </div>
</template>
