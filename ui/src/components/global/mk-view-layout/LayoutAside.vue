<script setup lang="ts">
import { computed, Fragment, h, isVNode, onBeforeUnmount, ref, watch, type FunctionalComponent, type VNode, useSlots } from 'vue'

defineOptions({ name: 'LayoutAside' })

const props = withDefaults(
  defineProps<{ collapsible?: boolean; resizable?: boolean; minLeftWidth?: number; maxLeftWidth?: number; title?: string }>(),
  { collapsible: false, resizable: false, maxLeftWidth: 400 },
)

defineSlots<{ default?: (props: { Header: FunctionalComponent; title: string }) => unknown }>()

const title = computed(() => props.title || '')
const slots = useSlots()
const isCollapsed = ref(false)
const asideCollapsed = computed(() => props.collapsible && isCollapsed.value)

// Tailwind 的主题别名在根节点解析，拖动时需在当前侧栏覆盖宽度类直接读取的 Token。
const asideRef = ref<HTMLElement>()
const leftWidth = ref(props.minLeftWidth)
const isResizing = ref(false)
const asideStyle = computed(() =>
  props.resizable && leftWidth.value !== undefined ? { '--spacing-sidebar-expanded': `${leftWidth.value}px` } : undefined,
)
let stopResizing: (() => void) | undefined

function startResizing(event: MouseEvent) {
  if (!props.resizable || asideCollapsed.value || event.button !== 0 || !asideRef.value) return
  stopResizing?.()
  event.preventDefault()
  const startX = event.clientX
  const startWidth = asideRef.value.getBoundingClientRect().width
  const themeWidth = Number.parseFloat(getComputedStyle(asideRef.value.parentElement!).getPropertyValue('--mk-sidebar-expanded-width'))
  const minWidth = props.minLeftWidth ?? themeWidth
  const maxWidth = Math.max(minWidth, props.maxLeftWidth)
  const previousUserSelect = document.body.style.userSelect
  const previousCursor = document.body.style.cursor
  isResizing.value = true
  document.body.style.userSelect = 'none'
  document.body.style.cursor = 'col-resize'

  function resizeAside(moveEvent: MouseEvent) {
    leftWidth.value = Math.max(minWidth, Math.min(maxWidth, startWidth + moveEvent.clientX - startX))
  }

  stopResizing = () => {
    isResizing.value = false
    document.body.style.userSelect = previousUserSelect
    document.body.style.cursor = previousCursor
    document.removeEventListener('mousemove', resizeAside)
    document.removeEventListener('mouseup', finishResizing)
    window.removeEventListener('blur', finishResizing)
    stopResizing = undefined
  }
  function finishResizing() {
    stopResizing?.()
  }
  document.addEventListener('mousemove', resizeAside)
  document.addEventListener('mouseup', finishResizing)
  window.addEventListener('blur', finishResizing)
}

watch(
  () => [props.resizable, asideCollapsed.value],
  () => stopResizing?.(),
)
onBeforeUnmount(() => stopResizing?.())

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
  <div
    ref="asideRef"
    class="group relative flex h-full shrink-0 transition-[width] duration-200 ease-out"
    :class="[asideCollapsed ? '' : 'w-sidebar-expanded', { 'aside-resizing': isResizing }]"
    :style="asideStyle"
  >
    <aside
      class="h-full overflow-hidden border-r transition-[width] duration-200 ease-out"
      :class="asideCollapsed ? 'w-0 border-none' : 'w-sidebar-expanded'"
    >
      <div v-show="!asideCollapsed" class="flex-column h-full w-sidebar-expanded">
        <LayoutAsideContent />
      </div>
    </aside>
    <!-- 拖动调整侧栏宽度 -->
    <div v-if="props.resizable && !asideCollapsed" class="aside-resize-handle" :class="{ 'is-resizing': isResizing }" @mousedown="startResizing" />
    <!-- 展开或收起侧栏 -->
    <MkTooltip v-if="props.collapsible" :content="asideCollapsed ? '展开' : '收起'" placement="right">
      <button
        type="button"
        class="absolute top-15 z-10 cursor-pointer border bg-white shadow-md h-6 transition-all duration-200 hover:text-primary"
        :class="
          asideCollapsed
            ? 'left-0 rounded-r-full border-l-0 w-5 flex-align-center pl-[2px]'
            : 'right-0 translate-x-1/2 rounded-full w-6 flex-center group-hover-visible'
        "
        @click="toggleAside"
      >
        <MkIcon name="icon_left_outlined" :class="asideCollapsed && 'rotate-180'" :size="12" />
      </button>
    </MkTooltip>
  </div>
</template>

<style scoped>
.aside-resizing,
.aside-resizing > aside {
  transition: none;
}

.aside-resize-handle {
  position: absolute;
  inset: 0 -2px 0 auto;
  z-index: 1;
  width: 4px;
  cursor: col-resize;
}

.aside-resize-handle:hover::after,
.aside-resize-handle.is-resizing::after {
  position: absolute;
  inset: 0 1px 0 auto;
  width: 1px;
  content: '';
  background: var(--el-color-primary);
}
</style>
