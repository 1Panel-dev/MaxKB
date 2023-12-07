<template>
  <el-dialog title="修改内容" v-model="dialogVisible" width="600">
    <el-form
      ref="formRef"
      :model="form"
      label-position="top"
      require-asterisk-position="right"
      :rules="rules"
      @submit.prevent
    >
      <el-form-item label="关联问题">
        <span>{{ form.problem_text }}</span>
      </el-form-item>
      <el-form-item label="内容" prop="content">
        <el-input
          v-model="form.content"
          placeholder="请输入内容"
          maxlength="1024"
          show-word-limit
          :rows="8"
          type="textarea"
        >
        </el-input>
      </el-form-item>
      <el-form-item label="标题">
        <el-input v-model="form.title" placeholder="请给当前内容设置一个标题，以便管理查看">
        </el-input>
      </el-form-item>
      <el-form-item label="保存至文档" prop="document">
        <el-cascader v-model="form.document" :props="LoadDocument" placeholder="请选择文档">
          <template #default="{ node, data }">
            <span class="flex align-center">
              <AppAvatar v-if="!node.isLeaf" class="mr-12" shape="square" :size="24">
                <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
              </AppAvatar>
              {{ data.name }}
            </span>
          </template>
        </el-cascader>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submitForm(formRef)"> 保存 </el-button>
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

const emit = defineEmits(['updateContent'])

const formRef = ref()

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const form = ref<any>({
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
          props.chartId,
          form.value.record_id,
          form.value.document[0],
          form.value.document[1],
          obj,
          loading
        )
        .then((res: any) => {
          emit('updateContent', res.data)
          loading.value = false
        })
    } else {
      console.log('error submit!', fields)
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
