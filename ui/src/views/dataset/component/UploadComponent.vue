<template>
  <h4 class="title-decoration-1 mb-8">上传文档</h4>
  <el-form
    ref="FormRef"
    :model="form"
    :rules="rules"
    label-position="top"
    require-asterisk-position="right"
  >
    <el-form-item>
      <el-radio-group v-model="form.fileType" @change="radioChange">
        <el-radio value="txt">文本文件</el-radio>
        <el-radio value="QA">QA 问答对</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item prop="fileList" v-if="form.fileType === 'QA'">
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
            拖拽文件至此上传或
            <em class="hover" @click.prevent="handlePreview(false)"> 选择文件 </em>
            <em class="hover" @click.prevent="handlePreview(true)"> 选择文件夹 </em>
          </p>
          <div class="upload__decoration">
            <p>当前支持 XLSX / XLS / CSV 格式的文档</p>
            <p>每次最多上传50个文件，每个文件不超过 100MB</p>
          </div>
        </div>
      </el-upload>
      <el-button type="primary" link @click="downloadTemplate('excel')">
        下载 Excel 模板
      </el-button>
      <el-divider direction="vertical" />
      <el-button type="primary" link @click="downloadTemplate('csv')"> 下载 CSV 模板 </el-button>
    </el-form-item>
    <el-form-item prop="fileList" v-else>
      <el-upload
        :webkitdirectory="false"
        class="w-full"
        drag
        multiple
        v-model:file-list="form.fileList"
        action="#"
        :auto-upload="false"
        :show-file-list="false"
        accept=".txt, .md, .csv, .log, .docx, .pdf, .html"
        :limit="50"
        :on-exceed="onExceed"
        :on-change="fileHandleChange"
        @click.prevent="handlePreview(false)"
      >
        <img src="@/assets/upload-icon.svg" alt="" />
        <div class="el-upload__text">
          <p>
            拖拽文件至此上传或
            <em class="hover" @click.prevent="handlePreview(false)"> 选择文件 </em>
            <em class="hover" @click.prevent="handlePreview(true)"> 选择文件夹 </em>
          </p>
          <div class="upload__decoration">
            <p>
              支持格式：TXT、Markdown、PDF、DOCX、HTML 每次最多上传50个文件，每个文件不超过 100MB
            </p>
            <p>若使用【高级分段】建议上传前规范文件的分段标识</p>
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
const { dataset } = useStore()
const documentsFiles = computed(() => dataset.documentsFiles)
const documentsType = computed(() => dataset.documentsType)
const form = ref({
  fileType: 'txt',
  fileList: [] as any
})

const rules = reactive({
  fileList: [{ required: true, message: '请上传文件', trigger: 'change' }]
})
const FormRef = ref()

watch(form.value, (value) => {
  dataset.saveDocumentsType(value.fileType)
  dataset.saveDocumentsFile(value.fileList)
})

function downloadTemplate(type: string) {
  documentApi.exportQATemplate(`${type}模版.${type == 'csv' ? type : 'xlsx'}`, type)
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
    MsgError('文件大小超过 100MB')
    fileList.splice(-1, 1) //移除当前超出大小的文件
    return false
  }
  if (!isRightType(file?.name, form.value.fileType)) {
    MsgError('文件格式不支持')
    fileList.splice(-1, 1)
    return false
  }
}

const onExceed = () => {
  MsgError('每次最多上传50个文件')
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
