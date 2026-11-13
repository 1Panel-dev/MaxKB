import { onBeforeUnmount, watch, type Ref } from 'vue'
import { Scroll } from './scroll'

/**
 * 限高滚动容器的底部跟随：容器挂载后定位到底部，内容变化时仅在用户仍位于底部附近才跟随。
 * 容器随展开 / 收起挂载和卸载，跟随实例与内容监听随之创建和释放。
 */
export function useBottomFollow(containerRef: Ref<HTMLElement | null | undefined>) {
  let scroll: Scroll | undefined
  let observer: MutationObserver | undefined

  function release() {
    observer?.disconnect()
    observer = undefined
    scroll?.destroy()
    scroll = undefined
  }

  watch(
    containerRef,
    (container) => {
      release()
      if (!container) return
      const follow = new Scroll(container)
      scroll = follow
      follow.forceBottom()
      observer = new MutationObserver(() => follow.scrollBottom())
      observer.observe(container, { childList: true, subtree: true, characterData: true })
    },
    { flush: 'post', immediate: true },
  )

  onBeforeUnmount(release)
}
