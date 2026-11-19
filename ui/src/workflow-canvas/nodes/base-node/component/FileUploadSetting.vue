<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { FileUploadSettingData } from '../types'
import type { FormInstance, FormRules } from 'element-plus'
import audioIcon from '@/assets/file-type/file-audio-icon.svg'
import documentIcon from '@/assets/file-type/file-document-icon.svg'
import imageIcon from '@/assets/file-type/file-image-icon.svg'
import videoIcon from '@/assets/file-type/file-video-icon.svg'
import MkTagsEdit from '@/components/mk-tags-edit/index.vue'
import { defaultFileUploadSetting } from '../constant'
import { AUDIO_EXTENSIONS, DOCUMENT_EXTENSIONS, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS } from '@/constants/file-type'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'BaseNodeFileUploadSetting' })

const setting = defineModel<FileUploadSettingData>({ required: true })

// 文件上传设置：打开时创建草稿，确认后回写配置。
const visible = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const formData = ref<FileUploadSettingData>(cloneDeep(defaultFileUploadSetting))
const rules: FormRules<FileUploadSettingData> = {
  local_upload: [
    {
      required: true,
      trigger: 'change',
      validator: (_rule, _value, callback) => {
        callback(formData.value.local_upload || formData.value.url_upload ? undefined : new Error(t('application.fileUpload.method.requiredMessage')))
      },
    },
  ],
}

const fileTypes = reactive([
  { field: 'document', label: computed(() => t('upload.types.document')), icon: documentIcon, extensions: DOCUMENT_EXTENSIONS },
  { field: 'image', label: computed(() => t('upload.types.image')), icon: imageIcon, extensions: IMAGE_EXTENSIONS },
  { field: 'audio', label: computed(() => t('upload.types.audio')), icon: audioIcon, extensions: AUDIO_EXTENSIONS },
  { field: 'video', label: computed(() => t('upload.types.video')), icon: videoIcon, extensions: VIDEO_EXTENSIONS },
] as const)

const presetExtensions = fileTypes.flatMap(({ extensions }) => extensions)

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    setting.value = cloneDeep(formData.value)
    visible.value = false
  })
}

function open() {
  formData.value = cloneDeep(setting.value)
  visible.value = true
}

function resetData() {
  formData.value = cloneDeep(defaultFileUploadSetting)
  formRef.value?.clearValidate()
}
</script>

<template>
  <!-- 打开文件上传设置 -->
  <el-button text type="primary" @click="open">
    <MkIcon name="icon_setting" />
  </el-button>
  <MkDialog v-model="visible" :title="t('application.fileUpload.title')" @closed="resetData">
    <el-form
      :validate-on-rule-change="false"
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('application.fileUpload.method.label')" prop="local_upload">
        <div class="flex w-full flex-wrap gap-6">
          <el-checkbox v-model="formData.local_upload">{{ t('application.fileUpload.method.local') }}</el-checkbox>
          <el-checkbox v-model="formData.url_upload">{{ t('application.fileUpload.method.url') }}</el-checkbox>
        </div>
      </el-form-item>
      <el-form-item :label="t('application.fileUpload.maxFiles')">
        <MkSlider v-model="formData.maxFiles" :max="100" :min="1" />
      </el-form-item>

      <el-form-item :label="`${t('application.fileUpload.fileSize')} (MB)`">
        <MkSlider v-model="formData.fileLimit" :max="1000" :min="1" />
      </el-form-item>

      <el-form-item :label="t('application.fileUpload.allowedTypes')">
        <div class="w-full space-y-2">
          <template v-for="fileType in fileTypes" :key="fileType.field">
            <MkCardCheckbox v-model="formData[fileType.field]" :label="fileType.label">
              <div class="flex-align-center min-w-0 gap-3">
                <img class="shrink-0 w-6" :src="fileType.icon" :alt="fileType.label" />
                <div class="min-w-0 flex-1">
                  <h6>{{ fileType.label }}</h6>
                  <p class="mt-1 break-all text-sm text-N600">{{ fileType.extensions.join('、') }}</p>
                </div>
              </div>
            </MkCardCheckbox>
          </template>

          <MkCardCheckbox v-model="formData.other" :label="t('upload.types.other')">
            <div class="flex-align-center min-w-0 gap-3">
              <img class="shrink-0 w-6" src="@/assets/file-type/unknown-icon.svg" />
              <div class="min-w-0 flex-1">
                <h6 class="mb-2">{{ t('upload.types.other') }}</h6>
                <MkTagsEdit v-model="formData.otherExtensions" :preset-extensions="presetExtensions" />
              </div>
            </div>
          </MkCardCheckbox>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <!-- 取消设置 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存文件上传设置 -->
      <el-button type="primary" @click="submit">{{ t('common.actions.confirm') }}</el-button>
    </template>
  </MkDialog>
</template>
