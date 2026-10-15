<script setup lang="ts">
import { computed, ref } from 'vue'
import { MsgSuccess } from '@/utils/message'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'

defineOptions({ name: 'ButtonCreateTermbase' })

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
      MsgSuccess('创建成功')
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
  <el-button type="primary" @click="handleOpenCreateTermbase">
    <MkIcon name="icon_add_outlined" />
    <span>创建词语</span>
  </el-button>
  <MkDialog v-model="visible" title="创建词语" @closed="resetData">
    <el-form @submit.prevent>
      <el-input v-model="content" type="textarea" :rows="7" placeholder="请输入需要保留的专业术语/专属词汇，一行一个，支持输入多个" />
    </el-form>
    <template #footer>
      <!-- 取消创建词语 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 提交创建词语 -->
      <el-button type="primary" :loading="loading" :disabled="!termbases.length" @click="handleCreateTermbase">创建</el-button>
    </template>
  </MkDialog>
</template>
