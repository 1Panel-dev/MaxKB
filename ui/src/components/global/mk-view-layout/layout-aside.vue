<script setup lang="ts">
import { computed, Fragment, h, isVNode, ref, type FunctionalComponent, type VNode, useSlots } from 'vue'

defineOptions({ name: 'LayoutAside' })

const props = withDefaults(defineProps<{ collapsible?: boolean; title?: string }>(), { collapsible: false })

defineSlots<{ default?: (props: { Header: FunctionalComponent; title: string }) => unknown }>()

const title = computed(() => props.title || '')
const slots = useSlots()
const isCollapsed = ref(false)
const asideCollapsed = computed(() => props.collapsible && isCollapsed.value)

function flattenSlotNodes(children: unknown): VNode[] {
  const childNodes = Array.isArray(children) ? children : [children]

  return childNodes.flatMap((child) => {
    if (!isVNode(child)) return []
    if (child.type === Fragment) return flattenSlotNodes(child.children)
    return [child]
  })
}

const LayoutAsideHeader: FunctionalComponent = (_, { slots }) => h('header', { class: 'flex-between shrink-0 p-4' }, slots.default?.())

const LayoutAsideContent: FunctionalComponent = () => {
  const contentNodes = flattenSlotNodes(slots.default?.({ Header: LayoutAsideHeader, title: title.value }))
  const hasCustomHeader = contentNodes.some((node) => node.type === LayoutAsideHeader)

  return [hasCustomHeader || !title.value ? null : h('header', { class: 'flex-between shrink-0 p-4' }, [h('h4', title.value)]), ...contentNodes]
}

function toggleAside(event: MouseEvent) {
  isCollapsed.value = !isCollapsed.value

  if (event.detail > 0) {
    const toggleButton = event.currentTarget as HTMLButtonElement
    toggleButton.blur()
  }
}
</script>

<template>
  <div class="group relative flex h-full shrink-0 transition-[width] duration-200 ease-out" :class="asideCollapsed ? '' : 'w-sidebar-expanded'">
    <aside class="h-full overflow-hidden border-r transition-[width] duration-200 ease-out" :class="asideCollapsed ? 'w-0 border-none' : 'w-sidebar-expanded'">
      <div v-show="!asideCollapsed" class="flex h-full w-sidebar-expanded flex-col">
        <LayoutAsideContent />
      </div>
    </aside>
    <el-tooltip v-if="props.collapsible" :content="asideCollapsed ? '展开' : '收起'" placement="right">
      <button
        type="button"
        class="absolute top-15 z-10 cursor-pointer border bg-white shadow-md h-6 transition-all duration-200 hover:text-primary"
        :class="asideCollapsed ? 'left-0 rounded-r-full border-l-0 w-5 flex items-center pl-[2px]' : 'right-0 translate-x-1/2 rounded-full w-6 flex-center group-hover-visible'"
        @click="toggleAside"
      >
        <MkIcon :name="asideCollapsed ? 'icon_right_outlined' : 'icon_left_outlined'" :size="12" />
      </button>
    </el-tooltip>
  </div>
</template>
