<template>
  <el-dialog
    :title="$t('views.applicationWorkflow.nodes.baseNode.FileUploadSetting.title')"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    append-to-body
    width="600"
  >
    <el-form
      label-position="top"
      ref="fieldFormRef"
      :model="form_data"
      require-asterisk-position="right"
    >
      <el-form-item :label="$t('views.applicationWorkflow.nodes.baseNode.FileUploadSetting.maxFiles')">
        <el-slider
          v-model="form_data.maxFiles"
          show-input
          :show-input-controls="false"
          :min="1"
          :max="10"
        />
      </el-form-item>
      <el-form-item :label="$t('views.applicationWorkflow.nodes.baseNode.FileUploadSetting.fileLimit')">
        <el-slider
          v-model="form_data.fileLimit"
          show-input
          :show-input-controls="false"
          :min="1"
          :max="100"
        />
      </el-form-item>
      <el-form-item :label="$t('views.applicationWorkflow.nodes.baseNode.FileUploadSetting.fileUploadType.label')">
        <el-card
          shadow="hover"
          class="card-checkbox cursor w-full mb-8"
          :class="form_data.document ? 'active' : ''"
          style="--el-card-padding: 8px 16px"
          @click.stop="form_data.document = !form_data.document"
        >
          <div class="flex-between">
            <div class="flex align-center">
              <img class="mr-12" src="@/assets/icon_file-doc.svg" alt="" />
              <div>
                <p class="line-height-22 mt-4">
                  {{ $t('common.fileUpload.document') }}（TXT、MD、DOCX、HTML、CSV、XLSX、XLS、PDF）
                </p>
                <el-text class="color-secondary">{{$t('views.applicationWorkflow.nodes.baseNode.FileUploadSetting.fileUploadType.documentText')}}</el-text>
              </div>
            </div>
            <el-checkbox
              v-model="form_data.document"
              @change="form_data.document = !form_data.document"
            />
          </div>
        </el-card>
        <el-card
          shadow="hover"
          class="card-checkbox cursor w-full mb-8"
          :class="form_data.image ? 'active' : ''"
          style="--el-card-padding: 8px 16px"
          @click.stop="form_data.image = !form_data.image"
        >
          <div class="flex-between">
            <div class="flex align-center">
              <img class="mr-12" src="@/assets/icon_file-image.svg" alt="" />
              <div>
                <p class="line-height-22 mt-4">
                  {{ $t('common.fileUpload.image') }}（JPG、JPEG、PNG、GIF）
                </p>
                <el-text class="color-secondary">{{$t('views.applicationWorkflow.nodes.baseNode.FileUploadSetting.fileUploadType.imageText')}}</el-text>
              </div>
            </div>
            <el-checkbox v-model="form_data.image" @change="form_data.image = !form_data.image" />
          </div>
        </el-card>

        <el-card
          shadow="hover"
          class="card-checkbox cursor w-full mb-8"
          :class="form_data.audio ? 'active' : ''"
          style="--el-card-padding: 8px 16px"
          @click.stop="form_data.audio = !form_data.audio"
        >
          <div class="flex-between">
            <div class="flex align-center">
              <img class="mr-12" src="@/assets/icon_file-audio.svg" alt="" />
              <div>
                <p class="line-height-22 mt-4">{{ $t('common.fileUpload.audio') }}（MP3、WAV、OGG、ACC）</p>
                <el-text class="color-secondary">{{$t('views.applicationWorkflow.nodes.baseNode.FileUploadSetting.fileUploadType.audioText')}}</el-text>
              </div>
            </div>
            <el-checkbox v-model="form_data.audio" @change="form_data.audio = !form_data.audio" />
          </div>
        </el-card>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="close"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit()" :loading="loading">
          {{ $t('common.confirm') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { nextTick, ref } from 'vue'

const emit = defineEmits(['refresh'])
const props = defineProps<{ nodeModel: any }>()

const dialogVisible = ref(false)
const loading = ref(false)
const fieldFormRef = ref()
const form_data = ref({
  maxFiles: 3,
  fileLimit: 50,
  document: true,
  image: false,
  audio: false,
  video: false
})

function open(data: any) {
  dialogVisible.value = true
  nextTick(() => {
    form_data.value = { ...form_data.value, ...data }
  })
}

function close() {
  dialogVisible.value = false
}

async function submit() {
  const formEl = fieldFormRef.value
  if (!formEl) return
  await formEl.validate().then(() => {
    emit('refresh', form_data.value)
    props.nodeModel.graphModel.eventCenter.emit('refreshFileUploadConfig')
    dialogVisible.value = false
  })
}

defineExpose({
  open
})
</script>

<style scoped lang="scss"></style>
