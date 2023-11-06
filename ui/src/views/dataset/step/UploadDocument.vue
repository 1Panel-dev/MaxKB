<template>
    <div class="upload-document">
        <!-- 基本信息 -->
  <BaseForm ref="BaseFormRef" />
  <!-- 上传文档 -->
  <UploadComponent ref="UploadComponentRef" />
    </div>

</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import BaseForm from '@/views/dataset/component/BaseForm.vue'
import UploadComponent from '@/views/dataset/component/UploadComponent.vue'
import useStore from '@/stores'
const { dataset } = useStore()

const BaseFormRef = ref()
const UploadComponentRef = ref()

// submit
const onSubmit = async () => {
  if ((await BaseFormRef.value.validate()) && (await UploadComponentRef.value.validate())) {
    // stores保存数据
    dataset.saveBaseInfo(BaseFormRef.value.form)
    dataset.saveDocumentsFile(UploadComponentRef.value.form.fileList)
    return true
  } else {
    return false
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
