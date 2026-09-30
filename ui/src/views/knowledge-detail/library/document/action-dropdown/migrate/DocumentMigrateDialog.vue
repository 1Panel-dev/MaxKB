<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { KnowledgeItem } from '@/api/types'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DocumentMigrateDialog' })
const props = defineProps<{ api: typeof DocumentApi; knowledgeId: string }>()
const emit = defineEmits<{ refresh: []; closed: [] }>()
const visible = ref(false)
const loading = defineModel<boolean>('loading', { default: false })
const optionLoading = ref(false)
const knowledgeOptions = ref<KnowledgeItem[]>([])
const knowledgeById = computed(() => new Map(knowledgeOptions.value.map((knowledge) => [knowledge.id, knowledge])))
const migrateFormRef = useTemplateRef<FormInstance>('migrateFormRef')
const migrateForm = reactive({ targetKnowledgeId: '' })
const migrateRules: FormRules<typeof migrateForm> = {
  targetKnowledgeId: [{ required: true, message: '请选择知识库', trigger: 'change' }],
}
const targetDocumentIds = ref<string[]>([])

// 打开迁移弹窗，固定本次文档并查询目标知识库。
function open(documentIds: string[]) {
  if (loading.value || optionLoading.value || !documentIds.length) return
  targetDocumentIds.value = [...documentIds]
  visible.value = true
  optionLoading.value = true
  KnowledgeApi.getAllKnowledge()
    .then((knowledge) => {
      knowledgeOptions.value = knowledge.filter(({ id }) => id !== props.knowledgeId)
    })
    .catch(() => {
      // 请求层统一提示错误，保留当前输入。
    })
    .finally(() => {
      optionLoading.value = false
    })
}

// 迁移成功后关闭并通知页面刷新，失败保留选择。
async function handleSubmit() {
  if (loading.value || optionLoading.value || !(await migrateFormRef.value?.validate().catch(() => false))) return
  loading.value = true
  return props.api
    .putMigrateDocuments(props.knowledgeId, migrateForm.targetKnowledgeId, targetDocumentIds.value)
    .then(() => {
      MsgSuccess('迁移成功')
      visible.value = false
      emit('refresh')
    })
    .catch(() => {
      // 请求层统一提示错误，保留当前输入。
    })
    .finally(() => {
      loading.value = false
    })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="文档迁移到" @closed="emit('closed')">
    <el-form ref="migrateFormRef" :model="migrateForm" :rules="migrateRules" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="选择知识库" prop="targetKnowledgeId">
        <el-select v-model="migrateForm.targetKnowledgeId" fit-input-width filterable placeholder="请选择知识库" :loading="optionLoading">
          <template v-for="target in knowledgeOptions" :key="target.id">
            <el-option :label="target.name" :value="target.id">
              <div class="flex-align-center min-w-0 gap-2">
                <KnowledgeIcon :type="target.type" :size="20" class="shrink-0" />
                <span class="truncate" :title="target.name">{{ target.name }}</span>
              </div>
            </el-option>
          </template>
          <template #label="{ label, value }">
            <span class="flex-align-center gap-2">
              <KnowledgeIcon :type="knowledgeById.get(value)?.type" :size="20" class="shrink-0" />
              <span class="truncate" :title="label">{{ label }}</span>
            </span>
          </template>
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消文档迁移 -->
      <el-button plain :disabled="loading || optionLoading" @click="visible = false">取消</el-button>
      <!-- 确认迁移文档 -->
      <el-button type="primary" :loading="loading" :disabled="optionLoading" @click="handleSubmit">确认</el-button>
    </template>
  </MkDialog>
</template>
