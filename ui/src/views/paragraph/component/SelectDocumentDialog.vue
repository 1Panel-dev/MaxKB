<template>
  <el-dialog
    :title="`${$t('views.chatLog.selectKnowledge')}/${$t('common.fileUpload.document')}`"
    v-model="dialogVisible"
    width="500"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @click.stop
  >
    <SelectKnowledgeDocument
      ref="SelectKnowledgeDocumentRef"
      :apiType="apiType"
      @changeKnowledge="changeKnowledge"
      @changeDocument="changeDocument"
      :isApplication="true"
      :workspace-id="knowledgeDetail.workspace_id"
    />
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submitForm" :loading="loading">
          {{ $t('views.document.setting.migration') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import SelectKnowledgeDocument from '@/components/select-knowledge-document/index.vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const props = defineProps<{
  apiType: 'systemShare' | 'workspace' | 'systemManage'
}>()
const route = useRoute()
const {
  params: { id, documentId }, // id为knowledgeID
  query: { from, isShared },
} = route as any

const shareDisabled = computed(() => {
  return isShared === 'true'
})

const emit = defineEmits(['refresh'])
const SelectKnowledgeDocumentRef = ref()
const knowledgeDetail = ref<any>({})
const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const paragraphList = ref<string[]>([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    paragraphList.value = []
    SelectKnowledgeDocumentRef.value?.clearValidate()
  }
})

const open = (list: any) => {
  getDetail()
  paragraphList.value = list
  dialogVisible.value = true
}
const submitForm = async () => {
  if (await SelectKnowledgeDocumentRef.value?.validate()) {
    const obj = {
      id_list: paragraphList.value,
    }
    loadSharedApi({ type: 'paragraph', systemType: props.apiType })
      .putMigrateMulParagraph(
        id,
        documentId,
        SelectKnowledgeDocumentRef.value.form.knowledge_id,
        SelectKnowledgeDocumentRef.value.form.document_id,
        obj,
        loading,
      )
      .then(() => {
        emit('refresh')
        dialogVisible.value = false
      })
  }
}

function getDetail() {
  loadSharedApi({ type: 'knowledge', systemType: props.apiType, isShared: shareDisabled.value })
    .getKnowledgeDetail(id, loading)
    .then((res: any) => {
      knowledgeDetail.value = res.data
    })
}

function changeKnowledge(dataset_id: string) {
  localStorage.setItem(id + 'chat_dataset_id', dataset_id)
}

function changeDocument(document_id: string) {
  localStorage.setItem(id + 'chat_document_id', document_id)
}

defineExpose({ open, dialogVisible })
</script>
<style lang="scss" scoped></style>
