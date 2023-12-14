<template>
  <el-dialog title="修改标注" v-model="dialogVisible" width="600">

    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submitForm(formRef)" :loading="loading"> 保存 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import logApi from '@/api/log'
import type { CascaderProps } from 'element-plus'
import useStore from '@/stores'

const { application, document } = useStore()

const props = defineProps({
  chartId: {
    type: String,
    default: ''
  }
})

const route = useRoute()
const {
  params: { id }
} = route as any


const formRef = ref()

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const form = ref<any>({
  chat_id: '',
  record_id: '',
  problem_text: '',
  title: '',
  content: '',
  document: []
})

const rules = reactive<FormRules>({
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }],
  document: [{ type: 'array', required: true, message: '请选择文档', trigger: 'change' }]
})

const datasetList = ref([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      chat_id: '',
      record_id: '',
      problem_text: '',
      title: '',
      content: '',
      document: []
    }
  }
})

const LoadDocument: CascaderProps = {
  lazy: true,
  value: 'id',
  label: 'name',
  leaf: 'dataset_id',
  lazyLoad(node, resolve: any) {
    const { level, data } = node
    if (data?.id) {
      getDocument(data?.id as string, resolve)
    } else {
      getDataset(resolve)
    }
  }
}

function getDocument(id: string, resolve: any) {
  document.asyncGetAllDocument(id, loading).then((res: any) => {
    datasetList.value = res.data
    resolve(datasetList.value)
  })
}

function getDataset(resolve: any) {
  application.asyncGetApplicationDataset(id, loading).then((res: any) => {
    datasetList.value = res.data
    resolve(datasetList.value)
  })
}

const open = (data: any) => {
  form.value.chat_id = data.chat
  form.value.record_id = data.id
  form.value.problem_text = data.problem_text
  form.value.content = data.answer_text
  dialogVisible.value = true
}
const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      const obj = {
        title: form.value.title,
        content: form.value.content
      }
      logApi
        .putChatRecordLog(
          id,
          form.value.chat_id,
          form.value.record_id,
          form.value.document[0],
          form.value.document[1],
          obj,
          loading
        )
        .then((res: any) => {
          dialogVisible.value = false
        })
    } else {
      console.log('error submit!', fields)
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
