<template>
  <MdEditor
    v-bind="$attrs"
    v-model="data"
    :preview="false"
    :toolbars="[]"
    class="magnify-md-editor"
    :footers="footers"
  >
    <template #defFooters>
      <el-button text type="info" @click="openDialog">
        <AppIcon iconName="app-magnify" style="font-size: 16px"></AppIcon>
      </el-button>
    </template>
  </MdEditor>
  <!-- 回复内容弹出层 -->
  <el-dialog v-model="dialogVisible" :title="title" append-to-body>
    <MdEditor v-model="cloneContent" :preview="false" :toolbars="[]" :footers="[]"></MdEditor>
    <template #footer>
      <div class="dialog-footer mt-24">
        <el-button type="primary" @click="submitDialog"> 确认</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
defineOptions({ name: 'MdEditorMagnify' })
const props = defineProps<{
  title: String
  modelValue: any
}>()
const emit = defineEmits(['update:modelValue', 'submitDialog'])
const data = computed({
  set: (value) => {
    emit('update:modelValue', value)
  },
  get: () => {
    return props.modelValue
  }
})

const dialogVisible = ref(false)
const cloneContent = ref('')
const footers: any = [null, '=', 0]
function openDialog() {
  cloneContent.value = props.modelValue
  dialogVisible.value = true
}
function submitDialog() {
  emit('submitDialog', cloneContent.value)
  dialogVisible.value = false
}
</script>

<style lang="scss" scoped>
.magnify-md-editor {
  :deep(.md-editor-footer) {
    border: none !important;
  }
}
</style>
