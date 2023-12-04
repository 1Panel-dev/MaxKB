<template>
  <h4 class="title-decoration-1 mb-16">基本信息</h4>
  <el-form
    ref="FormRef"
    :model="form"
    :rules="rules"
    label-position="top"
    require-asterisk-position="right"
  >
    <el-form-item label="数据集名称" prop="name">
      <el-input
        v-model.trim="form.name"
        placeholder="请输入数据集名称"
        maxlength="64"
        show-word-limit
      />
    </el-form-item>
    <el-form-item label="数据集描述" prop="desc">
      <el-input
        v-model.trim="form.desc"
        type="textarea"
        placeholder="描述数据集的内容，详尽的描述将帮助AI能深入理解该数据集的内容，能更准确的检索到内容，提高该数据集的命中率。"
        maxlength="500"
        show-word-limit
        :autosize="{ minRows: 3 }"
      />
    </el-form-item>
    <el-form-item v-loading="loading">
      <el-row justify="space-between" style="width: 100%">
        <el-col :span="11" v-for="(item, index) in application_list" :key="index" class="mb-16">
          <CardCheckbox value-field="id" :data="item" v-model="form.application_id_list">
            <template #icon>
              <AppAvatar
                v-if="item.name"
                :name="item.name"
                pinyinColor
                class="mr-12"
                shape="square"
                :size="32"
              />
            </template>
            {{ item.name }}
          </CardCheckbox>
        </el-col>
      </el-row>
    </el-form-item>
  </el-form>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import useStore from '@/stores'
import DatasetApi from '@/api/dataset'
import CardCheckbox from '@/components/card-checkbox/index.vue'
import type { ApplicationFormType } from '@/api/type/application'
const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  }
})
const loading = ref<boolean>(false)
const { dataset } = useStore()
const baseInfo = computed(() => dataset.baseInfo)
const application_list = ref<Array<ApplicationFormType>>([])
const form = ref<any>({
  name: '',
  desc: '',
  application_id_list: []
})

const rules = reactive({
  name: [{ required: true, message: '请输入数据集名称', trigger: 'blur' }],
  desc: [{ required: true, message: '请输入数据集描述', trigger: 'blur' }]
})
const FormRef = ref()

watch(
  () => props.data,
  (value) => {
    if (value && JSON.stringify(value) !== '{}') {
      form.value.name = value.name
      form.value.desc = value.desc
      form.value.application_id_list = value.application_id_list
      DatasetApi.listUsableApplication(value.id, loading).then((ok) => {
        application_list.value = ok.data
      })
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

onMounted(() => {
  if (baseInfo.value) {
    form.value = baseInfo.value
  }
})
onUnmounted(() => {
  form.value = {
    name: '',
    desc: ''
  }
})
defineExpose({
  validate,
  form
})
</script>
<style scoped lang="scss"></style>
