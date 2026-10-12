<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { Footers, ToolbarNames } from 'md-editor-v3'
import FileApi from '@/api/admin/file'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import type { ParagraphUpdatePayload } from '@/api/types'

defineOptions({ name: 'ParagraphForm' })
const props = withDefaults(defineProps<{ knowledgeId: string; disabled?: boolean }>(), { disabled: false })
const paragraphForm = defineModel<ParagraphUpdatePayload>({ required: true })
const formRef = ref<FormInstance>()
const paragraphRules: FormRules<ParagraphUpdatePayload> = {
  content: [
    { required: true, whitespace: true, message: '请输入内容', trigger: 'blur' },
    { max: 100000, message: '内容最多 100000 字符', trigger: 'blur' },
  ],
}

/* Markdown 内容编辑与知识库图片上传 */
const toolbars: ToolbarNames[] = [
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
]
const footers: Footers[] = ['markdownTotal', 0, '=', 'scrollSwitch']

function onUploadImg(files: File[], callback: (urls: string[]) => void) {
  if (props.disabled) return
  return Promise.all(files.map((file) => FileApi.postUploadFile(file, props.knowledgeId, FILE_SOURCE_TYPE.KNOWLEDGE).request))
    .then(callback)
    .catch(() => {
      // 上传失败由请求层统一提示。
    })
}

function handleContentBlur() {
  void formRef.value?.validateField('content').catch(() => {})
}

// 校验由 Dialog 的保存流程触发，业务只读状态由 disabled 控制。
function validate() {
  return formRef.value?.validate() ?? Promise.resolve(false)
}

defineExpose({ validate })
</script>

<template>
  <el-form
    ref="formRef"
    :model="paragraphForm"
    :rules="paragraphRules"
    :disabled="disabled"
    label-position="top"
    class="min-w-0 flex-1"
    @submit.prevent
  >
    <el-form-item label="标题" prop="title">
      <el-input v-model="paragraphForm.title" maxlength="256" placeholder="请输入标题" />
    </el-form-item>
    <el-form-item label="内容" prop="content">
      <MdEditor
        v-model="paragraphForm.content"
        placeholder="请输入内容"
        :max-length="100000"
        :preview="false"
        :toolbars="toolbars"
        :footers="footers"
        :disabled="disabled"
        style="height: 300px"
        @on-upload-img="onUploadImg"
        @on-blur="handleContentBlur"
      >
        <template #defFooters>
          <span class="-ml-[6px]">/ 100000</span>
        </template>
      </MdEditor>
    </el-form-item>
  </el-form>
</template>

<style scoped lang="scss"></style>
