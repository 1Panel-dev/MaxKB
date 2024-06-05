import { nextTick, onBeforeMount, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import useStore from '@/stores'
import { DeviceType } from '@/enums/common'
/** 参考 Bootstrap 的响应式设计 WIDTH = 600 */
const WIDTH = 600

/** 根据大小变化重新布局 */
export default () => {
  const { common } = useStore()
  const _isMobile = () => {
    const rect = document.body?.getBoundingClientRect()
    return rect.width - 1 < WIDTH
  }

  const _resizeHandler = () => {
    if (!document.hidden) {
      const isMobile = _isMobile()
      common.toggleDevice(isMobile ? DeviceType.Mobile : DeviceType.Desktop)
    }
  }

  onBeforeMount(() => {
    window.addEventListener('resize', _resizeHandler)
  })

  onMounted(() => {
    nextTick(() => {
      if (_isMobile()) {
        common.toggleDevice(DeviceType.Mobile)
      }
    })
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', _resizeHandler)
  })
}
