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
      <MarkdownEditor
        v-if="isEdit"
        v-model="form.content"
        placeholder="请输入分段内容"
        :maxLength="4096"
        :preview="false"
        :toolbars="toolbars"
        style="height: 300px"
        @onUploadImg="onUploadImg"
        :footers="footers"
      >
        <template #defFooters>
          <span style="margin-left: -6px;">/ 4096</span>
        </template>
      </MarkdownEditor>
      <MdPreview
        v-else
        ref="editorRef"
        editorId="preview-only"
        :modelValue="form.content"
        class="maxkb-md"
      />
    </el-form-item>
  </el-form>
</template>
<script setup lang="ts">
import { ref, reactive, onUnmounted, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { MdPreview } from 'md-editor-v3'
import MarkdownEditor from '@/components/markdown-editor/index.vue'
import imageApi from '@/api/image'
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
  'htmlPreview'
] as any[]

const footers = ['markdownTotal', 0, '=', 1, 'scrollSwitch']

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

const onUploadImg = async (files: any, callback: any) => {
  const res = await Promise.all(
    files.map((file: any) => {
      return new Promise((rev, rej) => {
        const fd = new FormData()
        fd.append('file', file)

        imageApi
          .postImage(fd)
          .then((res: any) => {
            rev(res)
          })
          .catch((error) => rej(error))
      })
    })
  )

  callback(res.map((item) => item.data))
}

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
