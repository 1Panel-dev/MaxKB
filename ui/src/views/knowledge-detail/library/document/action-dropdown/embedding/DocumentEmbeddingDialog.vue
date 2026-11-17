<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { DocumentTaskState } from '@/api/types'
import { DOCUMENT_TASK_STATE } from '@/api/enums'

defineOptions({ name: 'DocumentEmbeddingDialog' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ loading: boolean }>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ submit: [stateList: DocumentTaskState[]] }>()
const scope = ref<'error' | 'all'>('error')

function handleSubmit() {
  if (props.loading) return
  const stateList = Object.values(DOCUMENT_TASK_STATE).filter((state) => scope.value === 'all' || state !== DOCUMENT_TASK_STATE.SUCCESS)
  emit('submit', stateList)
}
</script>

<template>
  <MkDialog v-model="visible" width="420" :title="t('knowledge.paragraphScope.label')" @closed="scope = 'error'">
    <el-radio-group v-model="scope" class="mk-radio-group-vertical">
      <el-radio value="error">{{ t('knowledge.paragraphScope.unsuccessful') }}</el-radio>
      <el-radio value="all">{{ t('knowledge.paragraphScope.all') }}</el-radio>
    </el-radio-group>
    <template #footer>
      <!-- 取消向量化配置 -->
      <el-button plain :disabled="loading" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 提交向量化 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">{{ t('common.actions.submit') }}</el-button>
    </template>
  </MkDialog>
</template>
