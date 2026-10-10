<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormItemRule } from 'element-plus'
import type TagsApi from '@/api/admin/workspace/knowledge/tags'
import type { KnowledgeTagGroup, KnowledgeTagPayload, KnowledgeTagUpdatePayload } from '@/api/types'
import { MsgSuccess, MsgWarning } from '@/utils/message'

defineOptions({ name: 'TagFormDialog' })

const props = defineProps<{ knowledgeId: string; api: typeof TagsApi }>()
const emit = defineEmits<{ refresh: [] }>()

type TagFormOptions =
  | { mode: 'create' }
  | { mode: 'add-value'; key: string }
  | { mode: 'edit-group'; group: KnowledgeTagGroup }
  | { mode: 'edit-value'; tag: KnowledgeTagUpdatePayload }

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const mode = ref<TagFormOptions['mode']>('create')
const fixedTagKey = ref('')
const editTagId = ref('')
const originalTags = ref<KnowledgeTagUpdatePayload[]>([])
const tagForm = reactive<{ tags: (KnowledgeTagPayload & { id?: string })[] }>({ tags: [] })
const normalizedTags = computed(() => tagForm.tags.map((tag) => ({ ...tag, key: tag.key.trim(), value: tag.value.trim() })))
const isEditing = computed(() => mode.value === 'edit-group' || mode.value === 'edit-value')
const title = computed(() => (mode.value === 'edit-group' ? '编辑标签' : mode.value === 'edit-value' ? '编辑标签值' : '创建标签'))
const defaultTag = computed(() => ({ key: mode.value === 'edit-group' ? (tagForm.tags[0]?.key ?? '') : fixedTagKey.value, value: '' }))

// 整组编辑或编辑中增删行时，不能使用单值编辑接口。
const requiresMultiEdit = computed(
  () => mode.value === 'edit-group' || (mode.value === 'edit-value' && (tagForm.tags.length !== 1 || tagForm.tags[0]?.id !== editTagId.value)),
)

/* 回填表单：供标签管理和文档入口共同调用。 */
function open(options: TagFormOptions = { mode: 'create' }) {
  mode.value = options.mode
  if (options.mode === 'create') {
    tagForm.tags = [{ key: '', value: '' }]
  } else if (options.mode === 'add-value') {
    fixedTagKey.value = options.key
    tagForm.tags = [{ key: options.key, value: '' }]
  } else if (options.mode === 'edit-group') {
    originalTags.value = options.group.values.map(({ id, value }) => ({ id, key: options.group.key, value }))
    tagForm.tags = cloneDeep(originalTags.value)
  } else {
    fixedTagKey.value = options.tag.key
    editTagId.value = options.tag.id
    originalTags.value = [cloneDeep(options.tag)]
    tagForm.tags = cloneDeep(originalTags.value)
  }
  visible.value = true
}

function handleTagKeyChange(key: string) {
  if (mode.value === 'edit-group') {
    tagForm.tags.forEach((tag) => (tag.key = key))
  }
}

function getTagValueRules(index: number): FormItemRule[] {
  return [
    { required: true, whitespace: true, message: '请输入标签值', trigger: 'blur' },
    {
      validator: (_rule, _value, callback) => {
        const tag = tagForm.tags[index]
        const duplicate =
          tag &&
          tagForm.tags.some(
            (other, otherIndex) => otherIndex !== index && other.key.trim() === tag.key.trim() && other.value.trim() === tag.value.trim(),
          )
        callback(duplicate ? new Error('相同标签下的标签值不能重复') : undefined)
      },
      trigger: 'blur',
    },
  ]
}

function handleRowsChange() {
  formRef.value?.clearValidate()
}

function requestMultiEditTags(): Promise<unknown> | undefined {
  // TODO：接入 V3 整组／多行编辑请求，按协议映射 props.knowledgeId、originalTags.value（原数据）、normalizedTags.value（新数据）。
  // 返回真实请求 Promise；成功关闭和刷新已处理，失败应 reject。
  return undefined
}

/* 各创建、编辑分支共用提交状态和成功处理。 */
function handleSubmit() {
  if (loading.value) return
  formRef.value?.validate((valid) => {
    if (!valid || loading.value) return
    const tags = normalizedTags.value
    const tag = tags[0]
    if (!tag) return

    let request: Promise<unknown> | undefined
    if (requiresMultiEdit.value) {
      request = requestMultiEditTags()
    } else if (isEditing.value) {
      request = props.api.putKnowledgeTag(props.knowledgeId, editTagId.value, { ...tag, id: editTagId.value })
    } else {
      request = props.api.postKnowledgeTags(props.knowledgeId, tags)
    }
    if (!request) {
      MsgWarning('整组／多行编辑接口尚未接入，当前修改尚未保存')
      return
    }

    loading.value = true
    return request
      .then(() => {
        MsgSuccess(isEditing.value ? '保存成功' : '创建成功')
        visible.value = false
        emit('refresh')
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function resetData() {
  tagForm.tags = []
  mode.value = 'create'
  fixedTagKey.value = ''
  editTagId.value = ''
  originalTags.value = []
  loading.value = false
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="title" :show-close="!loading" @closed="resetData">
    <el-form ref="formRef" v-loading="loading" :model="tagForm" label-position="top" @submit.prevent>
      <MkFormList v-model="tagForm.tags" :default-item="defaultTag" @update:model-value="handleRowsChange">
        <template #default="{ index, item: tag }">
          <el-form-item
            class="min-w-0 flex-1"
            :label="index === 0 ? '标签' : ''"
            :prop="`tags.${index}.key`"
            :rules="{ required: true, whitespace: true, message: '请输入标签', trigger: 'blur' }"
          >
            <el-input
              v-model="tag.key"
              :disabled="mode === 'add-value' || mode === 'edit-value'"
              :maxlength="64"
              placeholder="请输入标签"
              @input="handleTagKeyChange"
            />
          </el-form-item>
          <el-form-item class="min-w-0 flex-1" :label="index === 0 ? '标签值' : ''" :prop="`tags.${index}.value`" :rules="getTagValueRules(index)">
            <el-input v-model="tag.value" :maxlength="128" placeholder="请输入标签值" />
          </el-form-item>
        </template>
      </MkFormList>
    </el-form>
    <template #footer>
      <!-- 取消标签编辑 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 创建或保存标签 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">{{ isEditing ? '保存' : '创建' }}</el-button>
    </template>
  </MkDialog>
</template>
