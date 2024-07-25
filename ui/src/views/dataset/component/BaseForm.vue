<template>
  <el-form
    ref="FormRef"
    :model="form"
    :rules="rules"
    label-position="top"
    require-asterisk-position="right"
    v-loading="loading"
  >
    <el-form-item label="知识库名称" prop="name">
      <el-input
        v-model="form.name"
        placeholder="请输入知识库名称"
        maxlength="64"
        show-word-limit
        @blur="form.name = form.name.trim()"
      />
    </el-form-item>
    <el-form-item label="知识库描述" prop="desc">
      <el-input
        v-model="form.desc"
        type="textarea"
        placeholder="描述知识库的内容，详尽的描述将帮助AI能深入理解该知识库的内容，能更准确的检索到内容，提高该知识库的命中率。"
        maxlength="256"
        show-word-limit
        :autosize="{ minRows: 3 }"
        @blur="form.desc = form.desc.trim()"
      />
    </el-form-item>
    <el-form-item label="向量模型" prop="embedding_mode_id">
      <el-select
        v-model="form.embedding_mode_id"
        placeholder="请选择向量模型"
        class="w-full"
        popper-class="select-model"
        :clearable="true"
      >
        <el-option-group
          v-for="(value, label) in modelOptions"
          :key="value"
          :label="relatedObject(providerOptions, label, 'provider')?.name"
        >
          <el-option
            v-for="item in value.filter((v: any) => v.status === 'SUCCESS')"
            :key="item.id"
            :label="item.name"
            :value="item.id"
            class="flex-between"
          >
            <div class="flex align-center">
              <span
                v-html="relatedObject(providerOptions, label, 'provider')?.icon"
                class="model-icon mr-8"
              ></span>
              <span>{{ item.name }}</span>
              <el-tag v-if="item.permission_type === 'PUBLIC'" type="info" class="info-tag ml-8">公用</el-tag>
            </div>
            <el-icon class="check-icon" v-if="item.id === form.embedding_mode_id"
              ><Check
            /></el-icon>
          </el-option>
          <!-- 不可用 -->
          <el-option
            v-for="item in value.filter((v: any) => v.status !== 'SUCCESS')"
            :key="item.id"
            :label="item.name"
            :value="item.id"
            class="flex-between"
            disabled
          >
            <div class="flex">
              <span
                v-html="relatedObject(providerOptions, label, 'provider')?.icon"
                class="model-icon mr-8"
              ></span>
              <span>{{ item.name }}</span>
              <span class="danger">{{
                $t('views.application.applicationForm.form.aiModel.unavailable')
              }}</span>
            </div>
            <el-icon class="check-icon" v-if="item.id === form.embedding_mode_id"
              ><Check
            /></el-icon>
          </el-option>
        </el-option-group>
      </el-select>
    </el-form-item>
  </el-form>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { groupBy } from 'lodash'
import useStore from '@/stores'
import type { datasetData } from '@/api/type/dataset'
import { relatedObject } from '@/utils/utils'
import type { Provider } from '@/api/type/model'

const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  }
})
const { model } = useStore()
const form = ref<datasetData>({
  name: '',
  desc: '',
  embedding_mode_id: ''
})

const rules = reactive({
  name: [{ required: true, message: '请输入知识库名称', trigger: 'blur' }],
  desc: [{ required: true, message: '请输入知识库描述', trigger: 'blur' }],
  embedding_mode_id: [{ required: true, message: '请输入Embedding模型', trigger: 'change' }]
})

const FormRef = ref()
const loading = ref(false)
const modelOptions = ref<any>([])
const providerOptions = ref<Array<Provider>>([])

watch(
  () => props.data,
  (value) => {
    if (value && JSON.stringify(value) !== '{}') {
      form.value.name = value.name
      form.value.desc = value.desc
      form.value.embedding_mode_id = value.embedding_mode_id
    }
  },
  {
    immediate: true
  }
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

function getModel() {
  loading.value = true
  model
    .asyncGetModel({ model_type: 'EMBEDDING' })
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function getProvider() {
  loading.value = true
  model
    .asyncGetProvider()
    .then((res: any) => {
      providerOptions.value = res?.data
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

onMounted(() => {
  getProvider()
  getModel()
})
onUnmounted(() => {
  form.value = {
    name: '',
    desc: '',
    embedding_mode_id: ''
  }
  FormRef.value?.clearValidate()
})

defineExpose({
  validate,
  form
})
</script>
<style scoped lang="scss"></style>
