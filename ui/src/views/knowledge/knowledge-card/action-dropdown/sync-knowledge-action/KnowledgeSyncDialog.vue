<script setup lang="ts">
import { ref } from 'vue'
import type KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'
import { KNOWLEDGE_SYNC_TYPE } from '@/api/enums'
import type { KnowledgeSyncType } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'KnowledgeSyncDialog' })
const props = defineProps<{ api: typeof KnowledgeApi | typeof SystemResourceKnowledgeApi; knowledgeId: string }>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ closed: [] }>()

/* Web 知识库同步方式与提交 */
const visible = ref(false)
const syncType = ref<KnowledgeSyncType>(KNOWLEDGE_SYNC_TYPE.INCREMENTAL)
const syncOptions = [
  { value: KNOWLEDGE_SYNC_TYPE.INCREMENTAL, label: '增量同步', description: '文档内容无更新时跳过，有更新时则更新文档的分段' },
  { value: KNOWLEDGE_SYNC_TYPE.REPLACE, label: '替换同步', description: '重新获取 Web 站点文档，替换本地知识库中相同URL的文档' },
  { value: KNOWLEDGE_SYNC_TYPE.COMPLETE, label: '整体同步', description: '先删除知识库中所有文档，重新从Web站点获取文档' },
] as const

function open() {
  visible.value = true
}

function handleSubmit() {
  if (loading.value) return
  loading.value = true
  return props.api
    .putSyncWebKnowledge(props.knowledgeId, syncType.value)
    .then(() => {
      MsgSuccess('同步任务发送成功')
      visible.value = false
    })
    .finally(() => {
      loading.value = false
    })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="同步知识库" :show-close="!loading" @closed="emit('closed')">
    <p class="mb-2">同步方式</p>
    <el-radio-group v-model="syncType" :disabled="loading" class="space-y-2">
      <template v-for="option in syncOptions" :key="option.value">
        <el-card shadow="hover" class="w-full" :class="{ 'border-primary!': syncType === option.value }">
          <el-radio :value="option.value" class="mk-card-radio">
            <h6>{{ option.label }}</h6>
            <span class="mt-1 block text-sm text-N600">{{ option.description }}</span>
          </el-radio>
        </el-card>
      </template>
    </el-radio-group>
    <p class="mt-4 text-danger">
      {{
        syncType === KNOWLEDGE_SYNC_TYPE.INCREMENTAL
          ? '注意：增量同步会跳过内容无更新的文档，内容有更新时会更新文档的分段，请谨慎操作。'
          : '注意：同步会删除已有数据重新获取新数据，请谨慎操作。'
      }}
    </p>
    <template #footer>
      <!-- 取消同步 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 确认同步 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">确认</el-button>
    </template>
  </MkDialog>
</template>
