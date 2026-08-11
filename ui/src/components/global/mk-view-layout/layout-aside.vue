<script setup lang="ts">
import { h, type FunctionalComponent } from 'vue'

defineOptions({ name: 'MkViewLayoutAside' })

const props = defineProps<{
  title?: string
}>()

defineSlots<{
  default?: (props: { Header: FunctionalComponent; title: string }) => unknown
}>()

const title = computed(() => props.title || '')
const LayoutAsideHeader: FunctionalComponent = (_, { slots }) =>
  h('header', { class: 'flex-between shrink-0 p-4' }, slots.default?.())
</script>

<template>
  <aside class="flex w-sidebar-expanded shrink-0 flex-col border-r">
    <slot :Header="LayoutAsideHeader" :title="title" />
  </aside>
</template>
