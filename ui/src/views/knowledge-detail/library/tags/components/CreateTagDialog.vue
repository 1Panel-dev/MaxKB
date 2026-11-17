<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { KnowledgeTagPayload } from '@/api/types'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import type { FormInstance } from 'element-plus'
import { MsgError, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'CreateTagDialog' })
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ knowledgeId: string; api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['tags'] }>()
const emit = defineEmits<{ refresh: [] }>()

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const fixedTagKey = ref('')
const tagForm = reactive<{ tags: KnowledgeTagPayload[] }>({ tags: [{ key: '', value: '' }] })
const title = computed(() => (fixedTagKey.value ? t('knowledge.tags.actions.addValue') : t('knowledge.tags.actions.create')))
const defaultTag = computed(() => ({ key: fixedTagKey.value, value: '' }))

/* 新增值只回填并锁定标签名，与创建标签共用提交流程。 */
function open(key?: string) {
  if (key) {
    fixedTagKey.value = key
    tagForm.tags = [{ key, value: '' }]
  }
  visible.value = true
}

function handleRowsChange() {
  formRef.value?.clearValidate()
}

/* 两个创建入口统一提交标签数组。 */
function handleSubmit() {
  if (loading.value) return
  return formRef.value?.validate((valid) => {
    if (!valid || loading.value || !tagForm.tags.length) return
    const tags = tagForm.tags.map((tag) => ({ key: fixedTagKey.value || tag.key.trim(), value: tag.value.trim() }))
    const duplicateTag = tags.find((tag, index) =>
      tags.some((other, otherIndex) => otherIndex !== index && other.key === tag.key && other.value === tag.value),
    )
    if (duplicateTag) {
      MsgError(t('knowledge.tags.messages.duplicateTag'))
      return
    }

    loading.value = true
    return (
      props.api.postKnowledgeTags?.(props.knowledgeId, tags).then(() => {
        MsgSuccess(t('common.messages.createSuccess'))
        visible.value = false
        emit('refresh')
      }) ?? Promise.resolve()
    ).finally(() => {
      loading.value = false
    })
  })
}

function resetData() {
  tagForm.tags = [{ key: '', value: '' }]
  fixedTagKey.value = ''
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
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <MkFormList v-model="tagForm.tags" :add-text="t('common.actions.add')" :default-item="defaultTag" @update:model-value="handleRowsChange">
        <template #default="{ index, item: tag }">
          <el-form-item
            class="min-w-0 flex-1 small"
            :label="index === 0 ? t('knowledge.tags.key.label') : ''"
            :prop="`tags.${index}.key`"
            :rules="{ required: true, whitespace: true, message: t('knowledge.tags.key.requiredMessage'), trigger: 'blur' }"
          >
            <el-input v-model="tag.key" :disabled="!!fixedTagKey" :maxlength="64" :placeholder="t('knowledge.tags.key.placeholder')" />
          </el-form-item>
          <el-form-item
            class="min-w-0 flex-1 small"
            :label="index === 0 ? t('knowledge.tags.value.label') : ''"
            :prop="`tags.${index}.value`"
            :rules="{ required: true, whitespace: true, message: t('knowledge.tags.value.requiredMessage'), trigger: 'blur' }"
          >
            <el-input v-model="tag.value" :maxlength="128" :placeholder="t('knowledge.tags.value.placeholder')" />
          </el-form-item>
        </template>
      </MkFormList>
    </el-form>
    <template #footer>
      <!-- 取消创建标签 -->
      <el-button plain :disabled="loading" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 创建标签 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">{{ t('common.actions.create') }}</el-button>
    </template>
  </MkDialog>
</template>
