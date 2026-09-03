<script setup lang="ts">
import { ref } from 'vue'
import { FullScreen } from '@element-plus/icons-vue'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

defineOptions({ name: 'BaseNodePrologueEditor' })

const modelValue = defineModel<string>({ required: true })
const dialogVisible = ref(false)
const dialogContent = ref('')
const footers = [null, '=', 0] as unknown as string[]

function openDialog() {
  dialogContent.value = modelValue.value
  dialogVisible.value = true
}

function submitDialog() {
  modelValue.value = dialogContent.value
  dialogVisible.value = false
}

function handleWheel(event: WheelEvent) {
  if (event.ctrlKey) event.preventDefault()
  else event.stopPropagation()
}
</script>

<template>
  <MdEditor v-model="modelValue" :footers="footers" :preview="false" :toolbars="[]" class="prologue-editor" @wheel="handleWheel">
    <template #defFooters>
      <el-button text title="放大编辑" @click="openDialog">
        <MkIcon :icon="FullScreen" />
      </el-button>
    </template>
  </MdEditor>

  <MkDialog v-model="dialogVisible" title="开场白" width="800">
    <MdEditor v-model="dialogContent" :footers="[]" :preview="false" :toolbars="[]" class="h-100!" @wheel="handleWheel" />
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitDialog">确定</el-button>
    </template>
  </MkDialog>
</template>

<style lang="scss" scoped>
.prologue-editor {
  height: 150px;

  :deep(.md-editor-footer) {
    border: 0;
  }
}
</style>
