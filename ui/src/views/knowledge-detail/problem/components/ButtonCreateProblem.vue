<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import { MsgSuccess, MsgWarning } from '@/utils/message'
import { isSystemResource, isSystemSharedResource, isWorkspaceSharedResource } from '@/utils/resource-context'
import { perm } from '@/permission'

/**
 * 知识库「问题」权限判断
 */
type KnowledgeProblemPermissionMethod = 'problemCreate'

function knowledgeProblemPermission(method: KnowledgeProblemPermissionMethod): boolean {
  if (isSystemResource()) return Boolean(perm.knowledge.system[method]())
  if (isSystemSharedResource()) return Boolean(perm.knowledge.share[method]())
  if (isWorkspaceSharedResource()) return false // 共享知识库在工作空间侧只读
  return Boolean(perm.knowledge.workspace[method](knowledgeId.value))
}

defineOptions({ name: 'ButtonCreateProblem' })
const { t } = useI18n({ useScope: 'global' })
const emit = defineEmits<{ refresh: [] }>()
const { knowledgeId, resourceApi } = useKnowledgeDetailContext()
const visible = ref(false)
const loading = ref(false)
const content = ref('')
const problems = computed(() =>
  content.value
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean),
)

function handleOpenCreateProblem() {
  visible.value = true
}

function handleCreateProblems() {
  if (loading.value || !problems.value.length) return
  if (problems.value.some((problem) => problem.length > 256)) {
    MsgWarning(t('knowledge.question.content.lengthMessage', { max: 256 }))
    return
  }
  loading.value = true
  return (
    resourceApi.problem.postProblems?.(knowledgeId.value, problems.value).then(() => {
      MsgSuccess(t('common.messages.createSuccess'))
      visible.value = false
      emit('refresh')
    }) ?? Promise.resolve()
  )
    .catch(() => {
      // 请求层提示错误，保留输入以便重试。
    })
    .finally(() => {
      loading.value = false
    })
}

function handleBeforeClose(done: () => void) {
  if (!loading.value) done()
}
</script>

<template>
  <!-- 创建问题 -->
  <el-button v-if="knowledgeProblemPermission('problemCreate')" type="primary" @click="handleOpenCreateProblem">
    <MkIcon name="icon_add_outlined" />
    <span>{{ t('knowledge.question.actions.create') }}</span>
  </el-button>
  <MkDialog v-model="visible" :title="t('knowledge.question.actions.create')" :before-close="handleBeforeClose" @closed="content = ''">
    <el-input v-model="content" type="textarea" :rows="7" :disabled="loading" :placeholder="t('knowledge.question.content.batchPlaceholder')" />
    <template #footer>
      <!-- 取消创建 -->
      <el-button plain :disabled="loading" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 提交问题 -->
      <el-button type="primary" :loading="loading" :disabled="!problems.length" @click="handleCreateProblems">
        {{ t('common.actions.create') }}
      </el-button>
    </template>
  </MkDialog>
</template>
