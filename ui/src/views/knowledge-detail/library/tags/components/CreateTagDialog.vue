<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { FormInstance, FormItemRule } from 'element-plus'
import TagsApi from '@/api/admin/workspace/knowledge/tags'
import type { KnowledgeTagPayload } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'CreateTagDialog' })

const props = withDefaults(defineProps<{ knowledgeId: string; api?: typeof TagsApi }>(), {
  api: () => TagsApi,
})
const emit = defineEmits<{ refresh: [] }>()

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const fixedTagKey = ref('')
const tagForm = reactive<{ tags: KnowledgeTagPayload[] }>({ tags: [{ key: '', value: '' }] })
const title = computed(() => (fixedTagKey.value ? '添加标签值' : '创建标签'))
const defaultTag = computed(() => ({ key: fixedTagKey.value, value: '' }))

/* 新增值只回填并锁定标签名，与创建标签共用提交流程。 */
function open(key?: string) {
  if (key) {
    fixedTagKey.value = key
    tagForm.tags = [{ key, value: '' }]
  }
  visible.value = true
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

/* 两个创建入口统一提交标签数组。 */
function handleSubmit() {
  if (loading.value) return
  return formRef.value?.validate((valid) => {
    if (!valid || loading.value || !tagForm.tags.length) return
    const tags = tagForm.tags.map((tag) => ({ key: fixedTagKey.value || tag.key.trim(), value: tag.value.trim() }))

    loading.value = true
    return props.api
      .postKnowledgeTags(props.knowledgeId, tags)
      .then(() => {
        MsgSuccess('创建成功')
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
  tagForm.tags = [{ key: '', value: '' }]
  fixedTagKey.value = ''
  loading.value = false
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="title" :before-close="handleBeforeClose" @closed="resetData">
    <el-form ref="formRef" v-loading="loading" :model="tagForm" label-position="top" @submit.prevent>
      <MkFormList v-model="tagForm.tags" :default-item="defaultTag" @update:model-value="handleRowsChange">
        <template #default="{ index, item: tag }">
          <el-form-item
            class="min-w-0 flex-1"
            :label="index === 0 ? '标签' : ''"
            :prop="`tags.${index}.key`"
            :rules="{ required: true, whitespace: true, message: '请输入标签', trigger: 'blur' }"
          >
            <el-input v-model="tag.key" :disabled="!!fixedTagKey" :maxlength="64" placeholder="请输入标签" />
          </el-form-item>
          <el-form-item class="min-w-0 flex-1" :label="index === 0 ? '标签值' : ''" :prop="`tags.${index}.value`" :rules="getTagValueRules(index)">
            <el-input v-model="tag.value" :maxlength="128" placeholder="请输入标签值" />
          </el-form-item>
        </template>
      </MkFormList>
    </el-form>
    <template #footer>
      <!-- 取消创建标签 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 创建标签 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">创建</el-button>
    </template>
  </MkDialog>
</template>
