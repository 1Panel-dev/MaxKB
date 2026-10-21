<script setup lang="ts">
import { computed, ref } from 'vue'
import { escape } from 'lodash'
import { CHAT_API_BASE_PATH } from '@/api/constants'
import { copyText } from '@/utils/clipboard'
import fullscreenImage from '@/assets/application/embed-fullscreen.png'
import floatingImage from '@/assets/application/embed-floating.png'
import mobileImage from '@/assets/application/embed-mobile.png'

defineOptions({ name: 'EmbedThirdPartyDialog' })

const props = defineProps<{ shareUrl: string; accessToken: string }>()
const visible = ref(false)
const selectedMode = ref<'fullscreen' | 'floating' | 'mobile'>('fullscreen')
const embedModes = [
  { value: 'fullscreen', label: '全屏模式', image: fullscreenImage },
  { value: 'floating', label: '浮窗模式', image: floatingImage },
  { value: 'mobile', label: '移动端模式', image: mobileImage },
] as const

const embedCode = computed(() => {
  if (!props.shareUrl || !props.accessToken) return ''
  const chatUrl = new URL(props.shareUrl)

  if (selectedMode.value === 'floating') {
    const embedUrl = new URL(`${CHAT_API_BASE_PATH}/embed`, window.location.origin)
    embedUrl.search = new URLSearchParams({
      protocol: window.location.protocol.replace(':', ''),
      host: window.location.host,
      token: props.accessToken,
    }).toString()
    // 复用访问链接的工作流参数，由 URLSearchParams 编码，不再手动编码。
    chatUrl.searchParams.forEach((value, key) => embedUrl.searchParams.append(key, value))
    return `<script
async
defer
src="${escape(embedUrl.href)}">
<\/script>`
  }

  if (selectedMode.value === 'mobile') chatUrl.searchParams.set('mode', 'mobile')
  return `<iframe
src="${escape(chatUrl.href)}"
style="width: 100%; height: 100%;"
frameborder="0"
allow="microphone">
</iframe>`
})

function open() {
  visible.value = true
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="嵌入第三方" :width="840" @closed="selectedMode = 'fullscreen'">
    <div class="space-y-4">
      <div class="grid grid-cols-3 gap-4">
        <template v-for="mode in embedModes" :key="mode.value">
          <!-- 切换嵌入模式 -->
          <el-card
            shadow="never"
            class="cursor-pointer text-center"
            :class="{ 'border-primary! bg-primary/10!': selectedMode === mode.value }"
            role="button"
            tabindex="0"
            :aria-pressed="selectedMode === mode.value"
            @click="selectedMode = mode.value"
            @keydown.enter.prevent="selectedMode = mode.value"
            @keydown.space.prevent="selectedMode = mode.value"
          >
            <div class="space-y-2">
              <div>{{ mode.label }}</div>
              <img :src="mode.image" alt="" class="mx-auto h-28 object-contain" />
            </div>
          </el-card>
        </template>
      </div>
      <div class="mk-gray-card-lg space-y-2">
        <div class="flex-between">
          <h6>复制以下代码进行嵌入</h6>
          <!-- 复制当前模式的嵌入代码 -->
          <MkTooltip content="复制">
            <el-button text :disabled="!embedCode" @click="copyText(embedCode)">
              <MkIcon name="icon_copy_outlined" />
            </el-button>
          </MkTooltip>
        </div>
        <div class="whitespace-pre-wrap break-all">{{ embedCode }}</div>
      </div>
    </div>
  </MkDialog>
</template>
