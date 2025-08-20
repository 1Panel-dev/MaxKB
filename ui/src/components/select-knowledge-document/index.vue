<template>
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
        @changeDocument="changeDocument"
      >
        <el-option v-for="item in documentList" :key="item.id" :label="item.name" :value="item.id">
          {{ item.name }}
        </el-option>
      </el-select>
    </el-form-item>
  </el-form>
</template>
<script lang="ts" setup>
import { ref, onUnmounted, reactive, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import useStore from '@/stores'
import { t } from '@/locales'
const props = defineProps<{
  data?: {
    type: Object
    default: () => {}
  }
  apiType: 'systemShare' | 'workspace' | 'systemManage'
  isApplication?: boolean,
  workspaceId?: string,
}>()

const { user } = useStore()

const emit = defineEmits(['changeKnowledge', 'changeDocument'])
const formRef = ref()
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

const defaultProps = {
  children: 'children',
  label: 'name',
  isLeaf: (data: any) =>
    data.resource_type ? data.resource_type !== 'folder' : data.workspace_id === 'None',
  disabled: (data: any, node: any) => {
    return data.resource_type === 'folder' && node?.isLeaf
  },
}

const loadTree = async (node: any, resolve: any) => {
  if (node.isLeaf) return resolve([])
  const folder_id = node.level === 0 ? user.getWorkspaceId() : node.data.id
  const obj =
   props.apiType === 'systemManage'
      ? {
          workspace_id: props.workspaceId,
          folder_id:  node.level === 0 ? props.workspaceId : node.data.id,
        }
      : {
          folder_id: folder_id,
        }
  await loadSharedApi({ type: 'knowledge', systemType: props.apiType })
    .getKnowledgeList(obj, optionLoading)
    .then((res: any) => {
      resolve(res.data)
    })
}

const documentList = ref<any[]>([])
const optionLoading = ref(false)

function changeKnowledge(id: string) {
  form.value.document_id = ''
  getDocument(id)
  emit('changeKnowledge', id)
}

function changeDocument(document_id: string) {
  emit('changeKnowledge', document_id)
}

function getDocument(id: string) {
  loadSharedApi({ type: 'document', systemType: props.apiType })
    .getDocumentList(id, optionLoading)
    .then((res: any) => {
      documentList.value = res.data
      if (props.isApplication) {
        if (localStorage.getItem(id + 'chat_document_id')) {
          form.value.document_id = localStorage.getItem(id + 'chat_document_id') as string
        }
        if (!documentList.value.find((v) => v.id === form.value.document_id)) {
          form.value.document_id = ''
        }
      }
    })
}

watch(
  () => props.data,
  (value: any) => {
    if (value && JSON.stringify(value) !== '{}') {
      form.value.knowledge_id = value.knowledge_id
      form.value.document_id = value.document_id
    }
  },
  {
    immediate: true,
  },
)

/*
  表单校验
*/
function validate() {
  if (!formRef.value) return
  return formRef.value.validate((valid: any) => {
    return valid
  })
}

function clearValidate() {
  form.value = {
    knowledge_id: '',
    document_id: '',
  }
  formRef.value?.clearValidate()
}

onUnmounted(() => {
  clearValidate()
})

defineExpose({
  validate,
  form,
  clearValidate,
})
</script>
