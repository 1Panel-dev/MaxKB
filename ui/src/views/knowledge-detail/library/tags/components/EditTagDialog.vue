<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type TagsApi from '@/api/admin/workspace/knowledge/tags'
import type { KnowledgeTagUpdatePayload } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'EditTagDialog' })

const props = defineProps<{ knowledgeId: string; api: typeof TagsApi }>()
const emit = defineEmits<{ refresh: [] }>()

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const editField = ref<'key' | 'value'>('key')
const tagForm = reactive<KnowledgeTagUpdatePayload>({ id: '', key: '', value: '' })
const title = computed(() => (editField.value === 'key' ? '编辑标签' : '编辑标签值'))
const formRules: FormRules<KnowledgeTagUpdatePayload> = {
  key: [{ required: true, whitespace: true, message: '请输入标签', trigger: 'blur' }],
  value: [{ required: true, whitespace: true, message: '请输入标签值', trigger: 'blur' }],
}

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
    return props.api
      .putKnowledgeTag(props.knowledgeId, tag.id, tag)
      .then(() => {
        MsgSuccess('保存成功')
        visible.value = false
        emit('refresh')
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function handleBeforeClose(done: () => void) {
  if (!loading.value) done()
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
  <MkDialog v-model="visible" :title="title" :before-close="handleBeforeClose" @closed="resetData">
    <el-form ref="formRef" v-loading="loading" :model="tagForm" :rules="formRules" label-position="top" @submit.prevent>
      <div class="flex gap-4">
        <el-form-item class="min-w-0 flex-1" label="标签" prop="key">
          <el-input v-model="tagForm.key" :disabled="editField === 'value'" :maxlength="64" placeholder="请输入标签" />
        </el-form-item>
        <el-form-item v-if="editField === 'value'" class="min-w-0 flex-1" label="标签值" prop="value">
          <el-input v-model="tagForm.value" :maxlength="128" placeholder="请输入标签值" />
        </el-form-item>
      </div>
    </el-form>
    <template #footer>
      <!-- 取消编辑标签 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 保存标签修改 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
    </template>
  </MkDialog>
</template>
