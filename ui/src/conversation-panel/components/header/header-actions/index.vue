<script lang="ts">
import { Fragment, cloneVNode, computed, defineComponent, h, isVNode } from 'vue'
import { ElButton } from 'element-plus'
import type { VNode } from 'vue'
import MkDropdownMenu from '@/components/global/mk-dropdown/MkDropdownMenu.vue'
import MkDropdown from '@/components/global/mk-dropdown/index.vue'
import MkIcon from '@/components/global/mk-icon/index.vue'
import { VIEW_TYPE, useViewType } from '../../../view/index'
import { useStore } from '@/stores/chat'
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
  props: { collapse: Boolean, alwaysCollapse: Boolean },
  setup(props, { slots }) {
    // 仅嵌入头部的更多图标使用主题文字颜色。
    const auth = useViewType() === VIEW_TYPE.EMBED ? useStore().auth : undefined
    const moreIconColor = computed(() => auth?.authProfile?.custom_theme?.header_font_color)
    return () => {
      const actions = collectActions(slots.default?.())
      const display = props.alwaysCollapse || (props.collapse && actions.length > 1) ? 'menu' : 'button'
      const renderActions = () =>
        actions.map((action) =>
          cloneVNode(action, {
            display,
            type: '',
            class: display === 'button' ? ['[&.is-disabled_.mk-icon]:text-N400!', action.props?.disabled ? 'text-N400!' : 'text-N900!'] : '',
          }),
        )

      if (display === 'button') return h('div', { class: 'flex-align-center gap-2 [&>.el-button]:ml-0!' }, renderActions())
      // 更多入口统一收纳所有可见操作。
      return h(
        MkDropdown,
        { trigger: 'click', placement: 'bottom-end', persistent: true },
        {
          default: () =>
            h(ElButton, { text: true }, () =>
              h(MkIcon, { name: 'icon_more_outlined', size: 18, color: moreIconColor.value, class: moreIconColor.value ? undefined : 'text-N900!' }),
            ),
          dropdown: () => h(MkDropdownMenu, null, { default: renderActions }),
        },
      )
    }
  },
})
</script>
