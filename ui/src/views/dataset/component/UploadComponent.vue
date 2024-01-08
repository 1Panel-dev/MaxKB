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
        accept=".txt, .md"
      >
        <img src="@/assets/upload-icon.svg" alt="" />
        <div class="el-upload__text">
          <p>
            将文件拖拽至此区域或
            <em> 选择文件上传 </em>
          </p>
          <div class="upload__decoration">
            <p>支持格式：TXT、Markdown，每次最多上传50个文件，每个文件不超过 10MB</p>
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
              <img :src="getImgUrl(item && item?.name)" alt="" />
              <div class="ml-8">
                <p>{{ item && item?.name }}</p>
                <el-text type="info">{{ filesize(item && item?.size) }}</el-text>
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
import type { UploadProps } from 'element-plus'
import { filesize, getImgUrl } from '@/utils/utils'
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

// const beforeUploadHandle: UploadProps['beforeUpload'] = (rawFile) => {
//   const type = fileType(rawFile?.name)
//   console.log(type)
//   if (type !== 'txt' || type !== 'md') {
//     MsgError('Avatar picture must be JPG format!')
//     return false
//   } else if (rawFile.size / 1024 / 1024 > 10) {
//     MsgError('文件不超过 10MB!')
//     return false
//   }
//   return true
// }

watch(form.value, (value) => {
  dataset.saveDocumentsFile(value.fileList)
})
function deleteFlie(index: number) {
  form.value.fileList.splice(index, 1)
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
