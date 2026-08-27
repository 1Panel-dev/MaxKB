<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { Refresh } from '@element-plus/icons-vue'
import { computed, useAttrs, nextTick, inject, ref, reactive } from 'vue'
import type { FormField } from '@/components/mk-dynamics-form/type'
import { MsgError } from '@/utils/message'
import type { UploadFiles } from 'element-plus'
const upload = inject('upload') as DynamicFormValue
const delFile = inject('delFile') as DynamicFormValue
const attrs = useAttrs() as DynamicFormValue
withDefaults(defineProps<{ modelValue?: DynamicFormValue; formField: FormField }>(), {
  modelValue: () => [],
})
const onExceed = () => {
  MsgError('单次上传最多 ' + fileCountLimit.value + ' 个文件')
}
const emit = defineEmits(['update:modelValue'])

const filesize = (size: number) => {
  if (!size) return ''
  const num = 1024.0
  if (size < num) return size + 'B'
  if (size < Math.pow(num, 2)) return (size / num).toFixed(2) + 'K' //kb
  if (size < Math.pow(num, 3)) return (size / Math.pow(num, 2)).toFixed(2) + 'M' //M
  if (size < Math.pow(num, 4)) return (size / Math.pow(num, 3)).toFixed(2) + 'G' //G
  return (size / Math.pow(num, 4)).toFixed(2) + 'T' //T
}

const typeList: DynamicFormValue = {
  txt: ['txt', 'pdf', 'docx', 'md', 'html', 'zip', 'xlsx', 'xls', 'csv'],
  table: ['xlsx', 'xls', 'csv'],
  QA: ['xlsx', 'csv', 'xls', 'zip'],
}
const fileType = (name: string) => {
  const suffix = name.split('.')
  return suffix[suffix.length - 1] || 'DynamicFormValue'
}

const getImgUrl = (name: string) => {
  const list = Object.values(typeList).flat()
  const type = list.includes(fileType(name).toLowerCase())
    ? fileType(name).toLowerCase()
    : 'DynamicFormValue'
  return new URL(`../assets/fileType/${type}-icon.svg`, import.meta.url).href
}

const fileArray = ref<DynamicFormValue>([])

const loading = ref(false)
// 上传成功数量
const successCount = computed(
  () => fileArray.value.filter((i: DynamicFormValue) => i.status !== 'uploading').length,
)
// 上传失败数量
const errorCount = computed(
  () => fileArray.value.filter((i: DynamicFormValue) => i.status === 'error').length,
)
// 上传中数量
const uploadingCount = computed(
  () => fileArray.value.filter((i: DynamicFormValue) => i.status === 'uploading').length,
)
// 可重新上传的失败项（网络错误等）
const retryList = computed(() =>
  fileArray.value.filter((i: DynamicFormValue) => i.status === 'error' && i.canRetry),
)

const getFileStatusOrder = (item: DynamicFormValue) => {
  if (item.status === 'error' && item.canRetry) return 0
  if (item.status === 'error') return 1
  if (item.status === 'uploading') return 2
  return 3
}
const sortedFileArray = computed(() =>
  fileArray.value
    .map((item: DynamicFormValue, index: number) => ({ item, index }))
    .sort(
      (a: DynamicFormValue, b: DynamicFormValue) =>
        getFileStatusOrder(a.item) - getFileStatusOrder(b.item) || a.index - b.index,
    )
    .map(({ item }: DynamicFormValue) => item),
)
// 重新上传所有可重试的失败文件
const retryAll = () => {
  retryList.value.forEach((i: DynamicFormValue) => uploadFile(i))
}

