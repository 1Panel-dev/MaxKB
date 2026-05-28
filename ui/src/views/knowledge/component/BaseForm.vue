<template>
  <el-form
    ref="FormRef"
    :model="form"
    :rules="rules"
    label-position="top"
    require-asterisk-position="right"
    v-loading="loading"
  >
    <el-form-item :label="$t('views.knowledge.form.knowledgeName.label')" prop="name">
      <el-input
        v-model="form.name"
        :placeholder="$t('views.knowledge.form.knowledgeName.placeholder')"
        maxlength="64"
        show-word-limit
        @blur="form.name = form.name.trim()"
      />
    </el-form-item>
    <el-form-item :label="$t('views.knowledge.form.knowledgeDescription.label')" prop="desc">
      <el-input
        v-model="form.desc"
        type="textarea"
        :placeholder="$t('views.knowledge.form.knowledgeDescription.placeholder')"
        maxlength="256"
        show-word-limit
        :autosize="{ minRows: 3 }"
        @blur="form.desc = form.desc.trim()"
      />
    </el-form-item>
    <el-form-item
      :label="$t('views.knowledge.form.EmbeddingModel.label')"
      prop="embedding_model_id"
    >
      <ModelSelect
        v-model="form.embedding_model_id"
        :placeholder="$t('views.knowledge.form.EmbeddingModel.placeholder')"
        :options="modelOptions"
        @submit-model="getSelectModel"
        :model-type="'EMBEDDING'"
        showFooter
      ></ModelSelect>
    </el-form-item>
    <el-form-item :label="$t('views.knowledge.form.vectorStoreType.label')" prop="vector_store_type">
      <el-radio-group v-model="form.vector_store_type">
        <el-radio label="pg_vector">
          <span>PgVector (PostgreSQL)</span>
          <el-tag size="small" type="info" style="margin-left: 4px">默认</el-tag>
        </el-radio>
        <el-radio label="qdrant">
          <span>Qdrant</span>
          <el-tag size="small" type="success" style="margin-left: 4px">高性能</el-tag>
        </el-radio>
      </el-radio-group>
    </el-form-item>
  </el-form>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { groupBy } from 'lodash'
import type { knowledgeData } from '@/api/type/knowledge'
import { t } from '@/locales'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
const props = defineProps<{
  data?: {
    type: object
    default: () => null
  }
  apiType: 'systemShare' | 'workspace' | 'systemManage'
}>()
const form = ref<knowledgeData>({
  name: '',
  desc: '',
  embedding_model_id: '',
  vector_store_type: 'pg_vector',
})
const workspace_id = ref('')

const rules = reactive({
  name: [
    {
      required: true,
      message: t('views.knowledge.form.knowledgeName.requiredMessage'),
      trigger: 'blur',
    },
  ],
  desc: [
    {
      required: true,
      message: t('views.knowledge.form.knowledgeDescription.requiredMessage'),
      trigger: 'blur',
    },
  ],
  embedding_model_id: [
    {
      required: true,
      message: t('views.knowledge.form.EmbeddingModel.requiredMessage'),
      trigger: 'change',
    },
  ],
})

const FormRef = ref()
const loading = ref(false)
const modelOptions = ref<any>([])

watch(
  () => props.data,
  (value: any) => {
    if (value && JSON.stringify(value) !== '{}') {
      form.value.name = value.name
      form.value.desc = value.desc
      form.value.embedding_model_id = value.embedding_model_id
      form.value.vector_store_type = value.vector_store_type || 'pg_vector'
      workspace_id.value = value.workspace_id || ''
      // 重新刷新模型列表
      getSelectModel()
    }
  },
  {
    immediate: true,
  },
)

/*
  表单校验
*/
function validate() {
  if (!FormRef.value) return
  return FormRef.value.validate((valid: any) => {
    return valid
  })
}

function getSelectModel() {
  loading.value = true
  const obj =
    props.apiType === 'systemManage'
      ? {
          model_type: 'EMBEDDING',
          workspace_id: workspace_id.value,
        }
      : {
          model_type: 'EMBEDDING',
        }
  loadSharedApi({ type: 'model', systemType: props.apiType })
    .getSelectModelList(obj)
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

onMounted(() => {
  if (props.apiType !== 'systemManage') {
    getSelectModel()
  }
})

onUnmounted(() => {
  form.value = {
    name: '',
    desc: '',
    embedding_model_id: '',
  }
  FormRef.value?.clearValidate()
})

defineExpose({
  validate,
  form,
})
</script>
<style scoped lang="scss"></style>
