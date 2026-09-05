<script setup lang="ts">
import { ref } from 'vue'
import type { Footers } from 'md-editor-v3'

defineOptions({ name: 'MdEditorMagnify', inheritAttrs: false })

const modelValue = defineModel<string>({ required: true })
defineProps<{ title: string }>()

const emit = defineEmits<{ submitDialog: [content: string] }>()

const footers: Footers[] = ['=', 0]
const dialogVisible = ref(false)
const dialogContent = ref('')

function openEditorDialog() {
  dialogContent.value = modelValue.value
  dialogVisible.value = true
}

function closeEditorDialog() {
  dialogVisible.value = false
}

function submitEditorDialog() {
  modelValue.value = dialogContent.value
  emit('submitDialog', dialogContent.value)
  closeEditorDialog()
}
</script>

<template>
  <MdEditor v-model="modelValue" :preview="false" :toolbars="[]" :footers="footers" class="magnify-md-editor" v-bind="$attrs">
    <template #defFooters>
      <el-button text @click="openEditorDialog" class="mr-1 mb-1">
        <MkIcon name="icon_magnify_outlined" />
      </el-button>
    </template>
  </MdEditor>

  <MkDialog v-model="dialogVisible" :title="title" align-center>
    <MdEditor v-model="dialogContent" :preview="false" :toolbars="[]" :footers="[]" class="magnify-dialog-editor" />

    <template #footer>
      <el-button type="primary" @click="submitEditorDialog">确定</el-button>
    </template>
  </MkDialog>
</template>

<style scoped lang="scss"></style>
