<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { KnowledgeTagUpdatePayload } from '@/api/types'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import type { FormInstance, FormRules } from 'element-plus'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'EditTagDialog' })
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ knowledgeId: string; api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['tags'] }>()
const emit = defineEmits<{ refresh: [] }>()

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const editField = ref<'key' | 'value'>('key')
const tagForm = reactive<KnowledgeTagUpdatePayload>({ id: '', key: '', value: '' })
const title = computed(() => (editField.value === 'key' ? t('knowledge.tags.actions.edit') : t('knowledge.tags.actions.editValue')))
const formRules = computed<FormRules<KnowledgeTagUpdatePayload>>(() => ({
  key: [{ required: true, whitespace: true, message: t('knowledge.tags.key.requiredMessage'), trigger: 'blur' }],
  value: [{ required: true, whitespace: true, message: t('knowledge.tags.value.requiredMessage'), trigger: 'blur' }],
}))

/* 回填独立草稿，取消编辑不改变列表数据。 */
function open(tag: KnowledgeTagUpdatePayload, field: 'key' | 'value') {
  editField.value = field
  Object.assign(tagForm, { id: tag.id, key: tag.key, value: tag.value })
  visible.value = true
}

function handleSubmit() {
  if (loading.value) return
  return formRef.value?.validate((valid) => {
    if (!valid || loading.value) return
    const tag: KnowledgeTagUpdatePayload = { ...tagForm, [editField.value]: tagForm[editField.value].trim() }
    loading.value = true
    return (
      props.api.putKnowledgeTag?.(props.knowledgeId, tag.id, tag).then(() => {
        MsgSuccess(t('common.messages.saveSuccess'))
        visible.value = false
        emit('refresh')
      }) ?? Promise.resolve()
    ).finally(() => {
      loading.value = false
    })
  })
}

function resetData() {
  Object.assign(tagForm, { id: '', key: '', value: '' })
  editField.value = 'key'
  loading.value = false
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="title" @closed="resetData">
    <el-form
      ref="formRef"
      v-loading="loading"
      :model="tagForm"
      :rules="formRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <div class="flex gap-4">
        <el-form-item class="min-w-0 flex-1" :label="t('knowledge.tags.key.label')" prop="key">
          <el-input v-model="tagForm.key" :disabled="editField === 'value'" :maxlength="64" :placeholder="t('knowledge.tags.key.placeholder')" />
        </el-form-item>
        <el-form-item v-if="editField === 'value'" class="min-w-0 flex-1" :label="t('knowledge.tags.value.label')" prop="value">
          <el-input v-model="tagForm.value" :maxlength="128" :placeholder="t('knowledge.tags.value.placeholder')" />
        </el-form-item>
      </div>
    </el-form>
    <template #footer>
      <!-- 取消编辑标签 -->
      <el-button plain :disabled="loading" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存标签修改 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
