import {
  Fragment,
  createTextVNode,
  defineComponent,
  h,
  isVNode,
  type Component,
  type Slots,
  type SlotsType,
  type VNode,
} from 'vue'
import { ElScrollbar } from 'element-plus'

type LayoutMainSlotProps = {
  Header: Component
  title: string
}

const LayoutMainHeader = defineComponent({
  name: 'MkViewLayoutMainHeader',
  setup(_, { slots }) {
    return () => slots.default?.()
  },
})

function flattenSlotNodes(children: unknown): VNode[] {
  const childNodes = Array.isArray(children) ? children : [children]

  return childNodes.flatMap((child) => {
    if (child === undefined || child === null || typeof child === 'boolean') return []
    if (!isVNode(child)) return [createTextVNode(String(child))]
    if (child.type === Fragment) return flattenSlotNodes(child.children)
    return [child]
  })
}

function getHeaderNodes(headerNode: VNode) {
  const headerSlots = headerNode.children as Slots | null
  return flattenSlotNodes(headerSlots?.default?.())
}

export default defineComponent({
  name: 'MkViewLayoutMain',
  props: {
    fallbackTitle: {
      default: '',
      type: String,
    },
    title: {
      default: '',
      type: String,
    },
  },
  slots: Object as SlotsType<{
    default?: (props: LayoutMainSlotProps) => VNode[]
  }>,
  setup(props, { slots }) {
    return () => {
      const headerNodes: VNode[] = []
      const contentNodes: VNode[] = []

      flattenSlotNodes(slots.default?.({ Header: LayoutMainHeader, title: props.title })).forEach(
        (node) => {
          if (node.type === LayoutMainHeader) {
            headerNodes.push(...getHeaderNodes(node))
            return
          }

          contentNodes.push(node)
        },
      )

      const resolvedHeaderNodes =
        headerNodes.length > 0
          ? headerNodes
          : props.fallbackTitle
            ? [h('h4', props.fallbackTitle)]
            : []

      return h('main', { class: 'flex min-w-0 flex-1 flex-col px-6 mb-6' }, [
        resolvedHeaderNodes.length
          ? h('header', { class: 'flex-between shrink-0 py-4' }, resolvedHeaderNodes)
          : null,
        h(
          ElScrollbar,
          {
            class: 'min-h-0 flex-1',
            viewClass: 'flex min-h-full flex-col',
          },
          { default: () => contentNodes },
        ),
      ])
    }
  },
})
