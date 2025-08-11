<template>
  <el-dialog
    :title="$t('views.application.editIcon')"
    v-model="dialogVisible"
    width="400"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div class="flex-center">
      <div class="edit-avatar">
        <el-avatar shape="square" :size="80" style="background: none">
          <img v-if="iconUrl" :src="iconUrl" alt="" />
          <img v-else :src="resetUrl('./favicon.ico')" alt="" />
        </el-avatar>
      </div>
    </div>
    <el-form
      ref="formRef"
      :model="form"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="$t('views.application.iconType')">
        <el-radio-group v-model="radioType">
          <el-radio value="default">{{ $t('views.application.defaultIcon') }}</el-radio>
          <el-radio value="custom">{{ $t('views.application.customIcon') }}</el-radio>
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
          {{ $t('views.application.iconUploadTip') }}
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
const iconFile = ref<any>(null)
const iconUrl = ref('')

const open = (data: any) => {
  detail.value = data
  if (data.icon && data.icon !== './favicon.ico') {
    radioType.value = 'custom'
    iconUrl.value = resetUrl(data.icon)
  } else {
    radioType.value = 'default'
    iconUrl.value = ''
  }
  iconFile.value = null
  dialogVisible.value = true
}

const onChange = (file: any, fileList: UploadFiles) => {
  // 判断文件大小是否合法，文件限制不能大于 10 MB
  const isLimit = file?.size / 1024 / 1024 < 10
  if (!isLimit) {
    MsgError(t('common.EditAvatarDialog.fileSizeExceeded'))
    return false
  } else {
    iconFile.value = file
    iconUrl.value = URL.createObjectURL(file.raw)
  }
}

function submit() {
  if (radioType.value === 'default') {
    // 重置为默认图标
    loadSharedApi({ type: 'application', systemType: apiType.value })
      .putApplicationIcon(detail.value.id, null, loading)
      .then((res: any) => {
        emit('refresh', './favicon.ico')
        MsgSuccess(t('common.saveSuccess'))
        dialogVisible.value = false
      })
  } else if (radioType.value === 'custom' && iconFile.value) {
    // 上传自定义图标
    loadSharedApi({ type: 'application', systemType: apiType.value })
      .putApplicationIcon(detail.value.id, iconFile.value.raw, loading)
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
.edit-avatar {
  margin-bottom: 16px;
}
</style>
