<template>
  <div class="w-full">
    <el-upload
      ref="UploadRef"
      :webkitdirectory="false"
      class="w-full"
      drag
      multiple
      v-bind:file-list="fileArray"
      action="#"
      :auto-upload="false"
      :show-file-list="false"
      :accept="accept"
      :on-exceed="onExceed"
      :on-change="fileHandleChange"
      @click.prevent="handlePreview(false)"
    >
      <img src="@/assets/upload-icon.svg" alt="" />
      <div class="el-upload__text">
        <p>
          {{ $t('views.document.upload.uploadMessage') }}
          <em class="hover" @click.prevent="handlePreview(false)">
            {{ $t('views.document.upload.selectFile') }}
          </em>
          <em class="hover ml-4" @click.prevent="handlePreview(true)">
            {{ $t('views.document.upload.selectFiles') }}
          </em>
        </p>
        <div class="upload__decoration">
          <p>
            {{ $t('views.document.tip.fileLimitCountTip1') }} {{ file_count_limit }}
            {{ $t('views.document.tip.fileLimitCountTip2') }},
            {{ $t('views.document.tip.fileLimitSizeTip1') }} {{ file_size_limit }} MB
          </p>
          <p>{{ $t('views.document.upload.formats') }}{{ formats }}</p>
        </div>
      </div>
    </el-upload>
    <div v-if="fileArray?.length" class="flex-between w-full mt-16">
      <span>
        {{
          $t('dynamicsForm.UploadInput.uploadStatus', {
            success: successCount,
            total: fileArray.length,
          })
        }}
      </span>
      <span v-if="uploadingCount" class="flex align-center">
        <el-icon class="is-loading color-primary" size="18"><Loading /></el-icon>
        <span class="ml-4">{{ $t('dynamicsForm.UploadInput.uploading') }}</span>
      </span>
      <span v-else-if="errorCount" class="flex align-center">
        <el-icon class="color-danger ml-4" size="18"><WarningFilled /></el-icon>
        <span class="ml-4">
          {{ $t('dynamicsForm.UploadInput.failedStatus', { count: errorCount }) }}
        </span>
        <el-button v-if="retryList.length" text @click="retryAll">
          <AppIcon iconName="app-refresh"></AppIcon>
          {{ $t('dynamicsForm.UploadInput.reUpload') }}
        </el-button>
      </span>
      <span v-else-if="successCount === fileArray.length" class="flex align-center">
        <el-icon class="color-success"><WarningFilled /></el-icon>
        <span class="ml-4">{{ $t('dynamicsForm.UploadInput.allSuccess') }}</span>
      </span>
    </div>
    <el-row :gutter="8" v-if="fileArray?.length" class="mt-8">
      <template v-for="(item, index) in sortedFileArray" :key="index">
        <el-col :span="12" class="mb-8">
          <el-card
            shadow="never"
            style="
              --el-card-padding: 8px 12px;
              line-height: normal;
              position: relative;
              overflow: hidden;
            "
            :class="item.status === 'error' ? 'border-danger' : ''"
          >
            <div class="flex-between">
              <div class="flex">
                <img :src="getImgUrl(item && item?.name)" alt="" width="40" />
                <div class="ml-8">
                  <p class="ellipsis-1" :title="item && item?.name">{{ item && item?.name }}</p>
                  <el-text type="info" size="small">
                    <template v-if="item.status === 'uploading'">
                      {{ filesize((item.size * item.percentage) / 100) }} /
                      {{ filesize(item.size) || '0K' }}
                    </template>
                    <template v-else>{{ filesize(item && item?.size) || '0K' }}</template>
                  </el-text>
                  <el-text class="ml-8" v-if="item.status === 'error'" type="danger" size="small">
                    {{ item.errMsg }}
                  </el-text>
                </div>
              </div>
              <div class="flex align-center">
                <el-button v-if="item.canRetry" text @click="uploadFile(item)">
                  <AppIcon iconName="app-refresh"></AppIcon>
                </el-button>
                <el-button text @click="deleteFile(item)">
                  <AppIcon iconName="app-delete"></AppIcon>
                </el-button>
              </div>
            </div>
            <el-progress
              v-if="item.status === 'uploading'"
              class="card-progress"
              :percentage="item.percentage"
              :stroke-width="4"
              :show-text="false"
            />
          </el-card>
        </el-col>
      </template>
    </el-row>
  </div>
</template>
<script setup lang="ts">
import { computed, useAttrs, nextTick, inject, ref, reactive } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
import { MsgError } from '@/utils/message'
import type { UploadFiles } from 'element-plus'
import { filesize, getImgUrl, fileType } from '@/utils/common'
import applicationApi from '@/api/application/application'
import { t } from '@/locales'
const upload = inject('upload') as any
const attrs = useAttrs() as any
const props = withDefaults(defineProps<{ modelValue?: any; formField: FormField }>(), {
  modelValue: () => [],
})
const onExceed = () => {
  MsgError(
    t('views.document.tip.fileLimitCountTip1') +
      file_count_limit.value +
      t('views.document.tip.fileLimitCountTip2'),
  )
}
const emit = defineEmits(['update:modelValue'])

