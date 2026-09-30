<script setup lang="ts">
import { ref } from 'vue'
import { DOCUMENT_TASK_STATE } from '@/api/enums'
import type { DocumentTaskState } from '@/api/types'

defineOptions({ name: 'DocumentEmbeddingDialog' })
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
  <MkDialog v-model="visible" width="420" title="选择分段" @closed="scope = 'error'">
    <el-radio-group v-model="scope" class="mk-radio-group-vertical">
      <el-radio value="error">仅执行未成功部分</el-radio>
      <el-radio value="all">全部分段</el-radio>
    </el-radio-group>
    <template #footer>
      <!-- 取消向量化配置 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 提交向量化 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">提交</el-button>
    </template>
  </MkDialog>
</template>
