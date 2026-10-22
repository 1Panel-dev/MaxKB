<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import type { CSSProperties } from 'vue'
import type { UploadFile } from 'element-plus'
import { ChatDotRound, Clock, Close, Expand, Promotion, Refresh, User } from '@element-plus/icons-vue'
import { cloneDeep } from 'lodash'
import type { ApplicationDisplaySetting } from '@/api/types'
import { MsgError, MsgSuccess } from '@/utils/message'
import { useApplicationDetailContext } from '../../context'

defineOptions({ name: 'DisplaySettingDialog' })

const { application, applicationId, resourceApi } = useApplicationDetailContext()
const visible = ref(false)
const loading = ref(false)
const saving = ref(false)
const loaded = ref(false)

// 展示草稿与恢复默认；只在保存时提交，取消不回写配置。
const defaultSetting: ApplicationDisplaySetting = {
  show_source: false,
  show_exec: false,
  language: '',
  show_history: true,
  draggable: true,
  show_guide: true,
  show_share: true,
  icon: '',
  chat_background: '',
  avatar: '',
  float_icon: '',
  user_avatar: '',
  disclaimer: false,
  disclaimer_value: '「以上内容均由 AI 生成，仅供参考和借鉴」',
  custom_theme: { theme_color: '', header_font_color: '#1f2329' },
  float_location: { x: { type: 'right', value: 0 }, y: { type: 'bottom', value: 30 } },
  show_avatar: true,
  show_user_avatar: false,
}
const displayForm = ref(cloneDeep(defaultSetting))
const imageFields = [
  { key: 'icon', label: '智能体 LOGO' },
  { key: 'chat_background', label: '聊天背景' },
  { key: 'avatar', label: 'AI 回复头像', visibility: 'show_avatar' },
  { key: 'user_avatar', label: '提问用户头像', visibility: 'show_user_avatar' },
  { key: 'float_icon', label: '浮窗入口图标' },
] as const

type ImageField = (typeof imageFields)[number]['key']
const imageFiles = ref<Partial<Record<ImageField, File>>>({})
const imagePreviews = ref<Partial<Record<ImageField, string>>>({})
const displayOptions = [
  { key: 'show_source', label: '显示知识来源' },
  { key: 'show_exec', label: '显示执行详情' },
  { key: 'show_history', label: '显示历史记录' },
  { key: 'show_guide', label: '显示引导图（浮窗模式）' },
  { key: 'show_share', label: '允许分享对话记录' },
  { key: 'disclaimer', label: '免责声明' },
] as const
const languageOptions = [
  { value: 'zh-CN', label: '简体中文' },
  { value: 'zh-Hant', label: '繁體中文' },
  { value: 'en-US', label: 'English' },
]

function loadSetting() {
  if (loading.value || saving.value) return
  loading.value = true
  return resourceApi.application
    .getAccessToken(applicationId.value)
    .then((config) => {
      // 老版本和社区版可能省略展示字段，嵌套配置分别补齐默认值。
      const setting = cloneDeep(defaultSetting)
      for (const key of Object.keys(setting) as (keyof ApplicationDisplaySetting)[]) {
        if (config[key] != null) Object.assign(setting, { [key]: cloneDeep(config[key]) })
      }
      setting.custom_theme = { ...defaultSetting.custom_theme, ...config.custom_theme }
      setting.float_location = {
        x: { ...defaultSetting.float_location.x, ...config.float_location?.x },
        y: { ...defaultSetting.float_location.y, ...config.float_location?.y },
      }
      displayForm.value = setting
      loaded.value = true
    })
    .finally(() => {
      loading.value = false
    })
}

function open() {
  visible.value = true
  return loadSetting()
}

// 图片只在本地预览；替换、恢复默认和关闭时释放临时 URL。
function releaseImagePreviews() {
  Object.values(imagePreviews.value).forEach((url) => URL.revokeObjectURL(url))
  imagePreviews.value = {}
  imageFiles.value = {}
}

function handleImageChange(file: UploadFile, field: ImageField) {
  const image = file.raw
  if (!image) return
  if (!['image/jpeg', 'image/png', 'image/gif'].includes(image.type)) {
    MsgError('仅支持 JPG、PNG、GIF 格式的图片')
    return
  }
  if (image.size > 10 * 1024 * 1024) {
    MsgError('图片大小不能超过 10 MB')
    return
  }
  const previousPreview = imagePreviews.value[field]
  if (previousPreview) URL.revokeObjectURL(previousPreview)
  imageFiles.value[field] = image
  imagePreviews.value[field] = URL.createObjectURL(image)
  displayForm.value[field] = ''
}

