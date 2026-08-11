<script setup lang="ts">
import type { Component, FunctionalComponent } from 'vue'
import { useRoute } from 'vue-router'
import LayoutAside from './layout-aside.vue'
import LayoutMain from './layout-main'

defineOptions({ name: 'MkViewLayout', inheritAttrs: false })

const props = withDefaults(
  defineProps<{
    loading?: boolean
    title?: string
  }>(),
  {
    loading: false,
  },
)

defineSlots<{
  aside?: (props: { Header: FunctionalComponent; title: string }) => unknown
  default?: (props: { Header: Component; title: string }) => unknown
  top?: () => unknown
}>()

const route = useRoute()
const title = computed(() => props.title || route.meta.title || '')
const slots = useSlots()
const fallbackTitle = computed(() =>
  !slots.default || slots.default.length === 0 ? title.value : '',
)
</script>

<template>
  <div v-loading="props.loading" class="flex h-full min-h-0 flex-col" v-bind="$attrs">
    <div v-if="$slots.top" class="shrink-0 border-b px-4 py-3">
      <slot name="top" />
    </div>

    <div class="flex min-h-0 flex-1">
      <LayoutAside v-if="$slots.aside" :title="title">
        <template #default="{ Header, title: asideTitle }">
          <slot name="aside" :Header="Header" :title="asideTitle" />
        </template>
      </LayoutAside>

      <LayoutMain :fallback-title="fallbackTitle" :title="title">
        <template #default="{ Header, title: mainTitle }">
          <slot :Header="Header" :title="mainTitle" />
        </template>
      </LayoutMain>
    </div>
  </div>
</template>
