<script setup lang="ts">
import type TagsApi from '@/api/admin/workspace/knowledge/tags'
import { nextTick, reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import { useKnowledgeLibraryContext } from '@/views/knowledge-detail/context'
import type { KnowledgeTagGroup } from '@/api/types'
import { MsgError, MsgSuccess } from '@/utils/message'
import CreateTagDialog from '@/views/knowledge-detail/library/tags/components/CreateTagDialog.vue'

type WorkspaceTagsApi = typeof TagsApi

defineOptions({ name: 'AddTagDialog' })
const props = defineProps<{
  knowledgeId: string
  api: typeof DocumentApi
}>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: []; closed: [] }>()

interface TagSelection {
  key: string
  tagId: string
}

const { resourceApi, resourceScope } = useKnowledgeLibraryContext()
const visible = ref(false)
const queryLoading = ref(false)
const targetKnowledgeId = ref('')
const targetDocumentIds = ref<string[]>([])
const tagGroups = ref<KnowledgeTagGroup[]>([])
const tagForm = reactive<{ tags: TagSelection[] }>({ tags: [{ key: '', tagId: '' }] })
const formRef = ref<FormInstance>()
const createTagRef = ref<InstanceType<typeof CreateTagDialog>>()
const createTagMounted = ref(false)

// 候选项只保留接口返回的前 100 个标签组，搜索交给 el-select 的 filterable。
function loadTagOptions() {
  const requestApi = resourceApi.tags
  if (resourceScope.value !== 'workspace' || !requestApi) return
  queryLoading.value = true
  return requestApi
    .getKnowledgeTags(targetKnowledgeId.value)
    .then((groups) => {
      tagGroups.value = groups.slice(0, 100)
    })
    .catch(() => {
      // 查询失败时清空候选，避免提交已失效的标签值。
      tagGroups.value = []
    })
    .finally(() => {
      queryLoading.value = false
    })
}

function open(documentIds: string[]) {
  if (resourceScope.value !== 'workspace' || !resourceApi.tags || visible.value || loading.value || !documentIds.length) return
  targetKnowledgeId.value = props.knowledgeId
  targetDocumentIds.value = [...documentIds]
  visible.value = true
  return loadTagOptions()
}

function getTagValues(key: string) {
  return tagGroups.value.find((group) => group.key === key)?.values ?? []
}

function handleTagKeyChange(index: number) {
  tagForm.tags[index]!.tagId = ''
  formRef.value?.clearValidate([`tags.${index}.key`, `tags.${index}.tagId`])
}

function handleRowsChange() {
  formRef.value?.clearValidate()
}

function handleOpenCreateTag(index: number, field: 'key' | 'value') {
  if (loading.value || createTagMounted.value) return
  const key = tagForm.tags[index]?.key
  createTagMounted.value = true
  return nextTick(() => createTagRef.value?.open(field === 'value' && key ? key : undefined))
}

// 添加成功后关闭并通知页面刷新。
function handleSubmit() {
  if (loading.value || createTagMounted.value) return
  return formRef.value?.validate((valid) => {
    if (!valid || loading.value || createTagMounted.value || !tagForm.tags.length) return
    const invalidTag = tagForm.tags.some((tag) => !getTagValues(tag.key).some(({ id }) => id === tag.tagId))
    if (invalidTag) {
      MsgError('标签值已存在')
      return
    }
    const tagIds = tagForm.tags.map(({ tagId }) => tagId)
    loading.value = true
    return props.api
      .postAddDocumentTags(targetKnowledgeId.value, targetDocumentIds.value, tagIds)
      .then(() => {
        MsgSuccess('添加成功')
        visible.value = false
        emit('refresh')
      })
      .finally(() => {
        loading.value = false
      })
  })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="添加标签" @closed="emit('closed')">
    <el-form ref="formRef" v-loading="loading" :model="tagForm" label-position="top" @submit.prevent>
      <MkFormList v-model="tagForm.tags" :default-item="{ key: '', tagId: '' }" @update:model-value="handleRowsChange">
        <template #default="{ index, item: tag }">
          <el-form-item
            class="min-w-0 flex-1"
            :label="index === 0 ? '标签' : ''"
            :prop="`tags.${index}.key`"
            :rules="{ required: true, message: '请选择标签', trigger: 'change' }"
          >
            <el-select v-model="tag.key" :loading="queryLoading" filterable clearable placeholder="请选择标签" @change="handleTagKeyChange(index)">
              <el-option v-for="group in tagGroups" :key="group.key" :label="group.key" :value="group.key" />
              <template #footer>
                <!-- 创建新标签 -->
                <el-button type="primary" link :disabled="queryLoading" @click.stop="handleOpenCreateTag(index, 'key')">
                  <MkIcon name="icon_add_outlined" />
                  <span>创建标签</span>
                </el-button>
              </template>
            </el-select>
          </el-form-item>
          <el-form-item
            class="min-w-0 flex-1"
            :label="index === 0 ? '标签值' : ''"
            :prop="`tags.${index}.tagId`"
            :rules="{ required: true, message: '请选择标签值', trigger: 'change' }"
          >
            <el-select v-model="tag.tagId" :loading="queryLoading" filterable clearable placeholder="请选择标签值">
              <el-option v-for="value in getTagValues(tag.key)" :key="value.id" :label="value.value" :value="value.id" />
              <template #footer>
                <!-- 已选标签时新增值，未选标签时创建标签 -->
                <el-button type="primary" link :disabled="queryLoading" @click.stop="handleOpenCreateTag(index, 'value')">
                  <MkIcon name="icon_add_outlined" />
                  <span>创建标签值</span>
                </el-button>
              </template>
            </el-select>
          </el-form-item>
        </template>
      </MkFormList>
    </el-form>
    <template #footer>
      <!-- 取消添加 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 添加所选标签到目标文档 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">添加</el-button>
    </template>
  </MkDialog>
  <CreateTagDialog
    v-if="createTagMounted && resourceScope === 'workspace'"
    ref="createTagRef"
    :knowledge-id="targetKnowledgeId"
    :api="resourceApi.tags as WorkspaceTagsApi"
    @refresh="loadTagOptions"
    @closed="createTagMounted = false"
  />
</template>
