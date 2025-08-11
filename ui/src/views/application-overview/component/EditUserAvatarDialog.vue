<template>
  <el-dialog
    :title="$t('views.application.editUserAvatar')"
    v-model="dialogVisible"
    width="400"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div class="flex-center">
      <div class="edit-avatar">
        <el-avatar shape="square" :size="80" style="background: none">
          <img v-if="avatarUrl" :src="avatarUrl" alt="" />
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
      <el-form-item :label="$t('views.application.avatarType')">
        <el-radio-group v-model="radioType">
          <el-radio value="default">{{ $t('views.application.defaultAvatar') }}</el-radio>
          <el-radio value="custom">{{ $t('views.application.customAvatar') }}</el-radio>
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
          {{ $t('views.application.avatarUploadTip') }}
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
const avatarFile = ref<any>(null)
const avatarUrl = ref('')

const open = (data: any) => {
  detail.value = data
  if (data.user_avatar && data.user_avatar !== '') {
    radioType.value = 'custom'
    avatarUrl.value = resetUrl(data.user_avatar)
  } else {
    radioType.value = 'default'
    avatarUrl.value = ''
  }
  avatarFile.value = null
  dialogVisible.value = true
}

const onChange = (file: any, fileList: UploadFiles) => {
  // 判断文件大小是否合法，文件限制不能大于 10 MB
  const isLimit = file?.size / 1024 / 1024 < 10
  if (!isLimit) {
    MsgError(t('common.EditAvatarDialog.fileSizeExceeded'))
    return false
  } else {
    avatarFile.value = file
    avatarUrl.value = URL.createObjectURL(file.raw)
  }
}

function submit() {
  if (radioType.value === 'default') {
    // 重置为默认头像
    loadSharedApi({ type: 'application', systemType: apiType.value })
      .putApplicationUserAvatar(detail.value.id, null, loading)
      .then((res: any) => {
        emit('refresh', '')
        MsgSuccess(t('common.saveSuccess'))
        dialogVisible.value = false
      })
  } else if (radioType.value === 'custom' && avatarFile.value) {
    // 上传自定义头像
    loadSharedApi({ type: 'application', systemType: apiType.value })
      .putApplicationUserAvatar(detail.value.id, avatarFile.value.raw, loading)
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
