<script setup lang="ts">
import { onBeforeUnmount, onMounted, provide, ref, watch } from 'vue'
import SharePanel from '../../main/share-panel/index.vue'
import { createSharePanelStore, SHARE_PANEL_KEY } from '../../main/share-panel/index'
import { VIEW_KEY, VIEW_TYPE, DEVICE_KEY, createDeviceType } from '../index.ts'

defineOptions({ name: 'ShareConversation' })

const props = defineProps<{
  /** 公开分享链接 ID */
  shareId: string
}>()

// 只读分享:仅主面板,无会话列表、输入框和执行详情。
// 不注入 MESSAGE_LIST_KEY,表单等内容项拿不到发送能力即自动只读。
const sharePanel = createSharePanelStore({ shareId: () => props.shareId })

provide(SHARE_PANEL_KEY, sharePanel)
provide(VIEW_KEY, VIEW_TYPE.SHARE)

// 分享页无侧栏，按窄屏推导设备类型
const BREAKPOINT = 768
const isMobile = ref(window.innerWidth < BREAKPOINT)
const onResize = () => (isMobile.value = window.innerWidth < BREAKPOINT)
provide(
  DEVICE_KEY,
  createDeviceType(() => (isMobile.value ? 'drawer' : 'push')),
)

onMounted(() => {
  window.addEventListener('resize', onResize)
  sharePanel.load()
})
onBeforeUnmount(() => window.removeEventListener('resize', onResize))
watch(() => props.shareId, sharePanel.load)
</script>

<template>
  <!-- share 视图自组装:provide 分享面板 store + 只读主面板 -->
  <div class="flex h-full overflow-hidden">
    <SharePanel />
  </div>
</template>

<style lang="scss">
@use '../../index.scss';
</style>
