<template>
  <el-dialog
    :title="`${$t('views.chatLog.selectKnowledge')}/${$t('common.fileUpload.document')}`"
    v-model="dialogVisible"
    width="500"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @click.stop
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
        <el-tree-select
          v-model="form.knowledge_id"
          :props="defaultProps"
          node-key="id"
          lazy
          :load="loadTree"
          :placeholder="$t('views.chatLog.selectKnowledgePlaceholder')"
          @change="changeKnowledge"
          :loading="optionLoading"
        >
          <template #default="{ data }">
            <div class="flex align-center">
              <KnowledgeIcon
                class="mr-12"
                :size="20"
                v-if="data.resource_type !== 'folder'"
                :type="data.type"
              />
              <el-avatar v-else class="mr-12" shape="square" :size="20" style="background: none">
                <img
                  src="@/assets/knowledge/icon_file-folder_colorful.svg"
                  style="width: 100%"
                  alt=""
                />
              </el-avatar>

              {{ data.name }}
            </div>
          </template>
        </el-tree-select>
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
import { ref, watch, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import useStore from '@/stores'
import { t } from '@/locales'

const props = defineProps<{
  apiType: 'systemShare' | 'workspace' | 'systemManage'
}>()
const route = useRoute()
const {
  params: { id, documentId }, // id为knowledgeID
} = route as any

const { user } = useStore()

const emit = defineEmits(['refresh'])
const formRef = ref()

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const form = ref<any>({
  knowledge_id: '',
  document_id: '',
})

const rules = reactive<FormRules>({
  knowledge_id: [
    { required: true, message: t('views.chatLog.selectKnowledgePlaceholder'), trigger: 'change' },
  ],
  document_id: [
    { required: true, message: t('views.chatLog.documentPlaceholder'), trigger: 'change' },
  ],
})

const documentList = ref<any[]>([])
const optionLoading = ref(false)
const paragraphList = ref<string[]>([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      knowledge_id: '',
      document_id: '',
    }
    documentList.value = []
    paragraphList.value = []
    formRef.value?.clearValidate()
  }
})

const defaultProps = {
  children: 'children',
  label: 'name',
  isLeaf: (data: any) =>
    data.resource_type ? data.resource_type !== 'folder' : data.workspace_id === 'None',
  disabled: (data: any, node: any) => {
    return data.id === id
  },
}

const loadTree = (node: any, resolve: any) => {
  if (node.isLeaf) return resolve([])
  const folder_id = node.level === 0 ? user.getWorkspaceId() : node.data.id
  loadSharedApi({ type: 'knowledge', systemType: props.apiType })
    .getKnowledgeList({ folder_id: folder_id }, optionLoading)
    .then((res: any) => {
      resolve(res.data)
    })
}

function changeKnowledge(id: string) {
  form.value.document_id = ''
  getDocument(id)
}

function getDocument(id: string) {
  loadSharedApi({ type: 'document', systemType: props.apiType })
    .getDocumentList(id, optionLoading)
    .then((res: any) => {
      documentList.value = res.data?.filter((v: any) => v.id !== documentId)
    })
}

const open = (list: any) => {
  paragraphList.value = list
  formRef.value?.clearValidate()
  dialogVisible.value = true
}
const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      const obj = {
        id_list: paragraphList.value,
      }
      loadSharedApi({ type: 'paragraph', systemType: props.apiType })
        .putMigrateMulParagraph(
          id,
          documentId,
          form.value.knowledge_id,
          form.value.document_id,
          obj,
          loading,
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
