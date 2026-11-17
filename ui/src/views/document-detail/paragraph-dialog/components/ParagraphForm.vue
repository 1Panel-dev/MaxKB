<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ParagraphUpdatePayload } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import type { Footers, ToolbarNames } from 'md-editor-v3'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import FileApi from '@/api/admin/file'

defineOptions({ name: 'ParagraphForm' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ knowledgeId: string }>()
const paragraphForm = defineModel<ParagraphUpdatePayload>({ required: true })
const formRef = ref<FormInstance>()
const contentMaxLength = 100000
const paragraphRules = computed<FormRules<ParagraphUpdatePayload>>(() => ({
  content: [
    { required: true, whitespace: true, message: t('knowledge.paragraph.content.requiredMessage'), trigger: 'blur' },
    { max: contentMaxLength, message: t('knowledge.paragraph.content.lengthMessage', { max: contentMaxLength }), trigger: 'blur' },
  ],
}))

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
  return Promise.all(files.map((file) => FileApi.postUploadFile(file, props.knowledgeId, FILE_SOURCE_TYPE.KNOWLEDGE).request))
    .then(callback)
    .catch(() => {
      // 上传失败由请求层统一提示。
    })
}

function handleContentBlur() {
  void formRef.value?.validateField('content').catch(() => {})
}

// 校验由 Dialog 的保存流程触发。
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
    :validate-on-rule-change="false"
    label-position="top"
    require-asterisk-position="right"
    class="min-w-0 flex-1"
    @submit.prevent
  >
    <el-form-item :label="t('knowledge.paragraph.heading.label')" prop="title">
      <el-input v-model="paragraphForm.title" maxlength="256" :placeholder="t('knowledge.paragraph.heading.placeholder')" />
    </el-form-item>
    <el-form-item :label="t('knowledge.paragraph.content.label')" prop="content">
      <MdEditor
        v-model="paragraphForm.content"
        :placeholder="t('knowledge.paragraph.content.placeholder')"
        :max-length="contentMaxLength"
        :preview="false"
        :toolbars="toolbars"
        :footers="footers"
        style="height: 300px"
        @on-upload-img="onUploadImg"
        @on-blur="handleContentBlur"
      >
        <template #defFooters>
          <span class="-ml-[6px]">/ {{ contentMaxLength }}</span>
        </template>
      </MdEditor>
    </el-form-item>
  </el-form>
</template>

<style scoped lang="scss"></style>
