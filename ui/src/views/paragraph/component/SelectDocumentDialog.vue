<template>
  <el-dialog title="选择知识库/文档" v-model="dialogVisible" width="500">
    <el-form
      ref="formRef"
      :model="form"
      label-position="top"
      require-asterisk-position="right"
      :rules="rules"
      @submit.prevent
    >
      <el-form-item label="选择知识库" prop="dataset_id">
        <el-select
          v-model="form.dataset_id"
          filterable
          placeholder="请选择知识库"
          :loading="optionLoading"
          @change="changeDataset"
        >
          <el-option v-for="item in datasetList" :key="item.id" :label="item.name" :value="item.id">
            <span class="flex align-center">
              <AppAvatar
                v-if="!item.dataset_id && item.type === '1'"
                class="mr-12 avatar-purple"
                shape="square"
                :size="24"
              >
                <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
              </AppAvatar>
              <AppAvatar
                v-else-if="!item.dataset_id && item.type === '0'"
                class="mr-12 avatar-blue"
                shape="square"
                :size="24"
              >
                <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
              </AppAvatar>
              {{ item.name }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="保存至文档" prop="document_id">
        <el-select
          v-model="form.document_id"
          filterable
          placeholder="请选择文档"
          :loading="optionLoading"
        >
          <el-option
            v-for="item in documentList"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          >
            {{ item.name }}
          </el-option>
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submitForm(formRef)" :loading="loading"> 迁移 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import paragraphApi from '@/api/paragraph'
import useStore from '@/stores'

const { dataset, document } = useStore()

const route = useRoute()
const {
  params: { id, documentId }
} = route as any

const emit = defineEmits(['refresh'])
const formRef = ref()

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const form = ref<any>({
  dataset_id: '',
  document_id: ''
})

const rules = reactive<FormRules>({
  dataset_id: [{ required: true, message: '请选择知识库', trigger: 'change' }],
  document_id: [{ required: true, message: '请选择文档', trigger: 'change' }]
})

const datasetList = ref<any[]>([])
const documentList = ref<any[]>([])
const optionLoading = ref(false)
const paragraphList = ref<string[]>([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      dataset_id: '',
      document_id: ''
    }
    datasetList.value = []
    documentList.value = []
    paragraphList.value = []
    formRef.value?.clearValidate()
  }
})

function changeDataset(id: string) {
  form.value.document_id = ''
  getDocument(id)
}

function getDocument(id: string) {
  document.asyncGetAllDocument(id, loading).then((res: any) => {
    documentList.value = res.data?.filter((v: any) => v.id !== documentId)
  })
}

function getDataset() {
  dataset.asyncGetAllDataset(loading).then((res: any) => {
    datasetList.value = res.data
  })
}

const open = (list: any) => {
  paragraphList.value = list
  getDataset()
  formRef.value?.clearValidate()
  dialogVisible.value = true
}
const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      paragraphApi
        .putMigrateMulParagraph(
          id,
          documentId,
          form.value.dataset_id,
          form.value.document_id,
          paragraphList.value,
          loading
        )
        .then(() => {
          emit('refresh')
          dialogVisible.value = false
        })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
