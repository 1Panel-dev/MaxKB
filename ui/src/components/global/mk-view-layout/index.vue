<script setup lang="ts">
import { computed, Fragment, h, isVNode, type FunctionalComponent, type VNode, useSlots } from 'vue'
import { useRoute } from 'vue-router'
import { ElScrollbar } from 'element-plus'
import LayoutAside from './layout-aside.vue'

defineOptions({ name: 'MkViewLayout', inheritAttrs: false })

const props = withDefaults(
  defineProps<{
    collapsible?: boolean
    loading?: boolean
    title?: string
  }>(),
  {
    collapsible: false,
    loading: false,
  },
)

defineSlots<{
  aside?: (props: { Header: FunctionalComponent; title: string }) => unknown
  default?: (props: {
    Footer: FunctionalComponent
    Header: FunctionalComponent
    title: string
  }) => unknown
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

const LayoutFooter: FunctionalComponent = (_, { slots }) =>
  h(
    'footer',
    { class: '-mx-6 -mb-6 flex shrink-0 justify-end border-t px-6 py-4' },
    slots.default?.(),
  )

const LayoutContent: FunctionalComponent = () => {
  const contentNodes = flattenSlotNodes(
    slots.default?.({ Footer: LayoutFooter, Header: LayoutHeader, title: title.value }),
  )
  const customHeaderNodes = contentNodes.filter((node) => node.type === LayoutHeader)
  const customFooterNodes = contentNodes.filter((node) => node.type === LayoutFooter)
  const bodyNodes = contentNodes.filter(
    (node) => node.type !== LayoutHeader && node.type !== LayoutFooter,
  )
  const headerNodes = customHeaderNodes.length
    ? customHeaderNodes
    : title.value
      ? [h('header', { class: 'flex-between shrink-0 py-4 gap-4' }, [h('h4', title.value)])]
      : []

  return [
    ...headerNodes,
    h(
      ElScrollbar,
      {
        class: ['-mx-6 min-h-0 flex-1', customFooterNodes.length ? '' : '-mb-6'],
        viewClass: 'flex min-h-full flex-col px-6 pb-6',
      },
      { default: () => bodyNodes },
    ),
    ...customFooterNodes,
  ]
}
</script>

<template>
  <div v-loading="props.loading" class="flex h-full min-h-0 flex-col" v-bind="$attrs">
    <div v-if="$slots.top" class="shrink-0 border-b px-4 py-3">
      <slot name="top" />
    </div>

    <div class="flex min-h-0 flex-1">
      <LayoutAside v-if="$slots.aside" :collapsible="props.collapsible" :title="title">
        <template #default="{ Header, title: asideTitle }">
          <slot name="aside" :Header="Header" :title="asideTitle" />
        </template>
      </LayoutAside>

      <main class="mb-6 flex min-h-0 min-w-0 flex-1 flex-col px-6">
        <LayoutContent />
      </main>
    </div>
  </div>
</template>
