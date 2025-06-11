<template>
  <el-dialog
    :title="$t('views.log.editContent')"
    v-model="dialogVisible"
    width="600"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form
      ref="formRef"
      :model="form"
      label-position="top"
      require-asterisk-position="right"
      :rules="rules"
      @submit.prevent
    >
      <el-form-item :label="$t('views.paragraph.relatedProblem.title')">
        <el-input
          v-model="form.problem_text"
          :placeholder="$t('views.paragraph.relatedProblem.title')"
          maxlength="256"
          show-word-limit
        >
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('common.content')" prop="content">
        <MdEditor
          v-model="form.content"
          :placeholder="$t('views.log.form.content.placeholder')"
          :maxLength="100000"
          :preview="false"
          :toolbars="toolbars"
          style="height: 300px"
          @onUploadImg="onUploadImg"
          :footers="footers"
        >
          <template #defFooters>
            <span style="margin-left: -6px">/ 100000</span>
          </template>
        </MdEditor>
      </el-form-item>
      <el-form-item :label="$t('common.title')">
        <el-input
          show-word-limit
          v-model="form.title"
          :placeholder="$t('views.log.form.title.placeholder')"
          maxlength="256"
        >
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('views.log.selectDataset')" prop="dataset_id">
        <el-select
          v-model="form.dataset_id"
          filterable
          :placeholder="$t('views.log.selectDatasetPlaceholder')"
          :loading="optionLoading"
          @change="changeDataset"
        >
          <el-option v-for="item in datasetList" :key="item.id" :label="item.name" :value="item.id">
            <span class="flex align-center">
              <AppAvatar
                v-if="!item.dataset_id && item.type === '1'"
                class="mr-12 avatar-purple"
                shape="square"
                :size="24"
              >
                <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
              </AppAvatar>
              <AppAvatar
                v-else-if="!item.dataset_id && item.type === '2'"
                class="mr-8 avatar-purple"
                shape="square"
                :size="24"
                style="background: none"
              >
                <img src="@/assets/logo_lark.svg" style="width: 100%" alt="" />
              </AppAvatar>
              <AppAvatar
                v-else-if="!item.dataset_id && item.type === '0'"
                class="mr-12 avatar-blue"
                shape="square"
                :size="24"
              >
                <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
              </AppAvatar>
              {{ item.name }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('views.log.saveToDocument')" prop="document_id">
        <el-select
          v-model="form.document_id"
          filterable
          :placeholder="$t('views.log.documentPlaceholder')"
          :loading="optionLoading"
          @change="changeDocument"
        >
          <el-option
            v-for="item in documentList"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          >
            {{ item.name }}
          </el-option>
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submitForm(formRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import logApi from '@/api/log'
import imageApi from '@/api/image'
import useStore from '@/stores'
import { t } from '@/locales'
const { application, document, user } = useStore()

const route = useRoute()
const {
  params: { id }
} = route as any

const emit = defineEmits(['refresh'])
const formRef = ref()

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

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const form = ref<any>({
  chat_id: '',
  record_id: '',
  problem_text: '',
  title: '',
  content: '',
  dataset_id: '',
  document_id: ''
})

const rules = reactive<FormRules>({
  content: [{ required: true, message: t('views.log.form.content.placeholder'), trigger: 'blur' }],
  dataset_id: [
    { required: true, message: t('views.log.selectDatasetPlaceholder'), trigger: 'change' }
  ],
  document_id: [{ required: true, message: t('views.log.documentPlaceholder'), trigger: 'change' }]
})

const datasetList = ref<any[]>([])
const documentList = ref<any[]>([])
const optionLoading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      chat_id: '',
      record_id: '',
      problem_text: '',
      title: '',
      content: '',
      dataset_id: '',
      document_id: ''
    }
    datasetList.value = []
    documentList.value = []
    formRef.value?.clearValidate()
  }
})

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

function changeDataset(dataset_id: string) {
  localStorage.setItem(id + 'chat_dataset_id', dataset_id)
  form.value.document_id = ''
  getDocument(dataset_id)
}

function changeDocument(document_id: string) {
  localStorage.setItem(id + 'chat_document_id', document_id)
}

function getDocument(dataset_id: string) {
  document.asyncGetAllDocument(dataset_id, loading).then((res: any) => {
    documentList.value = res.data
    if (localStorage.getItem(id + 'chat_document_id')) {
      form.value.document_id = localStorage.getItem(id + 'chat_document_id') as string
    }
    if (!documentList.value.find((v) => v.id === form.value.document_id)) {
      form.value.document_id = ''
    }
  })
}

function getDataset() {
  application.asyncGetApplicationDataset(id, loading).then((res: any) => {
    datasetList.value = res.data
    if (localStorage.getItem(id + 'chat_dataset_id')) {
      form.value.dataset_id = localStorage.getItem(id + 'chat_dataset_id') as string
      if (!datasetList.value.find((v) => v.id === form.value.dataset_id)) {
        form.value.dataset_id = ''
        form.value.document_id = ''
      } else {
        getDocument(form.value.dataset_id)
      }
    }
  })
}

const open = (data: any) => {
  getDataset()
  form.value.chat_id = data.chat_id
  form.value.record_id = data.id
  form.value.problem_text = data.problem_text ? data.problem_text.substring(0, 256) : ''
  form.value.content = data.answer_text
  formRef.value?.clearValidate()
  dialogVisible.value = true
}
const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      const obj = {
        title: form.value.title,
        content: form.value.content,
        problem_text: form.value.problem_text
      }
      logApi
        .putChatRecordLog(
          id,
          form.value.chat_id,
          form.value.record_id,
          form.value.dataset_id,
          form.value.document_id,
          obj,
          loading
        )
        .then((res: any) => {
          emit('refresh', res.data)
          dialogVisible.value = false
        })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
