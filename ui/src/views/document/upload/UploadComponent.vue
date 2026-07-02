<template>
  <h4 class="title-decoration-1 mb-8">{{ $t('views.document.uploadDocument') }}</h4>
  <el-form
    ref="FormRef"
    :model="form"
    :rules="rules"
    label-position="top"
    require-asterisk-position="right"
    v-loading="loading"
  >
    <div class="mt-16 mb-16">
      <el-radio-group v-model="form.fileType" @change="radioChange" class="app-radio-button-group">
        <el-radio-button value="txt">{{ $t('views.document.fileType.txt.label') }}</el-radio-button>
        <el-radio-button value="table">{{
          $t('views.document.fileType.table.label')
        }}</el-radio-button>
        <el-radio-button value="QA">{{ $t('views.document.fileType.QA.label') }}</el-radio-button>
      </el-radio-group>
    </div>

    <el-form-item prop="fileList" v-if="form.fileType === 'QA'">
      <div class="update-info flex p-8-12 border-r-6 mb-16 w-full">
        <div class="mt-4">
          <AppIcon iconName="app-warning-colorful" style="font-size: 16px"></AppIcon>
        </div>
        <div class="ml-16 lighter">
          <p>
            {{ $t('views.document.fileType.QA.tip1') }}
            <el-button type="primary" link @click="downloadTemplate('excel')">
              {{ $t('views.document.upload.download') }} Excel
              {{ $t('views.document.upload.template') }}
            </el-button>
            <el-button type="primary" link @click="downloadTemplate('csv')">
              {{ $t('views.document.upload.download') }} CSV
              {{ $t('views.document.upload.template') }}
            </el-button>
          </p>
          <p>{{ $t('views.document.fileType.QA.tip2') }}</p>
          <p>
            3. {{ $t('views.document.tip.fileLimitCountTip1') }} {{ file_count_limit }}
            {{ $t('views.document.tip.fileLimitCountTip2') }},
            {{ $t('views.document.tip.fileLimitSizeTip1') }} {{ file_size_limit }} MB
          </p>
        </div>
      </div>
      <el-upload
        :webkitdirectory="false"
        class="w-full mb-4"
        drag
        multiple
        :file-list="form.fileList"
        action="#"
        :auto-upload="false"
        :show-file-list="false"
        accept=".xlsx, .xls, .csv,.zip"
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
            <em class="hove ml-4" @click.prevent="handlePreview(true)">
              {{ $t('views.document.upload.selectFiles') }}
            </em>
          </p>
          <div class="upload__decoration">
            <p>{{ $t('views.document.upload.formats') }}XLS、XLSX、CSV、ZIP</p>
          </div>
        </div>
      </el-upload>
    </el-form-item>
    <el-form-item prop="fileList" v-else-if="form.fileType === 'table'">
      <div class="update-info flex p-8-12 border-r-6 mb-16 w-full">
        <div class="mt-4">
          <AppIcon iconName="app-warning-colorful" style="font-size: 16px"></AppIcon>
        </div>
        <div class="ml-16 lighter">
          <p>
            {{ $t('views.document.fileType.table.tip1') }}
            <el-button type="primary" link @click="downloadTableTemplate('excel')">
              {{ $t('views.document.upload.download') }} Excel
              {{ $t('views.document.upload.template') }}
            </el-button>
            <el-button type="primary" link @click="downloadTableTemplate('csv')">
              {{ $t('views.document.upload.download') }} CSV
              {{ $t('views.document.upload.template') }}
            </el-button>
          </p>
          <p>{{ $t('views.document.fileType.table.tip2') }}</p>
          <p>{{ $t('views.document.fileType.table.tip3') }}</p>
          <p>
            4. {{ $t('views.document.tip.fileLimitCountTip1') }} {{ file_count_limit }}
            {{ $t('views.document.tip.fileLimitCountTip2') }},
            {{ $t('views.document.tip.fileLimitSizeTip1') }} {{ file_size_limit }} MB
          </p>
        </div>
      </div>
      <el-upload
        :webkitdirectory="false"
        class="w-full mb-4"
        drag
        multiple
        :file-list="form.fileList"
        action="#"
        :auto-upload="false"
        :show-file-list="false"
        accept=".xlsx, .xls, .csv"
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
            <p>{{ $t('views.document.upload.formats') }}XLS、XLSX、CSV</p>
          </div>
        </div>
      </el-upload>
    </el-form-item>
    <el-form-item prop="fileList" v-else>
      <div class="update-info flex p-8-12 border-r-6 mb-16 w-full">
        <div class="mt-4">
          <AppIcon iconName="app-warning-colorful" style="font-size: 16px"></AppIcon>
        </div>
        <div class="ml-16 lighter">
          <p>{{ $t('views.document.fileType.txt.tip1') }}</p>
          <p>
            2. {{ $t('views.document.tip.fileLimitCountTip1') }} {{ file_count_limit }}
            {{ $t('views.document.tip.fileLimitCountTip2') }},
            {{ $t('views.document.tip.fileLimitSizeTip1') }} {{ file_size_limit }} MB
          </p>
        </div>
      </div>
      <el-upload
        :webkitdirectory="false"
        class="w-full"
        drag
        multiple
        :file-list="form.fileList"
        action="#"
        :auto-upload="false"
        :show-file-list="false"
        accept=".txt, .md, .log, .docx, .pdf, .html,.zip,.xlsx,.xls,.csv"
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
              {{
                $t('views.document.upload.formats')
              }}TXT、Markdown、PDF、DOCX、HTML、XLS、XLSX、CSV、ZIP
            </p>
          </div>
        </div>
      </el-upload>
    </el-form-item>
  </el-form>
  <div v-if="form.fileList?.length" class="flex-between w-full mt-16">
    <span>
      {{
        $t('dynamicsForm.UploadInput.uploadStatus', {
          success: successCount,
          total: form.fileList.length,
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
    <span v-else-if="successCount === form.fileList.length" class="flex align-center">
      <el-icon class="color-success"><WarningFilled /></el-icon>
      <span class="ml-4">{{ $t('dynamicsForm.UploadInput.allSuccess') }}</span>
    </span>
  </div>
  <el-row :gutter="8" v-if="form.fileList?.length" class="mt-8">
    <template v-for="(item, index) in sortedFileList" :key="index">
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
</template>
<script setup lang="ts">
import { ref, reactive, onUnmounted, onMounted, computed, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import type { UploadFiles } from 'element-plus'
import { filesize, getImgUrl, isRightType } from '@/utils/common'
import { MsgError } from '@/utils/message'
import applicationApi from '@/api/application/application'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import useStore from '@/stores'
import { t } from '@/locales'

const route = useRoute()
const {
  query: { id }, // id为knowledgeID，有id的是上传文档
} = route

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const { knowledge } = useStore()
const documentsFiles = computed(() => knowledge.documentsFiles)
const documentsType = computed(() => knowledge.documentsType)

const FormRef = ref()
const loading = ref(false)
const uploadLoading = ref(false)

const form = ref({
  fileType: 'txt',
  fileList: [] as any,
})

const rules = reactive({
  fileList: [
    { required: true, message: t('views.document.upload.requiredMessage'), trigger: 'change' },
  ],
})

const file_count_limit = ref(50)
const file_size_limit = ref(100)
const successCount = computed(
  () => form.value.fileList.filter((i: any) => i.status !== 'uploading').length,
)
const errorCount = computed(
  () => form.value.fileList.filter((i: any) => i.status === 'error').length,
)
const uploadingCount = computed(
  () => form.value.fileList.filter((i: any) => i.status === 'uploading').length,
)
const retryList = computed(() =>
  form.value.fileList.filter((i: any) => i.status === 'error' && i.canRetry),
)
const getFileStatusOrder = (item: any) => {
  if (item.status === 'error' && item.canRetry) return 0
  if (item.status === 'error') return 1
  if (item.status === 'uploading') return 2
  return 3
}
const sortedFileList = computed(() =>
  form.value.fileList
    .map((item: any, index: number) => ({ item, index }))
    .sort(
      (a: any, b: any) =>
        getFileStatusOrder(a.item) - getFileStatusOrder(b.item) || a.index - b.index,
    )
    .map(({ item }: any) => item),
)
const retryAll = () => {
  retryList.value.forEach((i: any) => uploadFile(i))
}

const filterSuccessFiles = (data: any): any => {
  return data?.filter((f: any) => f.status === 'success') || []
}
watch(form.value, (value) => {
  knowledge.saveDocumentsType(value.fileType)
  knowledge.saveDocumentsFile(filterSuccessFiles(value.fileList))
})

function downloadTemplate(type: string) {
  loadSharedApi({ type: 'document', systemType: apiType.value }).exportQATemplate(
    `${type}${t('views.document.upload.template')}.${type == 'csv' ? type : 'xlsx'}`,
    type,
  )
}

function downloadTableTemplate(type: string) {
  loadSharedApi({ type: 'document', systemType: apiType.value }).exportTableTemplate(
    `${type}${t('views.document.upload.template')}.${type == 'csv' ? type : 'xlsx'}`,
    type,
  )
}

function radioChange() {
  form.value.fileList.forEach((item: any) => {
    if (item?.status === 'uploading' && typeof item.abort === 'function') {
      item.aborted = true
      item.abort()
    }
  })
  form.value.fileList = []
}

function deleteFile(item: any) {
  if (item?.status === 'uploading' && typeof item.abort === 'function') {
    item.aborted = true
    item.abort()
  } else if (item?.status === 'success' && item?.file_id) {
    applicationApi.deleteFile(item.file_id)
  }
  const index = form.value.fileList.indexOf(item)
  if (index !== -1) {
    form.value.fileList.splice(index, 1)
  }
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
  if (form.value.fileList.length >= file_count_limit.value) {
    onExceed()
    removeCurrentFile()
    return false
  }
  const item = reactive({
    uid: file.uid,
    name: file.name,
    size: file.size,
    file_id: '',
    source_file_id: '',
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
    form.value.fileList?.push(item)
    removeCurrentFile()
    return false
  }
  if (!isRightType(file?.name, form.value.fileType)) {
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

  form.value.fileList.push(item)
  removeCurrentFile()
  uploadFile(item)
}

const uploadFile = (item: any) => {
  item.status = 'uploading'
  item.percentage = 0
  item.errMsg = ''
  item.canRetry = false
  item.aborted = false
  const res: any = applicationApi.postUploadFileProgress(
    item.raw,
    'TEMPORARY_120_MINUTE',
    'TEMPORARY_120_MINUTE',
    (percent: number) => {
      item.percentage = percent
    },
    uploadLoading,
  )
  item.abort = typeof res?.abort === 'function' ? res.abort : null
  const request: Promise<any> = res?.then ? res : res?.request
  request
    .then((ok: any) => {
      const split_path = ok.data.split('/')
      item.file_id = split_path[split_path.length - 1]
      item.source_file_id = item.file_id
      item.percentage = 100
      item.status = 'success'
    })
    .catch(() => {
      if (item.aborted) return
      item.status = 'error'
      item.errMsg = t('dynamicsForm.UploadInput.errorTip.networkError')
      item.canRetry = true
    })
}

const onExceed = () => {
  MsgError(
    t('views.document.tip.fileLimitCountTip1') +
      file_count_limit.value +
      t('views.document.tip.fileLimitCountTip2'),
  )
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

/*
  表单校验
*/
function validate() {
  if (!FormRef.value) return
  return FormRef.value.validate((valid: any) => {
    return valid
  })
}

function getDetail() {
  loadSharedApi({ type: 'knowledge', systemType: apiType.value })
    .getKnowledgeDetail(id, loading)
    .then((res: any) => {
      file_count_limit.value = res.data.file_count_limit
      file_size_limit.value = res.data.file_size_limit
    })
}

onMounted(() => {
  if (documentsType.value) {
    form.value.fileType = documentsType.value
  }
  if (documentsFiles.value) {
    form.value.fileList = documentsFiles.value
  }
  getDetail()
})
onUnmounted(() => {
  form.value = {
    fileType: 'txt',
    fileList: [],
  }
})

defineExpose({
  validate,
  form,
  uploadingCount,
})
</script>
<style scoped lang="scss"></style>
