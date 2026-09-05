<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { InputInstance } from 'element-plus'
import { MsgWarning } from '@/utils/message'
import { defaultFileUploadSetting } from '../constant'
import type { FileUploadSetting } from '../types'

defineOptions({ name: 'BaseNodeFileUploadSettingDialog' })

const emit = defineEmits<{ submit: [setting: FileUploadSetting] }>()

const visible = ref(false)
const extensionInputVisible = ref(false)
const extensionInput = ref('')
const inputRef = useTemplateRef<InputInstance>('inputRef')
const formData = ref<FileUploadSetting>(cloneDeep(defaultFileUploadSetting))

const fileTypes = [
  { field: 'document', label: '文档', description: 'TXT、MD、DOCX、HTML、CSV、XLSX、XLS、PDF' },
  { field: 'image', label: '图片', description: 'JPG、JPEG、PNG、GIF' },
  { field: 'audio', label: '音频', description: 'MP3、WAV、OGG、AAC、M4A' },
  { field: 'video', label: '视频', description: 'MP4、AVI、MKV、MOV、FLV、WMV' },
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
  if (!formData.value.local_upload && !formData.value.url_upload) {
    MsgWarning('请至少选择一种上传方式')
    return
  }
  emit('submit', cloneDeep(formData.value))
  visible.value = false
}

function open(setting: FileUploadSetting) {
  formData.value = cloneDeep(setting)
  visible.value = true
}

function resetData() {
  formData.value = cloneDeep(defaultFileUploadSetting)
  extensionInput.value = ''
  extensionInputVisible.value = false
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="文件上传设置" width="800" @closed="resetData">
    <el-form :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="单次最多上传文件数">
        <el-slider v-model="formData.maxFiles" :max="100" :min="1" show-input />
      </el-form-item>

      <el-form-item label="单个文件大小限制（MB）">
        <el-slider v-model="formData.fileLimit" :max="1000" :min="1" show-input />
      </el-form-item>

      <el-form-item label="允许上传的文件类型">
        <div class="grid w-full grid-cols-2 gap-2">
          <el-card
            v-for="fileType in fileTypes"
            :key="fileType.field"
            class="cursor-pointer"
            :class="{ 'border-primary': formData[fileType.field] }"
            shadow="never"
            @click="formData[fileType.field] = !formData[fileType.field]"
          >
            <div class="flex-between gap-3">
              <div class="min-w-0">
                <h6>{{ fileType.label }}</h6>
                <p class="mt-1 break-all text-sm text-N600">{{ fileType.description }}</p>
              </div>
              <el-checkbox v-model="formData[fileType.field]" @click.stop />
            </div>
          </el-card>

          <el-card
            class="col-span-2 cursor-pointer"
            :class="{ 'border-primary': formData.other }"
            shadow="never"
            @click="formData.other = !formData.other"
          >
            <div class="flex-between gap-3">
              <div class="min-w-0 flex-1">
                <h6>其他文件</h6>
                <div class="mt-2 flex flex-wrap gap-2" @click.stop>
                  <el-tag v-for="extension in formData.otherExtensions" :key="extension" closable type="info" @close="removeExtension(extension)">
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
              <el-checkbox v-model="formData.other" @click.stop />
            </div>
          </el-card>
        </div>
      </el-form-item>

      <el-form-item label="上传方式" required>
        <el-checkbox v-model="formData.local_upload">本地上传</el-checkbox>
        <el-checkbox v-model="formData.url_upload">URL 上传</el-checkbox>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit">确定</el-button>
    </template>
  </MkDialog>
</template>
