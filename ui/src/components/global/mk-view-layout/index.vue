<script setup lang="ts">
import { Fragment, h, isVNode, type FunctionalComponent, type VNode } from 'vue'
import { useRoute } from 'vue-router'
import LayoutAside from './layout-aside.vue'

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
  default?: (props: { Header: FunctionalComponent; title: string }) => unknown
  top?: () => unknown
}>()

const route = useRoute()
const title = computed(() => props.title || route.meta.title || '')
const slots = useSlots()

function flattenSlotNodes(children: unknown): VNode[] {
  const childNodes = Array.isArray(children) ? children : [children]

  return childNodes.flatMap((child) => {
    if (!isVNode(child)) return []
    if (child.type === Fragment) return flattenSlotNodes(child.children)
    return [child]
  })
}

const LayoutHeader: FunctionalComponent = (_, { slots }) =>
  h('header', { class: 'flex-between shrink-0 py-4 gap-4' }, slots.default?.())

const LayoutContent: FunctionalComponent = () => {
  const contentNodes = flattenSlotNodes(
    slots.default?.({ Header: LayoutHeader, title: title.value }),
  )
  const hasCustomHeader = contentNodes.some((node) => node.type === LayoutHeader)

  return [
    hasCustomHeader || !title.value
      ? null
      : h('header', { class: 'flex-between shrink-0 py-4 gap-4' }, [h('h4', title.value)]),
    ...contentNodes,
  ]
}
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

      <main class="mb-6 flex min-w-0 flex-1 flex-col px-6 min-h-0">
        <LayoutContent />
      </main>
    </div>
  </div>
</template>
