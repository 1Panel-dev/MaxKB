<script setup lang="ts">
import { computed, nextTick, useTemplateRef } from 'vue'
import type { FormItemInstance } from 'element-plus'
import type { KnowledgeItem } from '@/api/types'
import SelectKnowledgeDialog from '@/components/business/select-knowledge-dialog/index.vue'
import Knowledge from '../../items/knowledge/Knowledge.vue'
import type { FormField } from '../../type'

type KnowledgeOption = Pick<KnowledgeItem, 'id'> & Partial<Pick<KnowledgeItem, 'name' | 'type' | 'embedding_model_id'>>
interface KnowledgeConstructorValue {
  field?: string
  required?: boolean
  knowledge_list?: KnowledgeOption[]
  default_value?: string[]
}

const props = defineProps<{ modelValue: KnowledgeConstructorValue }>()
const emit = defineEmits<{ 'update:modelValue': [value: KnowledgeConstructorValue] }>()

// 配置回填与序列化：保留知识库快照及默认 ID 的字段协议。
const formValue = computed({
  get: () => props.modelValue || { knowledge_list: [], default_value: [] },
  set: (value: KnowledgeConstructorValue) => emit('update:modelValue', value),
})
const availableKnowledge = computed(() => formValue.value.knowledge_list || [])
const formField = computed<FormField>(() => ({
  field: formValue.value.field || '',
  input_type: 'Knowledge',
  attrs: { knowledge_list: availableKnowledge.value },
}))

function getData(): Partial<FormField> {
  return {
    input_type: 'Knowledge',
    default_value: formValue.value.default_value || [],
    attrs: {
      knowledge_list: availableKnowledge.value.map(({ id, name, type, embedding_model_id }) => ({ id, name, type, embedding_model_id })),
    },
  }
}

function render(formData: FormField) {
  formValue.value.default_value = formData.default_value || []
  formValue.value.knowledge_list = formData.attrs?.knowledge_list || []
}

defineExpose({ getData, render })

// 自定义选择列表不会自动触发表单校验，用户修改后等待字段更新再校验。
const knowledgeFormItemRef = useTemplateRef<FormItemInstance>('knowledgeFormItemRef')
function validateKnowledgeSelection() {
  void nextTick(() => {
    void knowledgeFormItemRef.value?.validate('change').catch(() => {
      // 校验失败由表单项展示，避免产生未处理的 Promise 拒绝。
    })
  })
}

// 添加知识库：由公共弹窗管理查询和临时选择，确认后同步可选项及默认值。
const knowledgeDialogRef = useTemplateRef<InstanceType<typeof SelectKnowledgeDialog>>('knowledgeDialogRef')

function openAddKnowledgeDialog() {
  knowledgeDialogRef.value?.open(availableKnowledge.value)
}

function handleKnowledgeSelect(knowledge: (Partial<KnowledgeItem> & { id: string })[]) {
  const selectedIds = new Set(knowledge.map(({ id }) => id))
  formValue.value.knowledge_list = knowledge.map(({ id, name, type, embedding_model_id }) => ({ id, name, type, embedding_model_id }))
  formValue.value.default_value = (formValue.value.default_value || []).filter((id) => selectedIds.has(id))
  validateKnowledgeSelection()
}

// 移除可选知识库时同步清理默认值，保留其他关联。
function removeKnowledge(knowledgeId: string) {
  formValue.value.knowledge_list = availableKnowledge.value.filter(({ id }) => id !== knowledgeId)
  formValue.value.default_value = (formValue.value.default_value || []).filter((id) => id !== knowledgeId)
  validateKnowledgeSelection()
}
</script>

<template>
  <el-form-item ref="knowledgeFormItemRef" prop="knowledge_list" :rules="[{ required: true, message: '请选择可选知识库', type: 'array', min: 1 }]">
    <MkCollapse class="w-full" trigger-class="pt-0 pb-2">
      <template #label>
        <div class="flex-between w-full">
          <div class="flex items-center">
            <span class="mk-required">可选知识库</span>
            <span v-if="availableKnowledge.length">({{ availableKnowledge.length }})</span>
          </div>

          <el-button type="primary" text @click.stop="openAddKnowledgeDialog">
            <MkIcon name="icon_add_outlined" />
          </el-button>
        </div>
      </template>
      <div v-if="availableKnowledge.length" class="space-y-2">
        <template v-for="knowledge in availableKnowledge" :key="knowledge.id">
          <el-card class="small" shadow="never">
            <div class="flex-between">
              <span class="flex min-w-0 items-center gap-2">
                <KnowledgeIcon :type="knowledge.type" :size="20" class="shrink-0" />
                <span class="min-w-0 flex-1 truncate" :title="knowledge.name">{{ knowledge.name }}</span>
              </span>
              <el-button text @click="removeKnowledge(knowledge.id)"><MkIcon name="icon_close_outlined" /></el-button>
            </div>
          </el-card>
        </template>
      </div>
      <el-text v-else type="info">请选择可选知识库</el-text>
    </MkCollapse>
  </el-form-item>
  <el-form-item
    v-if="availableKnowledge.length"
    label="默认知识库"
    prop="default_value"
    :required="formValue.required"
    :rules="formValue.required ? [{ message: '请选择知识库', type: 'array', min: 1 }] : []"
  >
    <Knowledge v-model="formValue.default_value" :form-field="formField" />
  </el-form-item>

  <SelectKnowledgeDialog ref="knowledgeDialogRef" @submit="handleKnowledgeSelect" />
</template>
