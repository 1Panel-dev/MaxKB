<script setup lang="ts">
import { computed } from 'vue'
import type { CSSProperties } from 'vue'
import type { ApplicationDisplaySetting } from '@/api/types'

defineOptions({ name: 'DisplaySettingPreview' })

const props = withDefaults(
  defineProps<{
    applicationName?: string
    setting: ApplicationDisplaySetting
    imagePreviews: Partial<Pick<ApplicationDisplaySetting, 'icon' | 'chat_background' | 'avatar' | 'user_avatar' | 'float_icon'>>
  }>(),
  { applicationName: '智能体名称' },
)

// 本次替换的图片优先展示，否则使用草稿中的已有地址。
const previewImages = computed(() => ({
  icon: props.imagePreviews.icon || props.setting.icon,
  chat_background: props.imagePreviews.chat_background || props.setting.chat_background,
  avatar: props.imagePreviews.avatar || props.setting.avatar,
  user_avatar: props.imagePreviews.user_avatar || props.setting.user_avatar,
  float_icon: props.imagePreviews.float_icon || props.setting.float_icon,
}))

// 仅展示配置草稿，不修改表单或发送对话请求。
const previewHeaderStyle = computed<CSSProperties>(() => ({
  background: `color-mix(in srgb, ${props.setting.custom_theme.theme_color || '#3370ff'} 5%, var(--mk-N100))`,
  color: props.setting.custom_theme.header_font_color || undefined,
}))
</script>

<template>
  <div class="mk-gray-card-lg flex h-full items-end gap-2 overflow-hidden">
    <div class="flex-column h-full min-w-0 flex-1 overflow-hidden border border-N300 bg-white shadow-lg rounded-xl">
      <header class="flex-between h-header shrink-0 gap-4 border-b border-N300 p-4" :style="previewHeaderStyle">
        <div class="flex-align-center min-w-0 flex-1 gap-2">
          <MkIcon name="icon_sidebar_outlined" :size="18" class="mr-2 shrink-0" />
          <ApplicationIcon :icon="previewImages.icon" :size="24" class="shrink-0" />
          <h6 class="truncate" :title="applicationName">{{ applicationName }}</h6>
        </div>
        <div class="flex-align-center shrink-0 gap-4">
          <MkIcon name="icon_new-chat_outlined" :size="18" />
          <MkIcon name="icon_close_outlined" :size="18" />
        </div>
      </header>
      <div
        class="flex-column flex-1 bg-cover bg-center p-4"
        :style="{ backgroundImage: previewImages.chat_background ? `url(${JSON.stringify(previewImages.chat_background)})` : undefined }"
      >
        <div class="space-y-3">
          <ApplicationIcon v-if="setting.show_avatar" :icon="previewImages.avatar" :size="24" />

          <div class="h-3.5 rounded bg-N100"></div>
          <div class="h-3.5 rounded bg-N100"></div>
          <div class="h-3.5 w-1/2 rounded bg-N100"></div>
        </div>
        <div class="mt-8 flex-column items-end gap-3">
          <div v-if="setting.show_user_avatar" class="flex">
            <el-avatar v-if="previewImages.user_avatar" class="bg-transparent!" shape="square" :size="24">
              <img :src="previewImages.user_avatar" alt="" />
            </el-avatar>
            <el-avatar v-else :size="24" :style="{ background: setting.custom_theme.theme_color || 'var(--mk-primary-gradient)' }">
              <img src="@/assets/mk_icon_user_gradient.svg" alt="" style="width: 50%" />
            </el-avatar>
          </div>

          <div class="h-8.5 w-2/3 rounded-xl bg-N100"></div>
        </div>
        <div class="mt-auto space-y-2">
          <div class="mk-input-box flex h-23 items-end justify-end border border-N350/60 shadow-lg">
            <!-- 预览发送按钮 -->
            <el-button circle disabled type="primary">
              <MkIcon name="icon_arrow-up_outlined" :size="18" />
            </el-button>
          </div>
          <p v-if="setting.disclaimer" class="wrap-anywhere text-center text-sm text-N500 -mb-1">{{ setting.disclaimer_value }}</p>
        </div>
      </div>
    </div>
    <!-- 浮窗图标 -->
    <img :src="previewImages.float_icon || '/MaxKB.gif'" alt="" class="size-8 shrink-0 object-contain" />
  </div>
</template>
