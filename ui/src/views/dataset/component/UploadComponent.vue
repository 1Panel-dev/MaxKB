<template>
  <h4 class="title-decoration-1 mb-8">上传文档</h4>
  <el-form
    ref="FormRef"
    :model="form"
    :rules="rules"
    label-position="top"
    require-asterisk-position="right"
  >
    <div class="mt-16 mb-16">
      <el-radio-group v-model="form.fileType" @change="radioChange" class="app-radio-button-group">
        <el-radio-button value="txt">文本文件</el-radio-button>
        <el-radio-button value="table">表格</el-radio-button>
        <el-radio-button value="QA">QA 问答对</el-radio-button>
      </el-radio-group>
    </div>

    <el-form-item prop="fileList" v-if="form.fileType === 'QA'">
      <div class="update-info flex p-8-12 border-r-4 mb-16 w-full">
        <div class="mt-4">
          <AppIcon iconName="app-warning-colorful" style="font-size: 16px"></AppIcon>
        </div>
        <div class="ml-16 lighter">
          <p>
            1、点击下载对应模版并完善信息：
            <el-button type="primary" link @click="downloadTemplate('excel')">
              下载 Excel 模版
            </el-button>
            <el-button type="primary" link @click="downloadTemplate('csv')">
              下载 CSV 模版
            </el-button>
          </p>
          <p>2、上传的表格文件中每个 sheet 会作为一个文档，sheet名称为文档名称</p>
          <p>3、每次最多上传 50 个文件，每个文件不超过 100MB</p>
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
            拖拽文件至此上传或
            <em class="hover" @click.prevent="handlePreview(false)"> 选择文件 </em>
            <em class="hover" @click.prevent="handlePreview(true)"> 选择文件夹 </em>
          </p>
          <div class="upload__decoration">
            <p>支持格式：EXCEL、CSV</p>
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
            1、点击下载对应模版并完善信息：
            <el-button type="primary" link @click="downloadTableTemplate('excel')">
              下载 Excel 模版
            </el-button>
            <el-button type="primary" link @click="downloadTableTemplate('csv')">
              下载 CSV 模版
            </el-button>
          </p>
          <p>2、第一行必须是列标题，且列标题必须是有意义的术语，表中每条记录将作为一个分段</p>
          <p>3、上传的表格文件中每个 sheet 会作为一个文档，sheet名称为文档名称</p>
          <p>4、每次最多上传 50 个文件，每个文件不超过 100MB</p>
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
            拖拽文件至此上传或
            <em class="hover" @click.prevent="handlePreview(false)"> 选择文件 </em>
            <em class="hover" @click.prevent="handlePreview(true)"> 选择文件夹 </em>
          </p>
          <div class="upload__decoration">
            <p>支持格式：EXCEL 和 CSV</p>
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
          <p>1、文件上传前，建议规范文件的分段标识</p>
          <p>2、每次最多上传 50 个文件，每个文件不超过 100MB</p>
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
            <p>支持格式：TXT、Markdown、PDF、DOCX、HTML</p>
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

function downloadTableTemplate(type: string) {
  documentApi.exportTableTemplate(`${type}模版.${type == 'csv' ? type : 'xlsx'}`, type)
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
  if (file?.size === 0) {
    MsgError('文件不能为空')
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
.update-info {
  background: #d6e2ff;
  line-height: 25px;
}
</style>
