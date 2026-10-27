<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import type { UploadFile } from 'element-plus'
import { cloneDeep } from 'lodash'
import type { ApplicationDisplaySetting } from '@/api/types'
import { MsgError, MsgSuccess } from '@/utils/message'
import { useApplicationDetailContext } from '../../context'
import DisplaySettingPreview from './components/DisplaySettingPreview.vue'
import { APPLICATION_DISPLAY_SETTING_DEFAULT } from '@/constants/application'
import ApplicationApi from '@/api/admin/workspace/application/application'

defineOptions({ name: 'XpackDisplaySettingDialog' })

const { application, applicationId, resourceApi } = useApplicationDetailContext()
const visible = ref(false)
const loading = ref(false)

const displayForm = ref<ApplicationDisplaySetting>(cloneDeep(APPLICATION_DISPLAY_SETTING_DEFAULT))
type ImageField = 'icon' | 'chat_background' | 'avatar' | 'user_avatar' | 'float_icon'
const imageFields: {
  key: ImageField
  label: string
  visibility?: 'show_avatar' | 'show_user_avatar'
}[] = [
  { key: 'icon', label: '智能体 LOGO' },
  { key: 'chat_background', label: '聊天背景' },
  { key: 'avatar', label: 'AI 回复头像', visibility: 'show_avatar' },
  { key: 'user_avatar', label: '提问用户头像', visibility: 'show_user_avatar' },
  { key: 'float_icon', label: '浮窗入口图标' },
]

const imageFiles = ref<Partial<Record<ImageField, File>>>({})
const imagePreviews = ref<Partial<Record<ImageField, string>>>({})
const displayOptions = [
  { key: 'show_source', label: '显示知识来源' },
  { key: 'show_exec', label: '显示执行详情' },
  { key: 'show_history', label: '显示历史记录' },
  { key: 'show_share', label: '允许分享对话记录' },
  { key: 'disclaimer', label: '免责声明' },
] as const
const languageOptions = [
  { value: 'zh-CN', label: '简体中文' },
  { value: 'zh-Hant', label: '繁體中文' },
  { value: 'en-US', label: 'English' },
]

