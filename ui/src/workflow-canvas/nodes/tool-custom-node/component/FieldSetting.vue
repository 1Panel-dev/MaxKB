<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ToolInputField } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'

defineOptions({ name: 'WorkflowToolInputFieldDialog' })

const { t } = useI18n({ useScope: 'global' })

const emit = defineEmits<{ submit: [field: ToolInputField, index?: number] }>()

const inputFieldTypes: ToolInputField['type'][] = ['string', 'int', 'float', 'dict', 'array']
const formRef = useTemplateRef<FormInstance>('formRef')
const visible = ref(false)
const editing = ref(false)
const currentIndex = ref<number>()
const inputFieldForm = ref<ToolInputField>({ desc: '', is_required: true, name: '', source: 'reference', type: 'string' })
const formRules = computed<FormRules<ToolInputField>>(() => ({
  name: [{ whitespace: true, required: true, message: t('tool.inputParams.name.requiredMessage'), trigger: 'blur' }],
}))

// 弹窗仅维护参数草稿，节点接收提交后关闭。
function open(field?: ToolInputField, index?: number) {
  if (field) {
    inputFieldForm.value = cloneDeep(field)
    editing.value = true
    currentIndex.value = index
  }
  visible.value = true
}

function handleSubmit() {
  formRef.value
    ?.validate()
    .then(() => emit('submit', cloneDeep(inputFieldForm.value), currentIndex.value))
    .catch(() => {})
}

function close() {
  visible.value = false
}

function resetData() {
  editing.value = false
  currentIndex.value = undefined
  inputFieldForm.value = { desc: '', is_required: true, name: '', source: 'reference', type: 'string' }
  formRef.value?.clearValidate()
}

defineExpose({ open, close })
</script>

<template>
  <!-- 添加输入参数 -->
  <el-button text type="primary" @click="open()">
    <MkIcon name="icon_add_outlined" />
  </el-button>
  <MkDialog v-model="visible" :title="editing ? t('common.parameters.edit') : t('common.parameters.add')" @closed="resetData">
    <el-form
      ref="formRef"
      :model="inputFieldForm"
      :rules="formRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('tool.inputParams.name.label')" prop="name">
        <el-input
          v-model="inputFieldForm.name"
          maxlength="64"
          :placeholder="t('tool.inputParams.name.placeholder')"
          @blur="inputFieldForm.name = inputFieldForm.name.trim()"
        />
      </el-form-item>
      <el-form-item :label="t('common.labels.dataType')">
        <el-select v-model="inputFieldForm.type" class="w-full">
          <el-option v-for="fieldType in inputFieldTypes" :key="fieldType" :label="fieldType" :value="fieldType" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('tool.inputParams.description.label')">
        <el-input
          v-model="inputFieldForm.desc"
          maxlength="128"
          :placeholder="t('tool.inputParams.description.placeholder')"
          show-word-limit
          @blur="inputFieldForm.desc = inputFieldForm.desc?.trim()"
        />
      </el-form-item>
      <el-form-item :label="t('common.labels.source')">
        <el-select v-model="inputFieldForm.source" class="w-full">
          <el-option :label="t('common.options.referenceParameter')" value="reference" />
          <el-option :label="t('common.options.custom')" value="custom" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('dynamicForm.fields.required.label')" @click.prevent>
        <el-switch v-model="inputFieldForm.is_required" />
      </el-form-item>
    </el-form>

    <template #footer>
      <!-- 取消编辑输入参数 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存输入参数 -->
      <el-button type="primary" @click="handleSubmit">{{ editing ? t('common.actions.save') : t('common.actions.add') }}</el-button>
    </template>
  </MkDialog>
</template>
