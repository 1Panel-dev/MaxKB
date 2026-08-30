<script setup lang="ts">
import { computed, Fragment, h, isVNode, ref, type FunctionalComponent, type VNode, type VNodeChild, useSlots } from 'vue'
import { useRoute } from 'vue-router'
import { ElScrollbar } from 'element-plus'
import LayoutAside from './layout-aside.vue'
import LayoutBatchFooter from './layout-batch-footer.vue'

defineOptions({ name: 'MkViewLayout', inheritAttrs: false })

type BatchSelectionValue = string | number
interface LayoutFooterProps {
  batchSelection?: BatchSelectionValue[]
  batchValues?: BatchSelectionValue[]
}

type LayoutFooterEmits = { 'batch-cancel': []; 'update:batchSelection': [values: BatchSelectionValue[]] }

type LayoutFooterSlots = { default?: () => VNodeChild; 'footer-batch-actions'?: (props: { batchSelection: BatchSelectionValue[] }) => VNodeChild }

interface ScrollData {
  scrollLeft: number
  scrollTop: number
}

const props = withDefaults(defineProps<{ collapsible?: boolean; loading?: boolean; title?: string }>(), { collapsible: false, loading: false })

const emit = defineEmits<{ scroll: [data: ScrollData] }>()

defineSlots<{
  aside?: (props: { Header: FunctionalComponent; title: string }) => unknown
  default?: (props: { Footer: FunctionalComponent; Header: FunctionalComponent; title: string }) => unknown
  top?: () => unknown
}>()

const route = useRoute()
const title = computed(() => props.title ?? route.meta.title ?? '')
const slots = useSlots()
const contentScrollbarRef = ref<InstanceType<typeof ElScrollbar>>()

function getScrollContainer() {
  return contentScrollbarRef.value?.wrapRef
}

function setScrollTop(scrollTop: number) {
  contentScrollbarRef.value?.setScrollTop(scrollTop)
}

function flattenSlotNodes(children: unknown): VNode[] {
  const childNodes = Array.isArray(children) ? children : [children]

  return childNodes.flatMap((child) => {
    if (!isVNode(child)) return []
    if (child.type === Fragment) return flattenSlotNodes(child.children)
    return [child]
  })
}

const LayoutHeader: FunctionalComponent = (_, { slots }) => h('header', { class: 'flex-between shrink-0 py-4 gap-4' }, slots.default?.())

const LayoutFooter: FunctionalComponent<LayoutFooterProps, LayoutFooterEmits, LayoutFooterSlots> = (footerProps, { emit: emitFooter, slots }) => {
  const batchActions = slots['footer-batch-actions']

  if (batchActions) {
    const batchSelection = footerProps.batchSelection ?? []
    const batchValues = footerProps.batchValues ?? []
    const selectedValues = new Set(batchSelection)
    const selectedCount = batchValues.filter((value) => selectedValues.has(value)).length
    const allSelected = batchValues.length > 0 && selectedCount === batchValues.length

    return h(
      LayoutBatchFooter,
      {
        allSelected,
        class: '-mx-6 -mb-6',
        selectedCount,
        total: batchValues.length,
        onCancel: () => {
          emitFooter('update:batchSelection', [])
          emitFooter('batch-cancel')
        },
        onSelectAll: (selected: boolean) => {
          emitFooter('update:batchSelection', selected ? [...batchValues] : [])
        },
      },
      { default: () => batchActions({ batchSelection }) },
    )
  }

  return h('footer', { class: '-mx-6 -mb-6 flex shrink-0 justify-end border-t px-6 py-4' }, slots.default?.() ?? undefined)
}

LayoutFooter.props = ['batchSelection', 'batchValues']
LayoutFooter.emits = ['batch-cancel', 'update:batchSelection']

const LayoutContent: FunctionalComponent = () => {
  const contentNodes = flattenSlotNodes(slots.default?.({ Footer: LayoutFooter, Header: LayoutHeader, title: title.value }))
  const customHeaderNodes = contentNodes.filter((node) => node.type === LayoutHeader)
  const customFooterNodes = contentNodes.filter((node) => node.type === LayoutFooter)
  const bodyNodes = contentNodes.filter((node) => node.type !== LayoutHeader && node.type !== LayoutFooter)
  const headerNodes = customHeaderNodes.length ? customHeaderNodes : title.value ? [h('header', { class: 'flex-between shrink-0 py-4 gap-4' }, [h('h4', title.value)])] : []
  return [
    ...headerNodes,
    h(
      ElScrollbar,
      {
        class: ['-mx-6 min-h-0 flex-1', customFooterNodes.length ? '' : '-mb-6'],
        onScroll: (data: ScrollData) => emit('scroll', data),
        ref: contentScrollbarRef,
        viewClass: 'flex min-h-full flex-col px-6 pb-6',
      },
      { default: () => bodyNodes },
    ),
    ...customFooterNodes,
  ]
}

defineExpose({ getScrollContainer, setScrollTop })
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
