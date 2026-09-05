<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { useFormItem } from 'element-plus'
import type { Footers } from 'md-editor-v3'

defineOptions({ name: 'MdEditorMagnify', inheritAttrs: false })

const modelValue = defineModel<string>({ required: true })
const props = withDefaults(defineProps<{ title: string; validateEvent?: boolean }>(), { validateEvent: true })

const emit = defineEmits<{ submitDialog: [content: string] }>()
const { formItem } = useFormItem()

const footers: Footers[] = ['=', 0]
const dialogVisible = ref(false)
const dialogContent = ref('')

// 仅接入配置了字段的 FormItem；规则及 trigger 是否匹配由 FormItem 自身判定。
function validateFormItem(trigger: 'blur' | 'change') {
  if (!props.validateEvent || !formItem?.propString) return
  formItem.validate(trigger).catch(() => {})
}

watch(modelValue, () => validateFormItem('change'))

function openEditorDialog() {
  dialogContent.value = modelValue.value
  dialogVisible.value = true
}

function closeEditorDialog() {
  dialogVisible.value = false
}

async function submitEditorDialog() {
  modelValue.value = dialogContent.value
  emit('submitDialog', dialogContent.value)
  closeEditorDialog()
  await nextTick()
  validateFormItem('blur')
}
</script>

<template>
  <MdEditor
    v-model="modelValue"
    :preview="false"
    :toolbars="[]"
    :footers="footers"
    class="magnify-md-editor"
    v-bind="$attrs"
    @blur="validateFormItem('blur')"
  >
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
