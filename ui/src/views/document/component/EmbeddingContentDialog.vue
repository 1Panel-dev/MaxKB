<template>
  <el-dialog
    v-model="dialogVisible"
    :title="$t('components.selectParagraph.title')"
    :before-close="close"
    width="450"
  >
    <el-radio-group v-model="state" class="radio-block">
      <el-radio value="error" size="large">{{
        $t('components.selectParagraph.error')
      }}</el-radio>
      <el-radio value="all" size="large">{{ $t('components.selectParagraph.all') }}</el-radio>
    </el-radio-group>
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
