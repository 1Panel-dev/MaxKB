<template>
  <el-form
    ref="FormRef"
    :model="form"
    :rules="rules"
    label-position="top"
    require-asterisk-position="right"
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
    <el-form-item label="Embedding模型" prop="embedding_mode_id">
      <el-select
        v-model="form.embedding_mode_id"
        class="w-full m-2"
        placeholder="请选择Embedding模型"
      >
        <el-option
          v-for="item in modelOptions"
          :key="item.id"
          :label="item.name"
          :value="item.id"
        ></el-option>
      </el-select>
    </el-form-item>
  </el-form>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import useStore from '@/stores'
import type { datasetData } from '@/api/type/dataset'

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
const modelOptions = ref([])

watch(
  () => props.data,
  (value) => {
    if (value && JSON.stringify(value) !== '{}') {
      form.value.name = value.name
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
  model.asyncGetModel({ model_type: 'EMBEDDING' }).then((res: any) => {
    modelOptions.value = res?.data
  })
}

onMounted(() => {
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
