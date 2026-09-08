<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules, InputInstance } from 'element-plus'
import documentIcon from '@/assets/file-type/file-document-icon.svg'
import imageIcon from '@/assets/file-type/file-image-icon.svg'
import audioIcon from '@/assets/file-type/file-audio-icon.svg'
import videoIcon from '@/assets/file-type/file-video-icon.svg'
import MkCardCheckbox from '@/components/mk-card-checkbox/index.vue'
import { MsgWarning } from '@/utils/message'
import { defaultFileUploadSetting } from '../constant'
import type { FileUploadSettingData } from '../types'

defineOptions({ name: 'BaseNodeFileUploadSetting' })

const setting = defineModel<FileUploadSettingData>({ required: true })

// 文件上传设置：打开时创建草稿，确认后回写配置。
const visible = ref(false)
const extensionInputVisible = ref(false)
const extensionInput = ref('')
const inputRef = useTemplateRef<InputInstance>('inputRef')
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

const reservedExtensions = new Set(fileTypes.flatMap(({ description }) => description.split('、')))

function showExtensionInput() {
  extensionInputVisible.value = true
  nextTick(() => inputRef.value?.focus())
}

function confirmExtension() {
  const extension = extensionInput.value.trim().replace(/^\./, '').toUpperCase()
  if (extension) {
    if (reservedExtensions.has(extension) || formData.value.otherExtensions.includes(extension)) {
      MsgWarning('该扩展名已存在')
    } else {
      formData.value.otherExtensions.push(extension)
    }
  }
  extensionInput.value = ''
  extensionInputVisible.value = false
}

function removeExtension(extension: string) {
  formData.value.otherExtensions = formData.value.otherExtensions.filter((item) => item !== extension)
}

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
  extensionInput.value = ''
  extensionInputVisible.value = false
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
                <div class="mt-2 flex flex-wrap gap-2" @click.stop>
                  <el-tag
                    v-for="extension in formData.otherExtensions"
                    :key="extension"
                    closable
                    effect="plain"
                    type="info"
                    @close="removeExtension(extension)"
                  >
                    {{ extension }}
                  </el-tag>
                  <el-input
                    v-if="extensionInputVisible"
                    ref="inputRef"
                    v-model="extensionInput"
                    class="w-24!"
                    size="small"
                    @blur="confirmExtension"
                    @keyup.enter="confirmExtension"
                  />
                  <el-button v-else size="small" @click="showExtensionInput">
                    <MkIcon name="icon_add_outlined" />
                    添加扩展名
                  </el-button>
                </div>
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
