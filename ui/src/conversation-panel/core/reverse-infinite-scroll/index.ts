import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { ScrollbarInstance } from 'element-plus'
import { Scroll } from '../scroll'

export interface ReverseInfiniteScrollProps {
  loading: boolean
  hasMore: boolean
  count: number
  loadMore: () => Promise<boolean>
}

/** 顶部加载历史消息，底部定位与跟随交给共用 Scroll。 */
export function useReverseInfiniteScroll(props: Readonly<ReverseInfiniteScrollProps>) {
  const scrollbarRef = ref<ScrollbarInstance>()
  const requesting = ref(false)
  const initialLoading = computed(() => props.loading && props.count === 0)
  const loadingMore = computed(() => props.count > 0 && (props.loading || requesting.value))
  let scroll: Scroll | undefined
  let initialized = false
  let previousTop = 0

  async function scrollToBottom() {
    await nextTick()
    scroll?.forceBottom()
  }

  async function followBottom() {
    await nextTick()
    if (!requesting.value) scroll?.scrollBottom()
  }

  // 只在成功新增历史记录后继续补满视口，失败或空页停止自动请求。
  async function loadOlder() {
    const wrap = scrollbarRef.value?.wrapRef
    if (!wrap || props.loading || requesting.value || !props.hasMore || !props.count) return
    const previousHeight = wrap.scrollHeight
    const previousCount = props.count
    requesting.value = true
    let loaded = false
    try {
      loaded = await props.loadMore()
      await nextTick()
      if (scrollbarRef.value?.wrapRef !== wrap) return
      scrollbarRef.value.setScrollTop(wrap.scrollTop + wrap.scrollHeight - previousHeight)
    } catch {
      // 下次主动上滑时可重试。
    } finally {
      requesting.value = false
    }
    if (loaded && props.count > previousCount) await fillViewport()
  }

  async function fillViewport() {
    const wrap = scrollbarRef.value?.wrapRef
    if (wrap && wrap.clientHeight > 0 && wrap.scrollHeight <= wrap.clientHeight + 1) await loadOlder()
  }

  function onScroll({ scrollTop }: { scrollTop: number }) {
    const scrollingUp = scrollTop < previousTop
    previousTop = scrollTop
    // 只响应向上滚动，前插补偿产生的向下位移不触发下一页。
    if (scrollingUp && scrollTop <= 60) void loadOlder()
  }

  async function initialize() {
    if (!props.count) initialized = false
    if (!scroll || initialized || !props.count || props.loading) return
    initialized = true
    await scrollToBottom()
    await fillViewport()
  }

  watch(
    () => [props.count, props.loading] as const,
    async ([count], [previousCount]) => {
      if (!initialized || !count) await initialize()
      else if (count !== previousCount) await followBottom()
    },
  )

  onMounted(() => {
    const wrap = scrollbarRef.value?.wrapRef
    if (wrap) scroll = new Scroll(wrap)
    void initialize()
  })
  onBeforeUnmount(() => {
    scroll?.destroy()
    scroll = undefined
  })

  return { scrollbarRef, initialLoading, loadingMore, onScroll, scrollToBottom, followBottom }
}
