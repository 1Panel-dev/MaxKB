<template>
  <el-dialog title="添加关联数据集" v-model="dialogVisible" width="600">
    <el-row :gutter="12">
      <el-col :span="12">
        <el-card shadow="hover"> Hover </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover"> Hover </el-card>
      </el-col>
    </el-row>
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