function loadSetting() {
  if (loading.value) return
  loading.value = true
  return ApplicationApi.getDisplaySetting(applicationId.value)
    .then((config) => {
      // 旧版接口可能省略展示字段，嵌套配置分别补齐默认值。
      const setting: ApplicationDisplaySetting = cloneDeep(APPLICATION_DISPLAY_SETTING_DEFAULT)
      for (const key of Object.keys(setting) as (keyof ApplicationDisplaySetting)[]) {
        if (config[key] != null) Object.assign(setting, { [key]: cloneDeep(config[key]) })
      }
      setting.custom_theme = { ...APPLICATION_DISPLAY_SETTING_DEFAULT.custom_theme, ...config.custom_theme }
      setting.float_location = {
        x: { ...APPLICATION_DISPLAY_SETTING_DEFAULT.float_location.x, ...config.float_location?.x },
        y: { ...APPLICATION_DISPLAY_SETTING_DEFAULT.float_location.y, ...config.float_location?.y },
      }
      displayForm.value = setting
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
  if (!image || loading.value) return
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
  if (loading.value) return
  releaseImagePreviews()
  displayForm.value = cloneDeep(APPLICATION_DISPLAY_SETTING_DEFAULT)
}

function handleClosed() {
  releaseImagePreviews()
  displayForm.value = cloneDeep(APPLICATION_DISPLAY_SETTING_DEFAULT)
}

// 对照 V2 协议提交文件、已有图片 URL 和嵌套 JSON，失败保留当前草稿。
function handleSave() {
  if (loading.value) return
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
  loading.value = true
  return resourceApi.application
    .putDisplaySetting(applicationId.value, payload)
    .then(() => {
      MsgSuccess('设置成功')
      visible.value = false
    })
    .finally(() => {
      loading.value = false
    })
}

defineExpose({ open })
onBeforeUnmount(releaseImagePreviews)
</script>

<template>
  <MkDialog
    v-model="visible"
    title="显示设置"
    class="mk-aside-content-dialog"
    body-class="border-t-0!"
    content-class="overflow-hidden"
    :width="1000"
    @closed="handleClosed"
  >
    <div v-loading="loading" class="h-full p-6 pt-0">
      <div class="grid h-full grid-cols-2 gap-6">
        <section class="min-h-0 min-w-0">
          <DisplaySettingPreview :application-name="application?.name" :setting="displayForm" :image-previews="imagePreviews" />
        </section>
        <section class="flex-column min-h-0 min-w-0">
          <el-scrollbar class="min-h-0 flex-1 -mr-6" view-class="pr-6">
            <el-form :model="displayForm" label-position="top" require-asterisk-position="right" @submit.prevent>
              <div class="grid grid-cols-2 gap-4">
                <el-form-item label="自定义主题色">
                  <el-color-picker v-model="displayForm.custom_theme.theme_color" />
                </el-form-item>
                <el-form-item label="头部标题字体颜色"><el-color-picker v-model="displayForm.custom_theme.header_font_color" /></el-form-item>
              </div>
              <el-form-item label="语言">
                <el-select v-model="displayForm.language" clearable placeholder="请选择">
                  <el-option v-for="language in languageOptions" :key="language.value" :label="language.label" :value="language.value" />
                </el-select>
              </el-form-item>
              <div class="space-y-2">
                <template v-for="field in imageFields" :key="field.key">
                  <el-card class="small" shadow="never" style="--el-card-padding: 12px">
                    <div class="flex-between mb-2">
                      <span>{{ field.label }}</span>
                      <div class="flex-align-center gap-3">
                        <!-- 切换头像显示 -->
                        <el-checkbox v-if="field.visibility" v-model="displayForm[field.visibility]">显示</el-checkbox>
                        <!-- 替换当前展示图片 -->
                        <el-upload
                          action="#"
                          :auto-upload="false"
                          :show-file-list="false"
                          accept="image/jpeg,image/png,image/gif"
                          :on-change="(file: UploadFile) => handleImageChange(file, field.key)"
                        >
                          <el-button plain class="shrink-0 min-w-7.5! w-7.5!">
                            <MkIcon name="icon_upload_outlined" :size="14" />
                          </el-button>
                        </el-upload>
                      </div>
                    </div>
                    <p class="text-sm text-N500">
                      {{ field.key === 'chat_background' ? '' : '建议尺寸 24*24，' }}支持 JPG、PNG、GIF，大小不超过 10 MB
                    </p>
                    <div v-if="field.key === 'float_icon'">
                      <el-divider class="my-3!" />
                      <div class="flex-between mb-2">
                        <span>图标默认位置</span>
                        <el-checkbox v-model="displayForm.draggable">可拖拽位置</el-checkbox>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <div class="flex-align-center gap-2">
                          <div class="mk-input-group min-w-0 flex-1">
                            <!-- 选择横向定位方向 -->
                            <el-select v-model="displayForm.float_location.x.type" class="mk-input-group__prepend w-15! shrink-0">
                              <el-option label="左" value="left" />
                              <el-option label="右" value="right" />
                            </el-select>
                            <!-- 设置横向偏移量 -->
                            <el-input-number
                              v-model="displayForm.float_location.x.value"
                              class="mk-input-group__content min-w-0 flex-1"
                              :min="0"
                              :step="1"
                              :precision="0"
                              :value-on-clear="0"
                              step-strictly
                              controls-position="right"
                              align="left"
                            />
                          </div>
                          <span>px</span>
                        </div>
                        <div class="flex-align-center gap-1">
                          <div class="mk-input-group min-w-0 flex-1">
                            <!-- 选择纵向定位方向 -->
                            <el-select v-model="displayForm.float_location.y.type" class="mk-input-group__prepend w-15! shrink-0">
                              <el-option label="上" value="top" />
                              <el-option label="下" value="bottom" />
                            </el-select>
                            <!-- 设置纵向偏移量 -->
                            <el-input-number
                              v-model="displayForm.float_location.y.value"
                              class="mk-input-group__content min-w-0 flex-1"
                              :min="0"
                              :step="1"
                              :precision="0"
                              :value-on-clear="0"
                              step-strictly
                              controls-position="right"
                              align="left"
                            />
                          </div>
                          <span>px</span>
                        </div>
                      </div>
                    </div>
                  </el-card>
                </template>
              </div>
              <div class="mt-3 flex-column gap-2">
                <el-checkbox v-for="option in displayOptions" :key="option.key" v-model="displayForm[option.key]">{{ option.label }}</el-checkbox>
                <div v-if="displayForm.disclaimer" class="ml-6">
                  <el-input v-model="displayForm.disclaimer_value" :maxlength="128" placeholder="请输入免责声明" show-word-limit />
                </div>
              </div>
            </el-form>
          </el-scrollbar>
          <footer>
            <div class="flex-between shrink-0 pt-6">
              <!-- 恢复默认展示配置 -->
              <el-button plain :disabled="loading" @click="handleRestoreDefault">
                <span>恢复默认</span>
              </el-button>
              <div class="flex-align-center">
                <!-- 取消展示设置 -->
                <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
                <!-- 保存展示设置 -->
                <el-button type="primary" :loading="loading" @click="handleSave">保存</el-button>
              </div>
            </div>
          </footer>
        </section>
      </div>
    </div>
  </MkDialog>
</template>
