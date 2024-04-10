<template>
  <h4 class="title-decoration-1 mb-8">上传文档</h4>
  <el-form
    ref="FormRef"
    :model="form"
    :rules="rules"
    label-position="top"
    require-asterisk-position="right"
  >
    <el-form-item prop="fileList">
      <el-upload
        class="w-full"
        drag
        multiple
        v-model:file-list="form.fileList"
        action="#"
        :auto-upload="false"
        :show-file-list="false"
        accept=".txt, .md, .csv, .log, .docx, .pdf"
        :limit="50"
        :on-exceed="onExceed"
        :on-change="filehandleChange"
      >
        <img src="@/assets/upload-icon.svg" alt="" />
        <div class="el-upload__text">
          <p>
            将文件拖拽至此区域或
            <em> 选择文件上传 </em>
          </p>
          <div class="upload__decoration">
            <p>
              支持格式：TXT、Markdown、PDF、DOCX，每次最多上传50个文件，每个文件不超过 100MB
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
                <el-text type="info">{{ filesize(item && item?.size) || '0K' }}</el-text>
              </div>
            </div>
            <el-button text @click="deleteFlie(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </el-card>
      </el-col>
    </template>
  </el-row>
</template>
<script setup lang="ts">
import { ref, reactive, onUnmounted, onMounted, computed, watch } from 'vue'
import type { UploadFile, UploadFiles } from 'element-plus'
import { filesize, getImgUrl, isRightType } from '@/utils/utils'
import { MsgError } from '@/utils/message'
import useStore from '@/stores'
const { dataset } = useStore()
const documentsFiles = computed(() => dataset.documentsFiles)
const form = ref({
  fileList: [] as any
})

const rules = reactive({
  fileList: [{ required: true, message: '请上传文件', trigger: 'change' }]
})
const FormRef = ref()

watch(form.value, (value) => {
  dataset.saveDocumentsFile(value.fileList)
})
function deleteFlie(index: number) {
  form.value.fileList.splice(index, 1)
}

// 上传on-change事件
const filehandleChange = (file: any, fileList: UploadFiles) => {
  //1、判断文件大小是否合法，文件限制不能大于10M
  const isLimit = file?.size / 1024 / 1024 < 100
  if (!isLimit) {
    MsgError('文件大小超过 100MB')
    fileList.splice(-1, 1) //移除当前超出大小的文件
    return false
  }
  if (!isRightType(file?.name)) {
    MsgError('文件格式不支持')
    fileList.splice(-1, 1)
    return false
  }
}

const onExceed = () => {
  MsgError('每次最多上传50个文件')
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
  if (documentsFiles.value) {
    form.value.fileList = documentsFiles.value
  }
})
onUnmounted(() => {
  form.value = {
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
</style>
