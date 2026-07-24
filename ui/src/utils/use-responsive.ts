import { onBeforeUnmount, onMounted, ref } from 'vue'

/** 与 Tailwind 的 md 断点一致；默认根字号为 16px 时，48rem 等于 768px。 */
const SMALL_SCREEN_MEDIA_QUERY = '(width < 48rem)'

/** 判断当前浏览器视口是否处于小屏布局，并在跨越断点时更新。 */
export function useIsSmallScreen() {
  const mediaQuery =
    typeof window === 'undefined' ? undefined : window.matchMedia(SMALL_SCREEN_MEDIA_QUERY)
  const isSmallScreen = ref(mediaQuery?.matches ?? false)

  function syncIsSmallScreen(event: MediaQueryListEvent) {
    isSmallScreen.value = event.matches
  }

  onMounted(() => {
    mediaQuery?.addEventListener('change', syncIsSmallScreen)
  })

  onBeforeUnmount(() => {
    mediaQuery?.removeEventListener('change', syncIsSmallScreen)
  })

  return isSmallScreen
}