function handleRestoreDefault() {
  releaseImagePreviews()
  displayForm.value = cloneDeep(defaultSetting)
}

function handleClosed() {
  releaseImagePreviews()
  displayForm.value = cloneDeep(defaultSetting)
  loaded.value = false
}

onBeforeUnmount(releaseImagePreviews)

// 对照 V2 协议提交文件、已有图片 URL 和嵌套 JSON，失败保留当前草稿。
function handleSave() {
  if (!loaded.value || loading.value || saving.value) return
  const payload = new FormData()
  const imageKeys = imageFields.map((field) => field.key)
  for (const [key, value] of Object.entries(displayForm.value)) {
    if (imageKeys.includes(key as ImageField)) {
      const field = key as ImageField
      payload.append(field, imageFiles.value[field] ?? '')
      payload.append(`${field}_url`, value as string)
    } else {
      payload.append(key, typeof value === 'object' ? JSON.stringify(value) : String(value ?? ''))
    }
  }
  saving.value = true
  return resourceApi.application
    .putDisplaySetting(applicationId.value, payload)
    .then(() => {
      MsgSuccess('设置成功')
      visible.value = false
    })
    .finally(() => {
      saving.value = false
    })
}

// 预览使用本地草稿，不发送实际对话请求。
const previewImages = computed(
  () => Object.fromEntries(imageFields.map(({ key }) => [key, imagePreviews.value[key] || displayForm.value[key]])) as Record<ImageField, string>,
)
const previewHeaderStyle = computed<CSSProperties>(() => ({
  backgroundColor: displayForm.value.custom_theme.theme_color || undefined,
  color: displayForm.value.custom_theme.header_font_color || undefined,
}))
const floatingIconStyle = computed<CSSProperties>(() => {
  const { x, y } = displayForm.value.float_location
  return {
    [x.type]: `clamp(0px, ${x.value}px, calc(100% - 40px))`,
    [y.type]: `clamp(0px, ${y.value}px, calc(100% - 40px))`,
  }
})

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="显示设置" align-center class="mk-aside-content-dialog" :width="1000" @closed="handleClosed">
    <div v-loading="loading" class="min-h-60">
      <div v-if="loaded" class="grid gap-6 grid-cols-2" :inert="saving">
        <div class="relative">
          <div class="flex-column h-full overflow-hidden rounded-xl border border-N200 bg-white shadow-lg">
            <div class="flex-between gap-3 border-b border-N200 bg-N100 px-4 py-3" :style="previewHeaderStyle">
              <div class="flex-align-center min-w-0 gap-2">
                <ApplicationIcon :icon="previewImages.icon" :size="28" />
                <h6 class="truncate" :title="application?.name || '智能体名称'">{{ application?.name || '智能体名称' }}</h6>
              </div>
              <div class="flex-align-center gap-3">
                <MkIcon v-if="displayForm.show_history" :icon="Clock" />
                <MkIcon :icon="Expand" />
                <MkIcon :icon="Close" />
              </div>
            </div>
            <div
              class="flex-column flex-1 gap-4 bg-cover bg-center p-4"
              :style="{ backgroundImage: previewImages.chat_background ? `url(${JSON.stringify(previewImages.chat_background)})` : undefined }"
            >
              <div class="flex gap-2">
                <ApplicationIcon v-if="displayForm.show_avatar" :icon="previewImages.avatar" :size="28" class="shrink-0" />
                <div class="min-w-0 space-y-2">
                  <div class="mk-gray-card">你好，我是你的 AI 助手，有什么可以帮你？</div>
                  <span v-if="displayForm.show_source" class="text-sm text-N600">知识来源 · 示例文档</span>
                  <span v-if="displayForm.show_exec" class="block text-sm text-N600">执行详情 · 已完成</span>
                </div>
              </div>
              <div class="flex justify-end gap-2">
                <div class="mk-gray-card h-fit">你好，介绍一下你的功能。</div>
                <el-avatar v-if="displayForm.show_user_avatar" :src="previewImages.user_avatar || undefined" :size="28" class="shrink-0">
                  <MkIcon :icon="User" />
                </el-avatar>
              </div>
              <div class="mt-auto space-y-2">
                <div v-if="displayForm.show_share" class="flex justify-end text-N600"><MkIcon :icon="Promotion" /></div>
                <div class="rounded-xl border border-N200 bg-white p-3 text-N600">请输入问题…</div>
                <p v-if="displayForm.disclaimer" class="wrap-anywhere text-center text-sm text-N600">{{ displayForm.disclaimer_value }}</p>
              </div>
            </div>
          </div>
          <div class="absolute" :style="floatingIconStyle">
            <div
              v-if="displayForm.show_guide"
              class="absolute right-0 bottom-12 w-max rounded-lg border border-N200 bg-white px-3 py-1 text-sm shadow-sm"
            >
              你好，有什么可以帮你？
            </div>
            <el-avatar :src="previewImages.float_icon || undefined" :size="40" class="bg-primary! text-white!">
              <MkIcon :icon="ChatDotRound" :size="24" />
            </el-avatar>
          </div>
        </div>
        <div>
          <el-scrollbar max-height="568px">
            <el-form :model="displayForm" label-position="top" class="pr-3" @submit.prevent>
              <div class="grid grid-cols-2 gap-4">
                <el-form-item label="自定义主题色">
                  <div class="flex-align-center gap-2">
                    <el-color-picker v-model="displayForm.custom_theme.theme_color" />
                    <span v-if="!displayForm.custom_theme.theme_color" class="text-N600">默认</span>
                  </div>
                </el-form-item>
                <el-form-item label="头部标题字体颜色"><el-color-picker v-model="displayForm.custom_theme.header_font_color" /></el-form-item>
              </div>
              <el-form-item label="语言">
                <el-select v-model="displayForm.language" clearable placeholder="跟随系统">
                  <el-option v-for="language in languageOptions" :key="language.value" :label="language.label" :value="language.value" />
                </el-select>
              </el-form-item>
              <div class="space-y-3">
                <template v-for="field in imageFields" :key="field.key">
                  <div class="rounded-lg border border-N200 p-3">
                    <div class="flex-between gap-3">
                      <h6>{{ field.label }}</h6>
                      <div class="flex-align-center gap-3">
                        <el-checkbox v-if="'visibility' in field" v-model="displayForm[field.visibility]">显示</el-checkbox>
                        <!-- 替换当前展示图片 -->
                        <el-upload
                          action="#"
                          :auto-upload="false"
                          :show-file-list="false"
                          accept="image/jpeg,image/png,image/gif"
                          :on-change="(file: UploadFile) => handleImageChange(file, field.key)"
                        >
                          <el-button size="small">替换</el-button>
                        </el-upload>
                      </div>
                    </div>
                    <p class="mt-2 text-sm text-N600">
                      {{ field.key === 'chat_background' ? '' : '建议尺寸 32 × 32，' }}支持 JPG、PNG、GIF，大小不超过 10 MB
                    </p>
                    <div v-if="field.key === 'float_icon'" class="mt-3 border-t border-N200 pt-3">
                      <div class="flex-between mb-2">
                        <span>图标默认位置</span>
                        <el-checkbox v-model="displayForm.draggable">可拖拽位置</el-checkbox>
                      </div>
                      <div class="grid grid-cols-2 gap-3">
                        <div class="flex-align-center gap-1">
                          <el-select v-model="displayForm.float_location.x.type" class="w-17! shrink-0">
                            <el-option label="左" value="left" />
                            <el-option label="右" value="right" />
                          </el-select>
                          <el-input-number
                            v-model="displayForm.float_location.x.value"
                            class="min-w-0! w-full!"
                            :min="0"
                            :precision="0"
                            :value-on-clear="0"
                            controls-position="right"
                            align="left"
                          />
                          <span>px</span>
                        </div>
                        <div class="flex-align-center gap-1">
                          <el-select v-model="displayForm.float_location.y.type" class="w-17! shrink-0">
                            <el-option label="上" value="top" />
                            <el-option label="下" value="bottom" />
                          </el-select>
                          <el-input-number
                            v-model="displayForm.float_location.y.value"
                            class="min-w-0! w-full!"
                            :min="0"
                            :precision="0"
                            :value-on-clear="0"
                            controls-position="right"
                            align="left"
                          />
                          <span>px</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
              <div class="mt-3 flex-column items-start">
                <el-checkbox v-for="option in displayOptions" :key="option.key" v-model="displayForm[option.key]">{{ option.label }}</el-checkbox>
                <el-input v-if="displayForm.disclaimer" v-model="displayForm.disclaimer_value" :maxlength="128" placeholder="请输入免责声明" />
              </div>
            </el-form>
          </el-scrollbar>
          <el-button link :disabled="!loaded || loading || saving" @click="handleRestoreDefault">
            <MkIcon :icon="Refresh" />
            <span>恢复默认</span>
          </el-button>
          <!-- 取消展示设置 -->
          <el-button :disabled="loading || saving" @click="visible = false">取消</el-button>
          <!-- 保存展示设置 -->
          <el-button type="primary" :loading="saving" :disabled="!loaded || loading" @click="handleSave">保存</el-button>
        </div>
      </div>
    </div>
  </MkDialog>
</template>