// 上传on-change事件
const fileHandleChange = (file: DynamicFormValue, fileList: UploadFiles) => {
  // 按文件唯一标识精确定位并移除当前文件
  // 注意：不能使用 splice(-1, 1) 盲删末尾元素，文件夹上传时会误删正常文件而放走超限文件
  const removeCurrentFile = () => {
    const index = fileList.findIndex((item: DynamicFormValue) => item.uid === file.uid)
    if (index !== -1) {
      fileList.splice(index, 1)
    }
  }
  if (fileArray.value.length >= fileCountLimit.value) {
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
  const isLimit = file?.size / 1024 / 1024 < fileSizeLimit.value
  if (!isLimit) {
    item.status = 'error'
    item.errMsg = '大小超限'
    // MsgError('每个文件最大' + fileSizeLimit.value + 'MB')
    // fileList.splice(-1, 1) //移除当前超出大小的文件
    fileArray.value?.push(item)
    removeCurrentFile()
    return false
  }
  if (!allowedFileTypes.value.includes(fileType(file.name).toLocaleUpperCase())) {
    if (file?.name !== '.DS_Store') {
      MsgError('文件格式不支持')
    }
    removeCurrentFile()
    return false
  }

  if (file?.size === 0) {
    MsgError('文件不能为空')
    removeCurrentFile()
    return false
  }

  fileArray.value?.push(item)
  removeCurrentFile()
  uploadFile(item)
}
// 执行上传
const uploadFile = (item: DynamicFormValue) => {
  item.status = 'uploading'
  item.percentage = 0
  item.errMsg = ''
  item.canRetry = false
  item.aborted = false
  const res: DynamicFormValue = upload(
    item.raw,
    (percent: number) => {
      item.percentage = percent
    },
    loading,
  )
  // provider 返回 { request, abort } 时保存中断方法，删除时可中断上传
  item.abort = typeof res?.abort === 'function' ? res.abort : null
  const request: Promise<DynamicFormValue> = res?.then ? res : res?.request
  request
    .then((ok: DynamicFormValue) => {
      const pathSegments = ok.data.split('/')
      item.file_id = pathSegments[pathSegments.length - 1]
      item.percentage = 100
      item.status = 'success'
      emit('update:modelValue', fileArray.value)
    })
    .catch(() => {
      // 主动中断（删除）导致的失败不再标记错误
      if (item.aborted) return
      item.status = 'error'
      item.errMsg = '网络失败'
      item.canRetry = true
    })
}
function deleteFile(item: DynamicFormValue) {
  // 上传过程中删除则中断上传请求
  if (item?.status === 'uploading' && typeof item.abort === 'function') {
    item.aborted = true
    item.abort()
  } else if (item?.status === 'success' && item?.file_id) {
    if (delFile) {
      delFile(item.file_id)
    }
  }
  const index = fileArray.value.indexOf(item)
  if (index !== -1) {
    fileArray.value.splice(index, 1)
  }
  emit('update:modelValue', fileArray.value)
}

const handlePreview = (bool: boolean) => {
  let inputDom: DynamicFormValue = null
  nextTick(() => {
    if (document.querySelector('.el-upload__input') !== null) {
      inputDom = document.querySelector('.el-upload__input')
      inputDom.webkitdirectory = bool
    }
  })
}
const accept = computed(() => {
  return (attrs.file_type_list || [])
    .map((item: DynamicFormValue) => '.' + item.toLowerCase())
    .join(',')
})
const allowedFileTypes = computed(() => {
  return attrs.file_type_list.map((item: DynamicFormValue) => item.toUpperCase()) || []
})
const formats = computed(() => {
  return allowedFileTypes.value.join('、')
})
const fileSizeLimit = computed(() => {
  return attrs.file_size_limit || 50
})
const fileCountLimit = computed(() => {
  return attrs.file_count_limit || 100
})
</script>

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
      <img src="@/assets/empty/no-data.svg" alt="" />
      <div class="el-upload__text">
        <p>
          将文件拖到此处，或
          <em class="hover" @click.prevent="handlePreview(false)"> 点击上传 </em>
          <em class="hover ml-4" @click.prevent="handlePreview(true)"> 选择文件夹 </em>
        </p>
        <div class="upload__decoration">
          <p>单次上传最多 {{ fileCountLimit }} 个文件， 每个文件最大 {{ fileSizeLimit }} MB</p>
          <p>支持格式：{{ formats }}</p>
        </div>
      </div>
    </el-upload>
    <div v-if="fileArray?.length" class="flex-between w-full mt-16">
      <span> 已完成 {{ successCount }} / {{ fileArray.length }} 个文件 </span>
      <span v-if="uploadingCount" class="flex align-center">
        <el-icon class="is-loading color-primary" size="18"><Loading /></el-icon>
        <span class="ml-4">上传中</span>
      </span>
      <span v-else-if="errorCount" class="flex align-center">
        <el-icon class="color-danger ml-4" size="18"><WarningFilled /></el-icon>
        <span class="ml-4"> 失败 {{ errorCount }} 个文件 </span>
        <el-button v-if="retryList.length" text @click="retryAll">
          <MkIcon :icon="Refresh"></MkIcon>
          重试
        </el-button>
      </span>
      <span v-else-if="successCount === fileArray.length" class="flex align-center">
        <el-icon class="color-success"><WarningFilled /></el-icon>
        <span class="ml-4">全部成功</span>
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
                  <p :title="item && item?.name">{{ item && item?.name }}</p>
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
                  <MkIcon :icon="Refresh"></MkIcon>
                </el-button>
                <el-button text @click="deleteFile(item)">
                  <MkIcon name="icon_delete-trash_outlined"></MkIcon>
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
