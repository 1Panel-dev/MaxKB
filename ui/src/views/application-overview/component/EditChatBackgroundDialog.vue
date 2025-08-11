<template>
  <el-dialog
    :title="$t('views.application.editChatBackground')"
    v-model="dialogVisible"
    width="400"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div class="flex-center">
      <div class="edit-background">
        <div class="background-preview" :style="backgroundStyle">
          <div class="preview-text">{{ $t('views.application.backgroundPreview') }}</div>
        </div>
      </div>
    </div>
    <el-form
      ref="formRef"
      :model="form"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="$t('views.application.backgroundType')">
        <el-radio-group v-model="radioType">
          <el-radio value="default">{{ $t('views.application.defaultBackground') }}</el-radio>
          <el-radio value="custom">{{ $t('views.application.customBackground') }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item v-if="radioType === 'custom'">
        <el-upload
          ref="uploadRef"
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          accept="image/jpeg, image/png, image/gif"
          :on-change="onChange"
        >
          <el-button>
            <el-icon class="mr-4"><Upload /></el-icon>
            {{ $t('common.EditAvatarDialog.upload') }}
          </el-button>
        </el-upload>
        <el-text type="info" size="small" class="mt-8">
          {{ $t('views.application.backgroundUploadTip') }}
        </el-text>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { FormInstance, UploadFiles } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { MsgSuccess, MsgError } from '@/utils/message'
import { resetUrl } from '@/utils/common'
import { t } from '@/locales'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { useRoute } from 'vue-router'

const route = useRoute()

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const emit = defineEmits(['refresh'])

const dialogVisible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const uploadRef = ref()

const form = ref({})
const detail = ref<any>({})
const radioType = ref('default')
const backgroundFile = ref<any>(null)
const backgroundUrl = ref('')

const backgroundStyle = computed(() => {
  if (backgroundUrl.value) {
    return {
      backgroundImage: `url(${backgroundUrl.value})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  return {}
})

const open = (data: any) => {
  detail.value = data
  if (data.chat_background && data.chat_background !== '') {
    radioType.value = 'custom'
    backgroundUrl.value = resetUrl(data.chat_background)
  } else {
    radioType.value = 'default'
    backgroundUrl.value = ''
  }
  backgroundFile.value = null
  dialogVisible.value = true
}

const onChange = (file: any, fileList: UploadFiles) => {
  // 判断文件大小是否合法，文件限制不能大于 10 MB
  const isLimit = file?.size / 1024 / 1024 < 10
  if (!isLimit) {
    MsgError(t('common.EditAvatarDialog.fileSizeExceeded'))
    return false
  } else {
    backgroundFile.value = file
    backgroundUrl.value = URL.createObjectURL(file.raw)
  }
}

function submit() {
  if (radioType.value === 'default') {
    // 重置为默认背景
    loadSharedApi({ type: 'application', systemType: apiType.value })
      .putApplicationChatBackground(detail.value.id, null, loading)
      .then((res: any) => {
        emit('refresh', '')
        MsgSuccess(t('common.saveSuccess'))
        dialogVisible.value = false
      })
  } else if (radioType.value === 'custom' && backgroundFile.value) {
    // 上传自定义背景
    loadSharedApi({ type: 'application', systemType: apiType.value })
      .putApplicationChatBackground(detail.value.id, backgroundFile.value.raw, loading)
      .then((res: any) => {
        emit('refresh', res.data)
        MsgSuccess(t('common.saveSuccess'))
        dialogVisible.value = false
      })
  } else {
    MsgError(t('common.EditAvatarDialog.uploadImagePrompt'))
  }
}

defineExpose({ open })
</script>

<style lang="scss" scoped>
.edit-background {
  margin-bottom: 16px;
}

.background-preview {
  width: 200px;
  height: 120px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  position: relative;
  overflow: hidden;
}

.preview-text {
  color: #909399;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.8);
  padding: 4px 8px;
  border-radius: 4px;
}
</style>
