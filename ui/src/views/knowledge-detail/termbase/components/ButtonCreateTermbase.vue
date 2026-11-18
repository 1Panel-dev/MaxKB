<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import { MsgSuccess } from '@/utils/message'
import { isSystemResource, isSystemSharedResource, isWorkspaceSharedResource } from '@/utils/resource-context'
import { perm } from '@/permission'

/**
 * 知识库「词库」权限判断
 */
type KnowledgeTermbasePermissionMethod = 'termbaseCreate'

function knowledgeTermbasePermission(method: KnowledgeTermbasePermissionMethod): boolean {
  if (isSystemResource()) return Boolean(perm.knowledge.system[method]())
  if (isSystemSharedResource()) return Boolean(perm.knowledge.share[method]())
  if (isWorkspaceSharedResource()) return false // 共享知识库在工作空间侧只读
  return Boolean(perm.knowledge.workspace[method](props.knowledgeId))
}

defineOptions({ name: 'ButtonCreateTermbase' })
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ knowledgeId: string }>()
const emit = defineEmits<{ refresh: [] }>()
const { resourceApi } = useKnowledgeDetailContext()

const visible = ref(false)
const loading = ref(false)
const content = ref('')
const termbases = computed(() =>
  content.value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean),
)

function handleOpenCreateTermbase() {
  visible.value = true
}

function handleCreateTermbase() {
  if (loading.value || !termbases.value.length) return

  loading.value = true
  return (
    resourceApi.termbase.postTermbases?.(props.knowledgeId, termbases.value).then(() => {
      MsgSuccess(t('common.messages.createSuccess'))
      visible.value = false
      emit('refresh')
    }) ?? Promise.resolve()
  )
    .catch(() => {
      // 请求层统一提示错误，保留输入内容以便修正后重试。
    })
    .finally(() => {
      loading.value = false
    })
}

function resetData() {
  content.value = ''
}
</script>

<template>
  <!-- 创建词语 -->
  <el-button v-if="knowledgeTermbasePermission('termbaseCreate')" type="primary" @click="handleOpenCreateTermbase">
    <MkIcon name="icon_add_outlined" />
    <span>{{ t('knowledge.termbase.actions.create') }}</span>
  </el-button>
  <MkDialog v-model="visible" :title="t('knowledge.termbase.actions.create')" @closed="resetData">
    <el-form @submit.prevent>
      <el-input v-model="content" type="textarea" :rows="7" :placeholder="t('knowledge.termbase.content.batchPlaceholder')" />
    </el-form>
    <template #footer>
      <!-- 取消创建词语 -->
      <el-button plain :disabled="loading" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 提交创建词语 -->
      <el-button type="primary" :loading="loading" :disabled="!termbases.length" @click="handleCreateTermbase">
        {{ t('common.actions.create') }}
      </el-button>
    </template>
  </MkDialog>
</template>
