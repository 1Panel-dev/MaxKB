<template>
  <el-dialog v-model="dialogVisible" title="选择向量化内容" width="500" :before-close="close">
    <el-radio-group v-model="state">
      <el-radio value="error" size="large">向量化未成功的分段</el-radio>
      <el-radio value="all" size="large">全部分段</el-radio>
    </el-radio-group>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="close">取消</el-button>
        <el-button type="primary" @click="submit"> 提交 </el-button>
      </div>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'
const dialogVisible = ref<boolean>(false)
const state = ref<'all' | 'error'>('error')
const stateMap = {
  all: ['0', '1', '2', '3', '4', '5', 'n'],
  error: ['0', '1', '3', '4', '5', 'n']
}
const submit_handle = ref<(stateList: Array<string>) => void>()
const submit = () => {
  if (submit_handle.value) {
    submit_handle.value(stateMap[state.value])
  }
  close()
}

const open = (handle: (stateList: Array<string>) => void) => {
  submit_handle.value = handle
  dialogVisible.value = true
}
const close = () => {
  submit_handle.value = undefined
  dialogVisible.value = false
}
defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
