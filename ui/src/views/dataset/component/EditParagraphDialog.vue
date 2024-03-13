<template>
  <el-dialog title="编辑分段" v-model="dialogVisible" width="80%" destroy-on-close>
    <ParagraphForm ref="paragraphFormRef" :data="detail" :isEdit="true" />
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submitHandle"> 保存 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { cloneDeep } from 'lodash'
import ParagraphForm from '@/views/paragraph/component/ParagraphForm.vue'

const emit = defineEmits(['updateContent'])

const dialogVisible = ref<boolean>(false)

const detail = ref({})

const paragraphFormRef = ref()

watch(dialogVisible, (bool) => {
  if (!bool) {
    detail.value = {}
  }
})

const open = (data: any) => {
  detail.value = cloneDeep(data)
  dialogVisible.value = true
}
const submitHandle = async () => {
  if (await paragraphFormRef.value?.validate()) {
    emit('updateContent', paragraphFormRef.value?.form)
    dialogVisible.value = false
  }
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
