<template>
  <h4 class="title-decoration-1 mb-8">{{ $t('views.document.uploadDocument') }}</h4>
  <el-form
    ref="FormRef"
    :model="form"
    :rules="rules"
    label-position="top"
    require-asterisk-position="right"
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
      <div class="update-info flex p-8-12 border-r-4 mb-16 w-full">
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
          <p>{{ $t('views.document.fileType.QA.tip3') }}</p>
        </div>
      </div>
      <el-upload
        :webkitdirectory="false"
        class="w-full mb-4"
        drag
        multiple
        v-model:file-list="form.fileList"
        action="#"
        :auto-upload="false"
        :show-file-list="false"
        accept=".xlsx, .xls, .csv,.zip"
        :limit="50"
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
      <div class="update-info flex p-8-12 border-r-4 mb-16 w-full">
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
          <p>{{ $t('views.document.fileType.table.tip4') }}</p>
        </div>
      </div>
      <el-upload
        :webkitdirectory="false"
        class="w-full mb-4"
        drag
        multiple
        v-model:file-list="form.fileList"
        action="#"
        :auto-upload="false"
        :show-file-list="false"
        accept=".xlsx, .xls, .csv"
        :limit="50"
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
      <div class="update-info flex p-8-12 border-r-4 mb-16 w-full">
        <div class="mt-4">
          <AppIcon iconName="app-warning-colorful" style="font-size: 16px"></AppIcon>
        </div>
        <div class="ml-16 lighter">
          <p>{{ $t('views.document.fileType.txt.tip1') }}</p>
          <p>{{ $t('views.document.fileType.txt.tip2') }}</p>
        </div>
      </div>
      <el-upload
        :webkitdirectory="false"
        class="w-full"
        drag
        multiple
        v-model:file-list="form.fileList"
        action="#"
        :auto-upload="false"
        :show-file-list="false"
        accept=".txt, .md, .log, .docx, .pdf, .html,.zip,.xlsx,.xls,.csv"
        :limit="50"
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
  <el-row :gutter="8" v-if="form.fileList?.length">
    <template v-for="(item, index) in form.fileList" :key="index">
      <el-col :span="12" class="mb-8">
        <el-card shadow="never" class="file-List-card">
          <div class="flex-between">
            <div class="flex">
              <img :src="getImgUrl(item && item?.name)" alt="" width="40" />
              <div class="ml-8">
                <p>{{ item && item?.name }}</p>
                <el-text type="info" size="small">{{
                  filesize(item && item?.size) || '0K'
                }}</el-text>
              </div>
            </div>
            <el-button text @click="deleteFile(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </el-card>
      </el-col>
    </template>
  </el-row>
</template>
<script setup lang="ts">
import { ref, reactive, onUnmounted, onMounted, computed, watch, nextTick } from 'vue'
import type { UploadFiles } from 'element-plus'
import { filesize, getImgUrl, isRightType } from '@/utils/utils'
import { MsgError } from '@/utils/message'
import documentApi from '@/api/document'
import useStore from '@/stores'
import { t } from '@/locales'
const { dataset } = useStore()
const documentsFiles = computed(() => dataset.documentsFiles)
const documentsType = computed(() => dataset.documentsType)
const form = ref({
  fileType: 'txt',
  fileList: [] as any
})

const rules = reactive({
  fileList: [
    { required: true, message: t('views.document.upload.requiredMessage'), trigger: 'change' }
  ]
})
const FormRef = ref()

watch(form.value, (value) => {
  dataset.saveDocumentsType(value.fileType)
  dataset.saveDocumentsFile(value.fileList)
})

function downloadTemplate(type: string) {
  documentApi.exportQATemplate(
    `${type}${t('views.document.upload.template')}.${type == 'csv' ? type : 'xlsx'}`,
    type
  )
}

function downloadTableTemplate(type: string) {
  documentApi.exportTableTemplate(
    `${type}${t('views.document.upload.template')}.${type == 'csv' ? type : 'xlsx'}`,
    type
  )
}

function radioChange() {
  form.value.fileList = []
}

function deleteFile(index: number) {
  form.value.fileList.splice(index, 1)
}

// 上传on-change事件
const fileHandleChange = (file: any, fileList: UploadFiles) => {
  //1、判断文件大小是否合法，文件限制不能大于100M
  const isLimit = file?.size / 1024 / 1024 < 100
  if (!isLimit) {
    MsgError(t('views.document.upload.errorMessage1'))
    fileList.splice(-1, 1) //移除当前超出大小的文件
    return false
  }

  if (!isRightType(file?.name, form.value.fileType)) {
    if (file?.name !== '.DS_Store') {
      MsgError(t('views.document.upload.errorMessage2'))
    }
    fileList.splice(-1, 1)
    return false
  }
  if (file?.size === 0) {
    MsgError(t('views.document.upload.errorMessage3'))
    fileList.splice(-1, 1)
    return false
  }
}

const onExceed = () => {
  MsgError(t('views.document.upload.errorMessage4'))
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

onMounted(() => {
  if (documentsType.value) {
    form.value.fileType = documentsType.value
  }
  if (documentsFiles.value) {
    form.value.fileList = documentsFiles.value
  }
})
onUnmounted(() => {
  form.value = {
    fileType: 'txt',
    fileList: []
  }
})

defineExpose({
  validate,
  form
})
</script>
<style scoped lang="scss">
.upload__decoration {
  font-size: 12px;
  line-height: 20px;
  color: var(--el-text-color-secondary);
}
.el-upload__text {
  .hover:hover {
    color: var(--el-color-primary-light-5);
  }
}

</style>
