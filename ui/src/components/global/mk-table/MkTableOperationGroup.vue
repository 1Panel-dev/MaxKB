<script lang="ts">
import { Comment, Fragment, Text, computed, defineComponent, h, isVNode, provide, type PropType, type VNode } from 'vue'
import MkTableMoreDropdown from './MkTableMoreDropdown.vue'
import { actionContextKey, type ActionContext } from '../mk-action/context'

/* 每个操作只挂载一次，由所在位置提供展示模式。 */
const ActionPlacement = defineComponent({
  name: 'TableActionPlacement',
  props: {
    action: { type: Object as PropType<VNode>, required: true },
    display: { type: String as PropType<ActionContext['display']>, required: true },
    first: Boolean,
  },
  setup(props) {
    provide(
      actionContextKey,
      computed(() => ({ display: props.display, first: props.first })),
    )
    return () => props.action
  },
})

/* 保留 Fragment 路径与显式 key，忽略条件注释和文本，不读取业务组件内部结构。 */
function collectActions(children: unknown, parentKey = ''): { key: string; node: VNode }[] {
  if (!Array.isArray(children)) return []
  return children.flatMap((node, index) => {
    if (!isVNode(node) || node.type === Comment || node.type === Text) return []
    const key = `${parentKey}/${String(node.key ?? index)}`
    if (node.type === Fragment) return collectActions(node.children, key)
    return [{ key, node }]
  })
}

export default defineComponent({
  name: 'MkTableOperationGroup',
  props: { maxVisible: { type: Number, default: 2 } },
  setup(props, { slots }) {
    return () => {
      // 插槽在渲染期间读取，确保 v-if 和行数据变化时重新分配。
      const actions = collectActions(slots.default?.())
      const maxVisible = Number.isFinite(props.maxVisible) ? Math.max(0, Math.floor(props.maxVisible)) : 2
      const inlineActions = actions.slice(0, maxVisible)
      const moreActions = actions.slice(maxVisible)
      return h('div', { class: 'flex-align-center gap-1 [&>.el-button]:ml-0!' }, [
        ...inlineActions.map(({ key, node }) => h(ActionPlacement, { key, action: node, display: 'button' })),
        moreActions.length
          ? h(
              MkTableMoreDropdown,
              { key: 'more', persistent: true },
              {
                default: () =>
                  moreActions.map(({ key, node }, index) => h(ActionPlacement, { key, action: node, display: 'menu', first: index === 0 })),
              },
            )
          : null,
      ])
    }
  },
})
</script>
