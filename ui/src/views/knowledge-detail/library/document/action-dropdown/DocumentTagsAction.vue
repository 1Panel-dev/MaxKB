<script setup lang="ts">
import { computed, ref } from 'vue'
import type { KnowledgeTagGroup } from '@/api/types'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DocumentTagsAction' })
const props = defineProps<{ api: typeof DocumentApi; knowledgeId: string; documentIds: string[]; manageTags?: boolean; disabled?: boolean }>()
const emit = defineEmits<{ refresh: [] }>()
const visible = ref(false)
const loading = ref(false)
const optionLoading = ref(false)
const targetDocumentIds = ref<string[]>([])
const manage = ref(false)
const selectedTagIds = ref<string[]>([])
const tagGroups = ref<KnowledgeTagGroup[]>([])
const documentTagGroups = ref<KnowledgeTagGroup[]>([])
const documentTags = computed(() => documentTagGroups.value.flatMap((group) => group.values.map((tag) => ({ ...tag, key: group.key }))))

function handleOpenDialog() {
  if (props.disabled || loading.value || optionLoading.value || !props.documentIds.length) return
  const ids = props.documentIds
  const manageTags = props.manageTags ?? false
  targetDocumentIds.value = [...ids]
  manage.value = manageTags
  selectedTagIds.value = []
  documentTagGroups.value = []
  visible.value = true
  optionLoading.value = true
  Promise.all([
    KnowledgeApi.getKnowledgeTags(props.knowledgeId),
    manageTags && ids[0] ? props.api.getDocumentTags(props.knowledgeId, ids[0]) : Promise.resolve([]),
  ])
    .then(([groups, currentTags]) => {
      tagGroups.value = groups
      documentTagGroups.value = currentTags
    })
    .catch(() => {
      // 请求层统一提示错误，保留当前输入。
    })
    .finally(() => {
      optionLoading.value = false
    })
}

function handleAddTags() {
  if (loading.value || !selectedTagIds.value.length) return
  loading.value = true
  return props.api
    .postAddDocumentTags(props.knowledgeId, targetDocumentIds.value, selectedTagIds.value)
    .then(() => {
      MsgSuccess('添加成功')
      emit('refresh')
      selectedTagIds.value = []
      if (manage.value && targetDocumentIds.value[0]) {
        return props.api.getDocumentTags(props.knowledgeId, targetDocumentIds.value[0]).then((groups) => {
          documentTagGroups.value = groups
        })
      }
      visible.value = false
    })
    .catch(() => {
      // 请求层统一提示错误，保留当前输入。
    })
    .finally(() => {
      loading.value = false
    })
}

function handleDeleteTag(tagId: string) {
  const documentId = targetDocumentIds.value[0]
  if (loading.value || !documentId) return
  loading.value = true
  return props.api
    .putDeleteDocumentTags(props.knowledgeId, documentId, [tagId])
    .then(() => {
      MsgSuccess('移除成功')
      documentTagGroups.value = documentTagGroups.value.map((group) => ({ ...group, values: group.values.filter(({ id }) => id !== tagId) }))
      emit('refresh')
    })
    .catch(() => {
      // 请求层统一提示错误，保留当前输入。
    })
    .finally(() => {
      loading.value = false
    })
}

function handleClosed() {
  targetDocumentIds.value = []
  selectedTagIds.value = []
  documentTagGroups.value = []
  tagGroups.value = []
}
</script>

<template>
  <!-- 文档标签设置或批量添加入口 -->
  <MkAction
    :label="manageTags ? '标签设置' : '添加标签'"
    icon="icon_tag"
    :disabled="disabled || loading || !documentIds.length"
    @click="handleOpenDialog"
  />
  <MkDialog v-model="visible" :title="manage ? '标签设置' : '添加标签'" :show-close="!loading && !optionLoading" @closed="handleClosed">
    <el-form v-loading="loading || optionLoading" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="标签">
        <el-select v-model="selectedTagIds" multiple filterable placeholder="请选择标签" :loading="optionLoading">
          <template v-for="group in tagGroups" :key="group.key">
            <el-option-group :label="group.key">
              <template v-for="tag in group.values" :key="tag.id">
                <el-option :label="`${group.key}: ${tag.value}`" :value="tag.id" :disabled="documentTags.some((current) => current.id === tag.id)" />
              </template>
            </el-option-group>
          </template>
        </el-select>
      </el-form-item>
    </el-form>
    <el-table v-if="manage" :data="documentTags" v-loading="loading || optionLoading">
      <el-table-column prop="key" label="标签名" />
      <el-table-column prop="value" label="标签值" />
      <el-table-column label="操作" width="80">
        <template #default="{ row }">
          <!-- 移除文档标签 -->
          <MkAction display="button" label="移除" icon="icon_delete-trash_outlined" :disabled="loading" @click="handleDeleteTag(row.id)" />
        </template>
      </el-table-column>
    </el-table>
    <template #footer>
      <!-- 关闭标签设置 -->
      <el-button :disabled="loading || optionLoading" @click="visible = false">关闭</el-button>
      <!-- 添加文档标签 -->
      <el-button type="primary" :disabled="!selectedTagIds.length || optionLoading" :loading="loading" @click="handleAddTags">添加</el-button>
    </template>
  </MkDialog>
</template>
