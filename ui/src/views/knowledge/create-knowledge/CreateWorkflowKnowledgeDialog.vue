<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import KnowledgeWorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import { MsgSuccess } from '@/utils/message'
import { knowledgeTemplate } from '../template'

defineOptions({ name: 'CreateWorkflowKnowledgeDialog' })

interface WorkflowKnowledgeDraft {
  desc: string
  name: string
}

const route = useRoute()
const router = useRouter()

const props = defineProps<{ folderId: string }>()

const dialogVisible = ref(false)
const loading = ref(false)
const knowledgeFormRef = ref<FormInstance>()
const knowledgeForm = reactive<WorkflowKnowledgeDraft>({ desc: '', name: '' })
const knowledgeFormRules: FormRules<typeof knowledgeForm> = {
  name: [{ required: true, message: '请输入知识库名称', trigger: 'blur' }],
}
const createDisabled = computed(() => !knowledgeForm.name.trim())

function submit() {
  knowledgeFormRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    KnowledgeWorkflowApi.postKnowledgeWorkflow({
      desc: knowledgeForm.desc.trim(),
      folder_id: props.folderId,
      name: knowledgeForm.name.trim(),
      type: KNOWLEDGE_TYPE.WORKFLOW,
      work_flow: cloneDeep(knowledgeTemplate.default),
    })
      .then((knowledge) => {
        MsgSuccess('创建成功')
        dialogVisible.value = false
        return router.push({
          name: 'workflow-knowledge',
          params: { knowledgeId: knowledge.id, workspaceId: route.params.workspaceId },
        })
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function open() {
  dialogVisible.value = true
}

function resetData() {
  Object.assign(knowledgeForm, { desc: '', name: '' })
  loading.value = false
  knowledgeFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" title="创建工作流知识库" align-center @closed="resetData">
    <el-form
      ref="knowledgeFormRef"
      :model="knowledgeForm"
      :rules="knowledgeFormRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent="submit"
    >
      <el-form-item label="名称" prop="name">
        <el-input
          v-model="knowledgeForm.name"
          maxlength="64"
          placeholder="请输入知识库名称"
          show-word-limit
          @blur="knowledgeForm.name = knowledgeForm.name.trim()"
        />
      </el-form-item>

      <el-form-item label="描述">
        <el-input
          v-model="knowledgeForm.desc"
          maxlength="256"
          placeholder="描述该知识库的应用场景及用途"
          :rows="4"
          show-word-limit
          type="textarea"
          @blur="knowledgeForm.desc = knowledgeForm.desc.trim()"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain :disabled="loading" @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :disabled="createDisabled" :loading="loading" @click="submit">创建</el-button>
    </template>
  </MkDialog>
</template>
