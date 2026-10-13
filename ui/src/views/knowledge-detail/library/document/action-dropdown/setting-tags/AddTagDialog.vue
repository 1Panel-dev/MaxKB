<script setup lang="ts">
import { computed, nextTick, reactive, ref, type ComponentPublicInstance } from 'vue'
import type { FormInstance, FormItemRule, SelectInstance } from 'element-plus'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import tagsApi from '@/api/admin/workspace/knowledge/tags'
import type { KnowledgeTagGroup } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import CreateTagDialog from '../../../tags/components/CreateTagDialog.vue'

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

const visible = ref(false)
const queryLoading = ref(false)
const optionsReady = ref(false)
const targetKnowledgeId = ref('')
const targetDocumentIds = ref<string[]>([])
const tagGroups = ref<KnowledgeTagGroup[]>([])
const tagForm = reactive<{ tags: TagSelection[] }>({ tags: [{ key: '', tagId: '' }] })
const formRef = ref<FormInstance>()
const keySelectRefs: Record<number, SelectInstance | null> = {}
const valueSelectRefs: Record<number, SelectInstance | null> = {}
const createTagRef = ref<InstanceType<typeof CreateTagDialog>>()
const createTagMounted = ref(false)
const busy = computed(() => loading.value || queryLoading.value || createTagMounted.value)
let added = false

// 候选项只保留接口返回的前 100 个标签组，搜索交给 el-select 的 filterable。
function loadTagOptions() {
  return tagsApi.getKnowledgeTags(targetKnowledgeId.value).then((groups) => {
    tagGroups.value = groups.slice(0, 100)
  })
}

function open(documentIds: string[]) {
  if (visible.value || busy.value || !documentIds.length) return
  targetKnowledgeId.value = props.knowledgeId
  targetDocumentIds.value = [...documentIds]
  visible.value = true
  queryLoading.value = true
  return loadTagOptions()
    .then(() => {
      optionsReady.value = true
    })
    .finally(() => {
      queryLoading.value = false
    })
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

function getTagValueRules(index: number): FormItemRule[] {
  return [
    { required: true, message: '请选择标签值', trigger: 'change' },
    {
      validator: (_rule, value: string, callback) => {
        const tag = tagForm.tags[index]
        if (value && (!tag || !getTagValues(tag.key).some(({ id }) => id === value))) {
          return callback(new Error('请重新选择标签值'))
        }
        callback()
      },
      trigger: 'change',
    },
  ]
}

function handleOpenCreateTag(index: number, field: 'key' | 'value') {
  if (busy.value || !optionsReady.value) return
  const key = tagForm.tags[index]?.key
  const selectRefs = field === 'key' ? keySelectRefs : valueSelectRefs
  selectRefs[index]?.blur()
  createTagMounted.value = true
  return nextTick(() => createTagRef.value?.open(field === 'value' && key ? key : undefined))
}

function handleTagsCreated() {
  // 创建成功后刷新当前弹窗的候选项。
  queryLoading.value = true
  optionsReady.value = false
  return loadTagOptions()
    .then(() => {
      optionsReady.value = true
    })
    .finally(() => {
      queryLoading.value = false
    })
}

function handleSubmit() {
  if (busy.value || !optionsReady.value) return
  return formRef.value?.validate((valid) => {
    if (!valid || busy.value || !tagForm.tags.length) return
    const tagIds = tagForm.tags.map(({ tagId }) => tagId)
    loading.value = true
    return props.api
      .postAddDocumentTags(targetKnowledgeId.value, targetDocumentIds.value, tagIds)
      .then(() => {
        MsgSuccess('添加成功')
        added = true
        visible.value = false
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function handleBeforeClose(done: () => void) {
  if (!busy.value) done()
}

function handleClosed() {
  // 等关闭动画结束再刷新，避免批量勾选清空时提前卸载弹窗。
  if (added) emit('refresh')
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="添加标签" :before-close="handleBeforeClose" @closed="handleClosed">
    <el-form ref="formRef" v-loading="queryLoading || loading" :model="tagForm" label-position="top" @submit.prevent>
      <MkFormList v-model="tagForm.tags" :default-item="{ key: '', tagId: '' }" @update:model-value="handleRowsChange">
        <template #default="{ index, item: tag }">
          <el-form-item
            class="min-w-0 flex-1"
            :label="index === 0 ? '标签' : ''"
            :prop="`tags.${index}.key`"
            :rules="{ required: true, message: '请选择标签', trigger: 'change' }"
          >
            <el-select
              :ref="(select: Element | ComponentPublicInstance | null) => (keySelectRefs[index] = select as SelectInstance | null)"
              v-model="tag.key"
              filterable
              clearable
              placeholder="请选择标签"
              @change="handleTagKeyChange(index)"
            >
              <el-option v-for="group in tagGroups" :key="group.key" :label="group.key" :value="group.key" />
              <template #footer>
                <!-- 创建新标签 -->
                <el-button type="primary" link :disabled="busy || !optionsReady" @click.stop="handleOpenCreateTag(index, 'key')">
                  <MkIcon name="icon_add_outlined" />
                  <span>创建标签</span>
                </el-button>
              </template>
            </el-select>
          </el-form-item>
          <el-form-item class="min-w-0 flex-1" :label="index === 0 ? '标签值' : ''" :prop="`tags.${index}.tagId`" :rules="getTagValueRules(index)">
            <el-select
              :ref="(select: Element | ComponentPublicInstance | null) => (valueSelectRefs[index] = select as SelectInstance | null)"
              v-model="tag.tagId"
              filterable
              clearable
              placeholder="请选择标签值"
            >
              <el-option v-for="value in getTagValues(tag.key)" :key="value.id" :label="value.value" :value="value.id" />
              <template #footer>
                <!-- 已选标签时新增值，未选标签时创建标签 -->
                <el-button type="primary" link :disabled="busy || !optionsReady" @click.stop="handleOpenCreateTag(index, 'value')">
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
      <el-button plain :disabled="busy" @click="visible = false">取消</el-button>
      <!-- 添加所选标签到目标文档 -->
      <el-button type="primary" :loading="loading" :disabled="queryLoading || createTagMounted || !optionsReady" @click="handleSubmit">
        添加
      </el-button>
    </template>
  </MkDialog>
  <CreateTagDialog
    v-if="createTagMounted"
    ref="createTagRef"
    :knowledge-id="targetKnowledgeId"
    @refresh="handleTagsCreated"
    @closed="createTagMounted = false"
  />
</template>
