<template>
  <el-dialog
    :title="`${$t('views.chatLog.selectKnowledge')}/${$t('common.fileUpload.document')}`"
    v-model="dialogVisible"
    width="500"
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
      <el-form-item :label="$t('views.chatLog.selectKnowledge')" prop="knowledge_id">
        <el-select
          v-model="form.knowledge_id"
          filterable
          :placeholder="$t('views.chatLog.selectKnowledgePlaceholder')"
          :loading="optionLoading"
          @change="changeknowledge"
        >
          <el-option v-for="item in knowledgeList" :key="item.id" :label="item.name" :value="item.id">
            <span class="flex align-center">
              <el-avatar
                v-if="!item.knowledge_id && item.type === '1'"
                class="mr-12 avatar-purple"
                shape="square"
                :size="24"
              >
                <img src="@/assets/knowledge/icon_web.svg" style="width: 58%" alt="" />
              </el-avatar>
              <el-avatar
                v-else-if="!item.knowledge_id && item.type === '2'"
                class="mr-12 avatar-purple"
                shape="square"
                :size="24"
                style="background: none"
              >
                <img src="@/assets/knowledge/logo_lark.svg" style="width: 100%" alt="" />
              </el-avatar>
              <el-avatar
                v-else-if="!item.knowledge_id && item.type === '0'"
                class="mr-12 avatar-blue"
                shape="square"
                :size="24"
              >
                <img src="@/assets/knowledge/icon_document.svg" style="width: 58%" alt="" />
              </el-avatar>
              {{ item.name }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('views.chatLog.saveToDocument')" prop="document_id">
        <el-select
          v-model="form.document_id"
          filterable
          :placeholder="$t('views.chatLog.documentPlaceholder')"
          :loading="optionLoading"
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
          {{ $t('views.document.setting.migration') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import paragraphApi from '@/api/shared/paragraph'
import useStore from '@/stores'
import { t } from '@/locales'
const { knowledge, document } = useStore()

const route = useRoute()
const {
  params: { id, documentId }
} = route as any

const emit = defineEmits(['refresh'])
const formRef = ref()

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const form = ref<any>({
  knowledge_id: '',
  document_id: ''
})

const rules = reactive<FormRules>({
  knowledge_id: [
    { required: true, message: t('views.chatLog.selectknowledgePlaceholder'), trigger: 'change' }
  ],
  document_id: [{ required: true, message: t('views.chatLog.documentPlaceholder'), trigger: 'change' }]
})

const knowledgeList = ref<any[]>([])
const documentList = ref<any[]>([])
const optionLoading = ref(false)
const paragraphList = ref<string[]>([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      knowledge_id: '',
      document_id: ''
    }
    knowledgeList.value = []
    documentList.value = []
    paragraphList.value = []
    formRef.value?.clearValidate()
  }
})

function changeknowledge(id: string) {
  form.value.document_id = ''
  getDocument(id)
}

function getDocument(id: string) {
  document.asyncGetAllDocument(id, loading).then((res: any) => {
    documentList.value = res.data?.filter((v: any) => v.id !== documentId)
  })
}

function getknowledge() {
  knowledge.asyncGetFolderKnowledge(loading).then((res: any) => {
    knowledgeList.value = res.data
  })
}

const open = (list: any) => {
  paragraphList.value = list
  getknowledge()
  formRef.value?.clearValidate()
  dialogVisible.value = true
}
const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      paragraphApi
        .putMigrateMulParagraph(
          id,
          documentId,
          form.value.knowledge_id,
          form.value.document_id,
          paragraphList.value,
          loading
        )
        .then(() => {
          emit('refresh')
          dialogVisible.value = false
        })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
