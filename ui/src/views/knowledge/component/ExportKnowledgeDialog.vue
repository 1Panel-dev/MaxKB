<template>
  <el-dialog
    v-model="dialogVisible"
    :title="$t('components.selectParagraph.title')"
    :before-close="close"
    width="450"
  >
    <el-checkbox v-model="with_source_file" label="同时导出源文件"/>
    <div>
      勾选后将原始文件一并打包至ZIP，导入时可自动恢复文件关联；不勾选则仅导出文本内容
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="close">{{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit"> {{ $t('common.submit') }} </el-button>
      </div>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'

const dialogVisible = ref<boolean>(false)
const with_source_file = ref<boolean>(false)
const submit_handle = ref<(with_source_file: boolean) => void>()

const submit = () => {
  if (submit_handle.value) {
    submit_handle.value(with_source_file.value)
  }
  close()
}

const open = (handle: (with_source_file: boolean) => void) => {
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
