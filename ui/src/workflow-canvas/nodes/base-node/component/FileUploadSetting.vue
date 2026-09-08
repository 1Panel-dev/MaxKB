<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import documentIcon from '@/assets/file-type/file-document-icon.svg'
import imageIcon from '@/assets/file-type/file-image-icon.svg'
import audioIcon from '@/assets/file-type/file-audio-icon.svg'
import videoIcon from '@/assets/file-type/file-video-icon.svg'
import MkCardCheckbox from '@/components/mk-card-checkbox/index.vue'
import MkTagsEdit from '@/components/mk-tags-edit/index.vue'
import { defaultFileUploadSetting } from '../constant'
import type { FileUploadSettingData } from '../types'

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
        callback(formData.value.local_upload || formData.value.url_upload ? undefined : new Error('请至少选择一种上传方式'))
      },
    },
  ],
}

const fileTypes = [
  { field: 'document', label: '文档', icon: documentIcon, description: 'TXT、MD、DOCX、HTML、CSV、XLSX、XLS、PDF' },
  { field: 'image', label: '图片', icon: imageIcon, description: 'JPG、JPEG、PNG、GIF' },
  { field: 'audio', label: '音频', icon: audioIcon, description: 'MP3、WAV、OGG、AAC、M4A' },
  { field: 'video', label: '视频', icon: videoIcon, description: 'MP4、AVI、MKV、MOV、FLV、WMV' },
] as const

const reservedExtensions = fileTypes.flatMap(({ description }) => description.split('、'))

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    setting.value = cloneDeep(formData.value)
    visible.value = false
  })
}

function open() {
  resetData()
  formData.value = cloneDeep(setting.value)
  visible.value = true
}

function resetData() {
  formData.value = cloneDeep(defaultFileUploadSetting)
  formRef.value?.clearValidate()
}
</script>

<template>
  <el-button text type="primary" @click="open">
    <MkIcon name="icon-setting" />
  </el-button>
  <MkDialog v-model="visible" title="文件上传设置" @closed="resetData" align-center>
    <el-form ref="formRef" :model="formData" :rules="rules" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="上传方式" prop="local_upload">
        <div class="flex w-full flex-wrap gap-6">
          <el-checkbox v-model="formData.local_upload">本地上传</el-checkbox>
          <el-checkbox v-model="formData.url_upload">URL 上传</el-checkbox>
        </div>
      </el-form-item>
      <el-form-item label="单次最多上传文件数">
        <MkSlider v-model="formData.maxFiles" :max="100" :min="1" />
      </el-form-item>

      <el-form-item label="每个文件最大 (MB)">
        <MkSlider v-model="formData.fileLimit" :max="1000" :min="1" />
      </el-form-item>

      <el-form-item label="允许上传的文件类型">
        <div class="w-full space-y-2">
          <template v-for="fileType in fileTypes" :key="fileType.field">
            <MkCardCheckbox v-model="formData[fileType.field]" :label="fileType.label">
              <div class="flex min-w-0 items-center gap-3">
                <img class="shrink-0 w-6" :src="fileType.icon" :alt="fileType.label" />
                <div class="min-w-0 flex-1">
                  <h6>{{ fileType.label }}</h6>
                  <p class="mt-1 break-all text-sm text-N600">{{ fileType.description }}</p>
                </div>
              </div>
            </MkCardCheckbox>
          </template>

          <MkCardCheckbox v-model="formData.other" label="其他文件">
            <div class="flex min-w-0 items-center gap-3">
              <img class="shrink-0 w-6" src="@/assets/file-type/unknown-icon.svg" />
              <div class="min-w-0 flex-1">
                <h6>其他文件</h6>
                <MkTagsEdit v-model="formData.otherExtensions" :reserved-extensions="reservedExtensions" class="mt-2" />
              </div>
            </div>
          </MkCardCheckbox>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit">确定</el-button>
    </template>
  </MkDialog>
</template>
