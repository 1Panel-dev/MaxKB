<template>
  <el-dialog
    :title="`Logo ${$t('common.setting')}`"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    width="550"
  >
    <el-radio-group v-model="radioType" class="radio-block mb-16">
      <el-radio value="default">
        <p>{{ $t('common.EditAvatarDialog.default') }}</p>
        <el-avatar class="avatar-green" shape="square" :size="32">
          <img src="@/assets/workflow/icon_tool.svg" style="width: 58%" alt="" />
        </el-avatar>
      </el-radio>

      <el-radio value="custom">
        <p>{{ $t('common.EditAvatarDialog.customizeUpload') }}</p>
        <div class="flex mt-8">
          <el-avatar
            v-if="fileURL"
            shape="square"
            :size="32"
            style="background: none"
            class="mr-16"
          >
            <img :src="fileURL" alt="" />
          </el-avatar>
          <el-upload
            ref="uploadRef"
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            accept="image/jpeg, image/png, image/gif"
            :on-change="onChange"
          >
            <el-button icon="Upload" :disabled="radioType !== 'custom'"
              >{{ $t('common.EditAvatarDialog.upload') }}
            </el-button>
          </el-upload>
        </div>
        <div class="el-upload__tip info mt-8">
          {{ $t('common.EditAvatarDialog.sizeTip') }}
        </div>
      </el-radio>
    </el-radio-group>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit" :loading="loading">
          {{ $t('common.save') }}</el-button
        >
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import {computed, ref, watch} from 'vue'
import ToolApi from '@/api/tool/tool'
import { cloneDeep } from 'lodash'
import { MsgError, MsgSuccess } from '@/utils/message'
import { defaultIcon, isAppIcon } from '@/utils/common'
import { t } from '@/locales'
import {loadSharedApi} from "@/utils/dynamics-api/shared-api.ts";
import {useRoute} from "vue-router";

const emit = defineEmits(['refresh'])
const route = useRoute()

const iconFile = ref<any>(null)
const fileURL = ref<any>(null)

const dialogVisible = ref<boolean>(false)
const loading = ref(false)
const detail = ref<any>(null)
const radioType = ref('default')

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const isShared = computed(() => {
  return route.path.includes('shared')
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    iconFile.value = null
    fileURL.value = null
  }
})

const open = (data: any) => {
  radioType.value = isAppIcon(data.icon) ? 'custom' : 'default'
  fileURL.value = isAppIcon(data.icon) ? data.icon : null
  detail.value = cloneDeep(data)
  dialogVisible.value = true
}

const onChange = (file: any) => {
  //1、判断文件大小是否合法，文件限制不能大于10MB
  const isLimit = file?.size / 1024 / 1024 < 10
  if (!isLimit) {
    // @ts-ignore
    MsgError(t('common.EditAvatarDialog.fileSizeExceeded'))
    return false
  } else {
    iconFile.value = file
    fileURL.value = URL.createObjectURL(file.raw)
  }
}

function submit() {
  if (radioType.value === 'default') {
    emit('refresh', '')
    dialogVisible.value = false
  } else if (radioType.value === 'custom' && iconFile.value) {
    const fd = new FormData()
    fd.append('file', iconFile.value.raw)
    loadSharedApi({ type: 'tool', systemType: apiType.value })
      .putToolIcon(detail.value.id, fd, loading).then((res: any) => {
        emit('refresh', res.data)
        dialogVisible.value = false
      })
  } else {
    MsgError(t('common.EditAvatarDialog.uploadImagePrompt'))
  }
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
