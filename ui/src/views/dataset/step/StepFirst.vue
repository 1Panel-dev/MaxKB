<template>
  <el-scrollbar>
    <div class="upload-document p-24">
      <!-- 基本信息 -->
      <BaseForm ref="BaseFormRef" v-if="isCreate" />
      <!-- 上传文档 -->
      <UploadComponent ref="UploadComponentRef" />
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BaseForm from '@/views/dataset/component/BaseForm.vue'
import UploadComponent from '@/views/dataset/component/UploadComponent.vue'

import useStore from '@/stores'
const { dataset } = useStore()

const route = useRoute()
const {
  params: { type }
} = route
const isCreate = type === 'create'
const BaseFormRef = ref()
const UploadComponentRef = ref()

// submit
const onSubmit = async () => {
  if (isCreate) {
    if ((await BaseFormRef.value?.validate()) && (await UploadComponentRef.value.validate())) {
      // stores保存数据
      dataset.saveBaseInfo(BaseFormRef.value.form)
      dataset.saveDocumentsFile(UploadComponentRef.value.form.fileList)
      return true
    } else {
      return false
    }
  } else {
    if (await UploadComponentRef.value.validate()) {
      // stores保存数据
      dataset.saveDocumentsFile(UploadComponentRef.value.form.fileList)
      return true
    } else {
      return false
    }
  }
}

onMounted(() => {})

defineExpose({
  onSubmit
})
</script>
<style scoped lang="scss">
.upload-document {
  width: 70%;
  margin: 0 auto;
}
</style>
