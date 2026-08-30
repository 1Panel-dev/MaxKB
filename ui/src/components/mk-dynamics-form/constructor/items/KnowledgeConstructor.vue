<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, reactive } from 'vue'
import Knowledge from '../../items/knowledge/Knowledge.vue'
import type { FormField } from '../../type'

const props = defineProps<{ modelValue: DynamicFormValue }>()

const emit = defineEmits(['update:modelValue'])

const collapseData = reactive({ optional_knowledge: true })
const formValue = computed({
  set: (item: DynamicFormValue) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue || { knowledge_list: [], default_value: [] }
  },
})

const formField = computed<FormField>(() => {
  return { attrs: { knowledge_list: formValue.value.knowledge_list } } as DynamicFormValue
})

const getData = () => {
  const knowledgeItemList = (formValue.value.knowledge_list || []).map((k: DynamicFormValue) => {
    return { id: k.id, name: k.name, type: k.type, embedding_model_id: k.embedding_model_id }
  })

  return { input_type: 'Knowledge', default_value: formValue.value.default_value || [], attrs: { knowledge_list: knowledgeItemList } }
}

const render = (formData: DynamicFormValue) => {
  formValue.value.default_value = formData.default_value || []
  formValue.value.knowledge_list = formData.attrs?.knowledge_list || []
}

defineExpose({ getData, render })

function removeKnowledge(id: string) {
  formValue.value.knowledge_list = formValue.value.knowledge_list.filter((k: DynamicFormValue) => k.id !== id)
  if (formValue.value.default_value) {
    formValue.value.default_value = formValue.value.default_value.filter((k_id: string) => k_id !== id)
  }
}
</script>

<template>
  <el-form-item prop="knowledge_list" :rules="[{ message: '请选择可选知识库', type: 'array', min: 1 }]">
    <template #label>
      <div class="flex-between mb-12 cursor" @click="collapseData.optional_knowledge = !collapseData.optional_knowledge">
        <div class="flex align-center">
          <el-icon class="mr-8 arrow-icon" :class="collapseData.optional_knowledge ? 'rotate-90' : ''">
            <CaretRight />
          </el-icon>
          <span class="lighter"
            >可选知识库
            <span class="color-danger">*</span>
          </span>
          <span class="ml-4" v-if="formValue.knowledge_list?.length">({{ formValue.knowledge_list.length }})</span>
        </div>
      </div>
    </template>
    <div class="w-full" v-if="collapseData.optional_knowledge">
      <div v-if="formValue.knowledge_list?.length > 0">
        <template v-for="(item, index) in formValue.knowledge_list" :key="index">
          <div class="flex-between border border-r-6 white-bg mb-8" style="padding: 3px 12px">
            <div class="flex align-center" style="width: 80%">
              <KnowledgeIcon :type="item.type" class="mr-8" :size="20" style="--el-avatar-border-radius: 6px" />

              <span class="ellipsis cursor" :title="item.name"> {{ item.name }}</span>
            </div>
            <el-button text @click="removeKnowledge(item.id)">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </template>
      </div>
      <el-text type="info" v-else> 请选择可选知识库 </el-text>
    </div>
  </el-form-item>
  <el-form-item
    label="默认知识库"
    prop="default_value"
    :required="formValue.required"
    :rules="formValue.required ? [{ message: '请选择知识库', type: 'array', min: 1 }] : []"
    v-if="formValue.knowledge_list && formValue.knowledge_list.length > 0"
  >
    <div class="w-full" v-if="formValue.knowledge_list?.length > 0">
      <Knowledge v-model="formValue.default_value" :form-field="formField" />
    </div>
  </el-form-item>
</template>
