<template>
  <el-dialog
    title="文件上传设置"
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
      <el-form-item label="单次上传最多文件数">
        <el-slider
          v-model="form_data.maxFiles"
          show-input
          :show-input-controls="false"
          :min="1"
          :max="10"
        />
      </el-form-item>
      <el-form-item label="每个文件最大（MB）">
        <el-slider
          v-model="form_data.fileLimit"
          show-input
          :show-input-controls="false"
          :min="1"
          :max="100"
        />
      </el-form-item>
      <el-form-item label="上传的文件类型">
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
                <p class="line-height-22 mt-4">文档（TXT、MD、DOCX、HTML、CSV、XLSX、XLS、PDF）</p>
                <el-text class="color-secondary">需要使用“文档内容提取”节点解析文档内容</el-text>
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
                <p class="line-height-22 mt-4">图片（JPG、JPEG、PNG、GIF）</p>
                <el-text class="color-secondary">需要使用“图片理解”节点解析图片内容</el-text>
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
                <p class="line-height-22 mt-4">音频（MP3、WAV、OGG、ACC）</p>
                <el-text class="color-secondary">需要使用“语音转文本”节点解析音频内容</el-text>
              </div>
            </div>
            <el-checkbox v-model="form_data.audio" @change="form_data.audio = !form_data.audio" />
          </div>
        </el-card>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="close"> 取消 </el-button>
        <el-button type="primary" @click="submit()" :loading="loading"> 确定 </el-button>
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
