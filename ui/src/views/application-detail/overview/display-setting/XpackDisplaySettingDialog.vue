<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ApplicationDisplaySetting } from '@/api/types'
import type { UploadFile } from 'element-plus'
import { useApplicationDetailContext } from '../../context'
import DisplaySettingPreview from './components/DisplaySettingPreview.vue'
import { APPLICATION_DISPLAY_SETTING_DEFAULT } from '@/constants/application'
import { LOCALE_OPTIONS } from '@/locales/config'
import { MsgError, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'XpackDisplaySettingDialog' })

const { t } = useI18n({ useScope: 'global' })

const { application, applicationId, resourceApi } = useApplicationDetailContext()
const visible = ref(false)
const loading = ref(false)

const displayForm = ref<ApplicationDisplaySetting>(cloneDeep(APPLICATION_DISPLAY_SETTING_DEFAULT))
type ImageField = 'icon' | 'chat_background' | 'avatar' | 'user_avatar' | 'float_icon'
const imageFields: {
  key: ImageField
  label: string
  visibility?: 'show_avatar' | 'show_user_avatar'
}[] = reactive([
  { key: 'icon', label: computed(() => `${t('application.title')} LOGO`) },
  { key: 'chat_background', label: computed(() => t('application.overview.display.background')) },
  { key: 'avatar', label: computed(() => t('application.overview.display.aiAvatar')), visibility: 'show_avatar' },
  { key: 'user_avatar', label: computed(() => t('application.overview.display.userAvatar')), visibility: 'show_user_avatar' },
  { key: 'float_icon', label: computed(() => t('application.overview.display.floatingIcon')) },
])

const imageFiles = ref<Partial<Record<ImageField, File>>>({})
const imagePreviews = ref<Partial<Record<ImageField, string>>>({})
const displayOptions = reactive([
  { key: 'show_source', label: computed(() => t('application.overview.display.showSource')) },
  { key: 'show_exec', label: computed(() => t('application.overview.display.showExecution')) },
  { key: 'show_history', label: computed(() => t('application.overview.display.showHistory')) },
  { key: 'show_share', label: computed(() => t('application.overview.display.allowShare')) },
  { key: 'disclaimer', label: computed(() => t('application.overview.display.disclaimer')) },
] as const)

function loadSetting() {
  if (loading.value) return
  loading.value = true
  return resourceApi.application
    .getDisplaySetting(applicationId.value)
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
    MsgError(t('upload.avatar.formatMessage'))
    return
  }
  if (image.size > 10 * 1024 * 1024) {
    MsgError(t('application.overview.display.imageSizeMessage', { size: 10 }))
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
      MsgSuccess(t('common.messages.settingsSuccess'))
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
    :title="t('application.overview.display.title')"
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
                <el-form-item :label="t('application.overview.display.themeColor')">
                  <el-color-picker v-model="displayForm.custom_theme.theme_color" />
                </el-form-item>
                <el-form-item :label="t('application.overview.display.headerFontColor')">
                  <el-color-picker v-model="displayForm.custom_theme.header_font_color" />
                </el-form-item>
              </div>
              <el-form-item :label="t('application.overview.display.language')">
                <el-select v-model="displayForm.language" clearable :placeholder="t('common.placeholders.select')">
                  <el-option v-for="language in LOCALE_OPTIONS" :key="language.value" :label="language.label" :value="language.value" />
                </el-select>
              </el-form-item>
              <div class="space-y-2">
                <template v-for="field in imageFields" :key="field.key">
                  <el-card class="small" shadow="never" style="--el-card-padding: 12px">
                    <div class="flex-between mb-2">
                      <span>{{ field.label }}</span>
                      <div class="flex-align-center gap-3">
                        <!-- 切换头像显示 -->
                        <el-checkbox v-if="field.visibility" v-model="displayForm[field.visibility]">
                          {{ t('application.overview.display.show') }}
                        </el-checkbox>
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
                      {{
                        field.key === 'chat_background'
                          ? t('application.overview.display.backgroundHint', { size: 10 })
                          : t('application.overview.display.imageHint', { dimensions: '24*24', size: 10 })
                      }}
                    </p>
                    <div v-if="field.key === 'float_icon'">
                      <el-divider class="my-3!" />
                      <div class="flex-between mb-2">
                        <span>{{ t('application.overview.display.iconPosition') }}</span>
                        <el-checkbox v-model="displayForm.draggable">{{ t('application.overview.display.draggable') }}</el-checkbox>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <div class="flex-align-center gap-2">
                          <div class="mk-input-group min-w-0 flex-1">
                            <!-- 选择横向定位方向 -->
                            <el-select v-model="displayForm.float_location.x.type" class="mk-input-group__prepend w-15! shrink-0">
                              <el-option :label="t('application.overview.display.left')" value="left" />
                              <el-option :label="t('application.overview.display.right')" value="right" />
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
                              <el-option :label="t('application.overview.display.top')" value="top" />
                              <el-option :label="t('application.overview.display.bottom')" value="bottom" />
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
                  <el-input
                    v-model="displayForm.disclaimer_value"
                    :maxlength="128"
                    :placeholder="t('application.overview.display.disclaimerPlaceholder')"
                    show-word-limit
                  />
                </div>
              </div>
            </el-form>
          </el-scrollbar>
          <footer>
            <div class="flex-between shrink-0 pt-6">
              <!-- 恢复默认展示配置 -->
              <el-button plain :disabled="loading" @click="handleRestoreDefault">
                <span>{{ t('application.overview.display.restoreDefault') }}</span>
              </el-button>
              <div class="flex-align-center">
                <!-- 取消展示设置 -->
                <el-button plain :disabled="loading" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
                <!-- 保存展示设置 -->
                <el-button type="primary" :loading="loading" @click="handleSave">{{ t('common.actions.save') }}</el-button>
              </div>
            </div>
          </footer>
        </section>
      </div>
    </div>
  </MkDialog>
</template>
