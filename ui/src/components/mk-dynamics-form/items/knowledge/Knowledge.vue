<script setup lang="ts">
import { computed } from 'vue'
import type { KnowledgeItem } from '@/api/types'
import type { FormField } from '../../type'

defineOptions({ name: 'DynamicFormKnowledge', inheritAttrs: false })

type KnowledgeOption = Pick<KnowledgeItem, 'id' | 'name' | 'type'>

const props = withDefaults(defineProps<{ modelValue?: string[]; formField: FormField }>(), { modelValue: () => [] })
const emit = defineEmits<{
  'update:modelValue': [knowledgeIds: string[]]
  change: [formField: FormField]
}>()

// 可选知识库与选中值：仅展示配置内的 ID，用户选择时再回写表单。
const availableKnowledge = computed<KnowledgeOption[]>(() => props.formField.attrs?.knowledge_list || [])
const knowledgeById = computed(() => new Map(availableKnowledge.value.map((knowledge) => [knowledge.id, knowledge])))
const selectedKnowledgeIds = computed({
  get: () => props.modelValue.filter((knowledgeId) => knowledgeById.value.has(knowledgeId)),
  set: (knowledgeIds: string[]) => {
    emit('update:modelValue', knowledgeIds)
    emit('change', props.formField)
  },
})
</script>

<template>
  <div class="w-full">
    <el-select v-model="selectedKnowledgeIds" multiple v-bind="$attrs" class="w-full" placeholder="请选择知识库">
      <el-option v-for="knowledge in availableKnowledge" :key="knowledge.id" :label="knowledge.name" :value="knowledge.id">
        <div class="flex min-w-0 items-center gap-2">
          <KnowledgeIcon :type="knowledge.type" :size="20" class="shrink-0" />
          <span class="truncate" :title="knowledge.name">{{ knowledge.name }}</span>
        </div>
      </el-option>
      <template #label="{ label, value }">
        <span class="inline-flex max-w-full items-center gap-2">
          <KnowledgeIcon :type="knowledgeById.get(value)?.type" :size="14" class="shrink-0" style="--el-avatar-border-radius: 4px" />
          <span class="truncate" :title="label">{{ label }}</span>
        </span>
      </template>
    </el-select>
  </div>
</template>