const fileArray = ref<any>([])
const loading = ref(false)
// 上传成功数量
const successCount = computed(
  () => fileArray.value.filter((i: any) => i.status !== 'uploading').length,
)
// 上传失败数量
const errorCount = computed(() => fileArray.value.filter((i: any) => i.status === 'error').length)
// 上传中数量
const uploadingCount = computed(
  () => fileArray.value.filter((i: any) => i.status === 'uploading').length,
)
// 可重新上传的失败项（网络错误等）
const retryList = computed(() =>
  fileArray.value.filter((i: any) => i.status === 'error' && i.canRetry),
)
const getFileStatusOrder = (item: any) => {
  if (item.status === 'error' && item.canRetry) return 0
  if (item.status === 'error') return 1
  if (item.status === 'uploading') return 2
  return 3
}
const sortedFileArray = computed(() =>
  fileArray.value
    .map((item: any, index: number) => ({ item, index }))
    .sort(
      (a: any, b: any) =>
        getFileStatusOrder(a.item) - getFileStatusOrder(b.item) || a.index - b.index,
    )
    .map(({ item }: any) => item),
)
// 重新上传所有可重试的失败文件
const retryAll = () => {
  retryList.value.forEach((i: any) => uploadFile(i))
}

// 上传on-change事件
const fileHandleChange = (file: any, fileList: UploadFiles) => {
  // 按文件唯一标识精确定位并移除当前文件
  // 注意：不能使用 splice(-1, 1) 盲删末尾元素，文件夹上传时会误删正常文件而放走超限文件
  const removeCurrentFile = () => {
    const index = fileList.findIndex((item: any) => item.uid === file.uid)
    if (index !== -1) {
      fileList.splice(index, 1)
    }
  }
  if (fileArray.value.length >= file_count_limit.value) {
    onExceed()
    removeCurrentFile()
    return false
  }
  const item = reactive({
    uid: file.uid,
    name: file.name,
    size: file.size,
    file_id: '',
    percentage: 0,
    status: 'uploading' as 'uploading' | 'success' | 'error',
    errMsg: '',
    canRetry: false,
    raw: file.raw,
    abort: null as null | (() => void),
    aborted: false,
  })

  //1、判断文件大小是否合法，文件限制不能大于100M
  const isLimit = file?.size / 1024 / 1024 < file_size_limit.value
  if (!isLimit) {
    item.status = 'error'
    item.errMsg = t('dynamicsForm.UploadInput.errorTip.sizeError')
    // MsgError(t('views.document.tip.fileLimitSizeTip1') + file_size_limit.value + 'MB')
    // fileList.splice(-1, 1) //移除当前超出大小的文件
    fileArray.value?.push(item)
    removeCurrentFile()
    return false
  }
  if (!file_type_list.value.includes(fileType(file.name).toLocaleUpperCase())) {
    if (file?.name !== '.DS_Store') {
      MsgError(t('views.document.upload.errorMessage2'))
    }
    removeCurrentFile()
    return false
  }

  if (file?.size === 0) {
    MsgError(t('views.document.upload.errorMessage3'))
    removeCurrentFile()
    return false
  }

  fileArray.value?.push(item)
  removeCurrentFile()
  uploadFile(item)
}
// 执行上传
const uploadFile = (item: any) => {
  item.status = 'uploading'
  item.percentage = 0
  item.errMsg = ''
  item.canRetry = false
  item.aborted = false
  const res: any = upload(
    item.raw,
    (percent: number) => {
      item.percentage = percent
    },
    loading,
  )
  // provider 返回 { request, abort } 时保存中断方法，删除时可中断上传
  item.abort = typeof res?.abort === 'function' ? res.abort : null
  const request: Promise<any> = res?.then ? res : res?.request
  request
    .then((ok: any) => {
      const split_path = ok.data.split('/')
      item.file_id = split_path[split_path.length - 1]
      item.percentage = 100
      item.status = 'success'
      emit('update:modelValue', fileArray.value)
    })
    .catch(() => {
      // 主动中断（删除）导致的失败不再标记错误
      if (item.aborted) return
      item.status = 'error'
      item.errMsg = t('dynamicsForm.UploadInput.errorTip.networkError')
      item.canRetry = true
    })
}
function deleteFile(item: any) {
  // 上传过程中删除则中断上传请求
  if (item?.status === 'uploading' && typeof item.abort === 'function') {
    item.aborted = true
    item.abort()
  } else if (item?.status === 'success' && item?.file_id) {
    applicationApi.deleteFile(item.file_id)
  }
  const index = fileArray.value.indexOf(item)
  if (index !== -1) {
    fileArray.value.splice(index, 1)
  }
  emit('update:modelValue', fileArray.value)
}

const handlePreview = (bool: boolean) => {
  let inputDom: any = null
  nextTick(() => {
    if (document.querySelector('.el-upload__input') != null) {
      inputDom = document.querySelector('.el-upload__input')
      inputDom.webkitdirectory = bool
    }
  })
}
const accept = computed(() => {
  return (attrs.file_type_list || []).map((item: any) => '.' + item.toLowerCase()).join(',')
})
const file_type_list = computed(() => {
  return attrs.file_type_list.map((item: any) => item.toUpperCase()) || []
})
const formats = computed(() => {
  return file_type_list.value.join('、')
})
const file_size_limit = computed(() => {
  return attrs.file_size_limit || 50
})
const file_count_limit = computed(() => {
  return attrs.file_count_limit || 100
})
</script>
<style lang="scss" scoped></style>
