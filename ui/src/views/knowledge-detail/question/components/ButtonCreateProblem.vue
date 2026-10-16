<script setup lang="ts">
import { computed, ref } from 'vue'
import { MsgSuccess, MsgWarning } from '@/utils/message'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'

defineOptions({ name: 'ButtonCreateProblem' })
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
    MsgWarning('每个问题最多输入 256 个字符')
    return
  }
  loading.value = true
  return (
    resourceApi.problem.postProblems?.(knowledgeId.value, problems.value).then(() => {
      MsgSuccess('创建成功')
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
  <el-button type="primary" @click="handleOpenCreateProblem">
    <MkIcon name="icon_add_outlined" />
    <span>创建问题</span>
  </el-button>
  <MkDialog v-model="visible" title="创建问题" :before-close="handleBeforeClose" @closed="content = ''">
    <el-input v-model="content" type="textarea" :rows="7" :disabled="loading" placeholder="请输入问题，一行一个，支持输入多个" />
    <template #footer>
      <!-- 取消创建 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 提交问题 -->
      <el-button type="primary" :loading="loading" :disabled="!problems.length" @click="handleCreateProblems">创建</el-button>
    </template>
  </MkDialog>
</template>
