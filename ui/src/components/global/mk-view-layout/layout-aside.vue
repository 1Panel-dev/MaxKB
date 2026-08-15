<script setup lang="ts">
import {
  computed,
  Fragment,
  h,
  isVNode,
  type FunctionalComponent,
  type VNode,
  useSlots,
} from 'vue'

defineOptions({ name: 'MkViewLayoutAside' })

const props = defineProps<{
  title?: string
}>()

defineSlots<{
  default?: (props: { Header: FunctionalComponent; title: string }) => unknown
}>()

const title = computed(() => props.title || '')
const slots = useSlots()

function flattenSlotNodes(children: unknown): VNode[] {
  const childNodes = Array.isArray(children) ? children : [children]

  return childNodes.flatMap((child) => {
    if (!isVNode(child)) return []
    if (child.type === Fragment) return flattenSlotNodes(child.children)
    return [child]
  })
}

const LayoutAsideHeader: FunctionalComponent = (_, { slots }) =>
  h('header', { class: 'flex-between shrink-0 p-4' }, slots.default?.())

const LayoutAsideContent: FunctionalComponent = () => {
  const contentNodes = flattenSlotNodes(
    slots.default?.({ Header: LayoutAsideHeader, title: title.value }),
  )
  const hasCustomHeader = contentNodes.some((node) => node.type === LayoutAsideHeader)

  return [
    hasCustomHeader || !title.value
      ? null
      : h('header', { class: 'flex-between shrink-0 p-4' }, [h('h4', title.value)]),
    ...contentNodes,
  ]
}
</script>

<template>
  <aside class="flex w-sidebar-expanded shrink-0 flex-col border-r">
    <LayoutAsideContent />
  </aside>
</template>
