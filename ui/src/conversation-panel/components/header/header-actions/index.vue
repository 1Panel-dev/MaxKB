<script lang="ts">
import { cloneVNode, defineComponent, Fragment, h, isVNode, type VNode } from 'vue'
import MkDropdown from '@/components/global/mk-dropdown/index.vue'
import MkDropdownMenu from '@/components/global/mk-dropdown/MkDropdownMenu.vue'
import MkIcon from '@/components/global/mk-icon/index.vue'
import { ElButton } from 'element-plus'
import { hasRenderableSlotContent } from '@/utils/vnode'

// 只展开 Fragment；插槽直接传 MkAction，显示条件写在该节点上。
function collectActions(children: unknown): VNode[] {
  const actionNodes = Array.isArray(children) ? children : [children]
  return actionNodes.flatMap((node) => {
    if (!isVNode(node) || !hasRenderableSlotContent(node)) return []
    if (node.type === Fragment) return collectActions(node.children)
    return [node]
  })
}

export default defineComponent({
  name: 'HeaderActions',
  props: { collapse: Boolean },
  setup(props, { slots }) {
    return () => {
      const actions = collectActions(slots.default?.())
      const display = props.collapse && actions.length > 1 ? 'menu' : 'button'
      const renderActions = () =>
        actions.map((action) =>
          cloneVNode(action, {
            display,
            class: ['[&.is-disabled_.mk-icon]:text-N400!', display === 'button' ? (action.props?.disabled ? 'text-N400!' : 'text-N900!') : ''],
          }),
        )

      if (display === 'button') return h(Fragment, renderActions())
      // 更多入口统一收纳所有可见操作。
      return h(
        MkDropdown,
        { trigger: 'click', placement: 'bottom-end', persistent: true },
        {
          default: () => h(ElButton, { text: true }, () => h(MkIcon, { name: 'icon_more_outlined', size: 18, class: 'text-N900!' })),
          dropdown: () => h(MkDropdownMenu, null, { default: renderActions }),
        },
      )
    }
  },
})
</script>

<style lang="scss"></style>
