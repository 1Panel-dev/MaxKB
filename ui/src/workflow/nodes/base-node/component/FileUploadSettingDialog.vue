<template>
  <el-dialog
    :title="$t('views.applicationWorkflow.nodes.baseNode.FileUploadSetting.title')"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    append-to-body
    width="800"
  >
    <el-form
      label-position="top"
      ref="fieldFormRef"
      :model="form_data"
      require-asterisk-position="right"
    >
      <el-form-item
        :label="$t('views.applicationWorkflow.nodes.baseNode.FileUploadSetting.maxFiles')"
      >
        <el-slider
          v-model="form_data.maxFiles"
          show-input
          :show-input-controls="false"
          :min="1"
          :max="10"
        />
      </el-form-item>
      <el-form-item
        :label="$t('views.applicationWorkflow.nodes.baseNode.FileUploadSetting.fileLimit')"
      >
        <el-slider
          v-model="form_data.fileLimit"
          show-input
          :show-input-controls="false"
          :min="1"
          :max="100"
        />
      </el-form-item>
      <el-form-item
        :label="
          $t('views.applicationWorkflow.nodes.baseNode.FileUploadSetting.fileUploadType.label')
        "
      >
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
                  {{ $t('common.fileUpload.document') }}
                  <el-text class="color-secondary"
                  >{{
                      $t(
                        'views.applicationWorkflow.nodes.baseNode.FileUploadSetting.fileUploadType.documentText'
                      )
                    }}
                  </el-text>
                </p>
                <p>{{ documentExtensions.join('、') }}</p>
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
                  {{ $t('common.fileUpload.image') }}
                  <el-text class="color-secondary"
                  >{{
                      $t(
                        'views.applicationWorkflow.nodes.baseNode.FileUploadSetting.fileUploadType.imageText'
                      )
                    }}
                  </el-text>
                </p>
                <p>{{ imageExtensions.join('、') }}</p>
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
                <p class="line-height-22 mt-4">
                  {{ $t('common.fileUpload.audio') }}
                  <el-text class="color-secondary"
                  >{{
                      $t(
                        'views.applicationWorkflow.nodes.baseNode.FileUploadSetting.fileUploadType.audioText'
                      )
                    }}
                  </el-text>
                </p>
                <p>{{ audioExtensions.join('、') }}</p>
              </div>
            </div>
            <el-checkbox v-model="form_data.audio" @change="form_data.audio = !form_data.audio" />
          </div>
        </el-card>
        <el-card
          shadow="hover"
          class="card-checkbox cursor w-full mb-8"
          :class="form_data.other ? 'active' : ''"
          style="--el-card-padding: 8px 16px"
          @click.stop="form_data.other = !form_data.other"
        >
          <div class="flex-between">
            <div class="flex align-center">
              <img class="mr-12" :width="32" src="@/assets/fileType/unknown-icon.svg" alt="" />
              <div>
                <p class="line-height-22 mt-4">
                  {{ $t('common.fileUpload.other') }}
                  <el-text class="color-secondary"
                  >{{
                      $t(
                        'views.applicationWorkflow.nodes.baseNode.FileUploadSetting.fileUploadType.otherText'
                      )
                    }}
                  </el-text>
                </p>
                <el-space wrap :size="2" class="mt-4">
                  <el-tag
                    v-for="tag in form_data.otherExtensions"
                    :key="tag"
                    closable
                    :disable-transitions="false"
                    @close="handleClose(tag)"
                    type="info"
                    class="mr-4"
                    effect="plain"
                    style="
                      --el-tag-border-radius: 4px;
                      --el-tag-border-color: var(--el-border-color);
                    "
                  >
                    {{ tag }}
                  </el-tag>
                  <el-input
                    v-if="inputVisible"
                    ref="InputRef"
                    v-model="inputValue"
                    size="small"
                    @keyup.enter="handleInputConfirm"
                    @blur="handleInputConfirm"
                  />
                  <el-button v-else class="button-new-tag" size="small" @click.stop="showInput">
                    + {{ $t('common.fileUpload.addExtensions') }}
                  </el-button>
                </el-space>
              </div>
            </div>
            <el-checkbox v-model="form_data.other" @change="form_data.other = !form_data.other" />
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
import type { InputInstance } from 'element-plus'
import { cloneDeep } from 'lodash'
import { MsgWarning } from '@/utils/message'
import { t } from '@/locales'

const emit = defineEmits(['refresh'])
const props = defineProps<{ nodeModel: any }>()

const dialogVisible = ref(false)
const inputVisible = ref(false)
const inputValue = ref('')
const loading = ref(false)
const fieldFormRef = ref()
const InputRef = ref<InputInstance>()

const documentExtensions = ['TXT', 'MD', 'DOCX', 'HTML', 'CSV', 'XLSX', 'XLS', 'PDF']
const imageExtensions = ['JPG', 'JPEG', 'PNG', 'GIF']
const audioExtensions = ['MP3', 'WAV', 'OGG', 'ACC', 'M4A']

const form_data = ref({
  maxFiles: 3,
  fileLimit: 50,
  document: true,
  image: false,
  audio: false,
  video: false,
  other: false,
  otherExtensions: ['PPT', 'DOC']
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

const handleClose = (tag: string) => {
  form_data.value.otherExtensions = form_data.value.otherExtensions.filter((item) => item !== tag)
}

const showInput = () => {
  inputVisible.value = true
  nextTick(() => {
    InputRef.value!.input!.focus()
  })
}
const handleInputConfirm = () => {
  if (inputValue.value) {
    inputValue.value = inputValue.value.toUpperCase()
    if (
      form_data.value.otherExtensions.includes(inputValue.value) ||
      documentExtensions.includes(inputValue.value) ||
      imageExtensions.includes(inputValue.value) ||
      audioExtensions.includes(inputValue.value)
    ) {
      inputVisible.value = false
      inputValue.value = ''
      MsgWarning(t('common.fileUpload.existingExtensionsTip'))
      return
    }
    form_data.value.otherExtensions.push(inputValue.value)
  }
  inputVisible.value = false
  inputValue.value = ''
}

async function submit() {
  const formEl = fieldFormRef.value
  if (!formEl) return
  await formEl.validate().then(() => {
    const formattedData = cloneDeep(form_data.value)
    emit('refresh', formattedData)
    // emit('refresh', form_data.value)
    props.nodeModel.graphModel.eventCenter.emit('refreshFileUploadConfig')
    dialogVisible.value = false
  })
}

defineExpose({
  open
})
</script>

<style scoped lang="scss"></style>
