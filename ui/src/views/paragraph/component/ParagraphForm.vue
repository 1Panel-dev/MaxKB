<template>
  <el-form
    ref="paragraphFormRef"
    :model="form"
    label-position="top"
    require-asterisk-position="right"
    :rules="rules"
    @submit.prevent
  >
    <el-form-item label="分段标题">
      <el-input v-if="isEdit" v-model="form.title" placeholder="请输入分段标题"> </el-input>
      <span class="lighter" v-else>{{ form.title || '-' }}</span>
    </el-form-item>
    <el-form-item label="分段内容" prop="content">
      <!-- <el-input
        v-if="isEdit"
        v-model="form.content"
        placeholder="请输入分段内容"
        maxlength="4096"
        show-word-limit
        :rows="8"
        type="textarea"
      > 
     </el-input>-->
      <MdEditor
        v-if="isEdit"
        v-model="form.content"
        placeholder="请输入分段内容"
        :maxLength="4096"
        :preview="false"
        :toolbars="toolbars"
        style="height: 300px"
      />
      <MdPreview
        v-else
        ref="editorRef"
        editorId="preview-only"
        :modelValue="form.content"
        class="maxkb-md"
      />
      <!-- <span v-else class="break-all lighter">{{ form.content }}</span> -->
    </el-form-item>
  </el-form>
</template>
<script setup lang="ts">
import { ref, reactive, onUnmounted, watch, nextTick } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { MdEditor, MdPreview } from 'md-editor-v3'
const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  },
  isEdit: Boolean
})

const toolbars = [
  'bold',
  'underline',
  'italic',
  '-',
  'title',
  'strikeThrough',
  'sub',
  'sup',
  'quote',
  'unorderedList',
  'orderedList',
  'task',
  '-',
  'codeRow',
  'code',
  'link',
  'image',
  'table',
  'mermaid',
  'katex',
  '-',
  'revoke',
  'next',
  '=',
  'pageFullscreen',
  'preview',
  'htmlPreview',
  'catalog'
] as any[]

const editorRef = ref()

const form = ref<any>({
  title: '',
  content: ''
})

const rules = reactive<FormRules>({
  content: [
    { required: true, message: '请输入分段内容', trigger: 'blur' },
    { max: 4096, message: '内容最多不超过 4096 个字', trigger: 'blur' }
  ]
})

const paragraphFormRef = ref<FormInstance>()

watch(
  () => props.data,
  (value) => {
    if (value && JSON.stringify(value) !== '{}') {
      form.value.title = value.title
      form.value.content = value.content
    }
  },
  {
    immediate: true
  }
)
watch(
  () => props.isEdit,
  (value) => {
    if (!value) {
      paragraphFormRef.value?.clearValidate()
    }
  },
  {
    immediate: true
  }
)

/*
  表单校验
*/
function validate() {
  if (!paragraphFormRef.value) return
  return paragraphFormRef.value.validate((valid: any) => {
    return valid
  })
}

// const onHtmlChanged = () => {
//   appendTarget()
// }
// const appendTarget = () => {
//   nextTick(() => {
//     var item = document.getElementsByClassName('maxkb-md')
//     for (var j = 0; j < item.length; j++) {
//       var aTags = item[j].getElementsByTagName('a')
//       for (var i = 0; i < aTags.length; i++) {
//         aTags[i].setAttribute('target', '_blank')
//       }
//     }
//   })
// }

onUnmounted(() => {
  form.value = {
    title: '',
    content: ''
  }
})

defineExpose({
  validate,
  form
})
</script>
<style scoped lang="scss"></style>
