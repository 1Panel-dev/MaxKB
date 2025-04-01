<template>
  <el-dialog
    :title="$t('views.document.generateQuestion.title')"
    v-model="dialogVisible"
    width="650"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div class="content-height">
      <el-form
        ref="FormRef"
        :model="form"
        :rules="rules"
        label-position="top"
        require-asterisk-position="right"
      >
        <div class="update-info flex border-r-4 mb-16 p-8-12">
          <div class="mt-4">
            <AppIcon iconName="app-warning-colorful" style="font-size: 16px"></AppIcon>
          </div>
          <div class="ml-12 lighter">
            <p>{{ $t('views.document.generateQuestion.tip1', { data: '{data}' }) }}</p>
            <p>
              {{ $t('views.document.generateQuestion.tip2')+ '<question></question>' +
              $t('views.document.generateQuestion.tip3') }}
            </p>
            <p>{{ $t('views.document.generateQuestion.tip4') }}</p>
          </div>
        </div>
        <el-form-item
          :label="$t('views.application.applicationForm.form.aiModel.label')"
          prop="model_id"
        >
          <ModelSelect
            v-model="form.model_id"
            :placeholder="$t('views.application.applicationForm.form.aiModel.placeholder')"
            :options="modelOptions"
            showFooter
            :model-type="'LLM'"
          ></ModelSelect>
        </el-form-item>
        <el-form-item
          :label="$t('views.application.applicationForm.form.prompt.label')"
          prop="prompt"
        >
          <el-input
            v-model="form.prompt"
            :placeholder="$t('views.application.applicationForm.form.prompt.placeholder')"
            :rows="7"
            type="textarea"
          />
        </el-form-item>
        <el-form-item
          v-if="['document', 'dataset'].includes(apiType)"
          :label="$t('components.selectParagraph.title')"
          prop="state"
        >
          <el-radio-group v-model="state" class="radio-block">
            <el-radio value="error" size="large">{{
              $t('components.selectParagraph.error')
            }}</el-radio>
            <el-radio value="all" size="large">{{ $t('components.selectParagraph.all') }}</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submitHandle(FormRef)" :disabled="!model || loading">
          {{ $t('common.confirm') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import documentApi from '@/api/document'
import paragraphApi from '@/api/paragraph'
import datasetApi from '@/api/dataset'
import useStore from '@/stores'
import { groupBy } from 'lodash'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import type { FormInstance } from 'element-plus'

const route = useRoute()
const {
  params: { id, documentId } // id为datasetID
} = route as any

const { model, prompt, user } = useStore()

const emit = defineEmits(['refresh'])

const loading = ref<boolean>(false)

const dialogVisible = ref<boolean>(false)
const modelOptions = ref<any>(null)
const idList = ref<string[]>([])
const apiType = ref('') // 文档document或段落paragraph
const state = ref<'all' | 'error'>('error')
const stateMap = {
  all: ['0', '1', '2', '3', '4', '5', 'n'],
  error: ['0', '1', '3', '4', '5', 'n']
}
const FormRef = ref()
const datasetId = ref<string>()
const userId = user.userInfo?.id as string
const form = ref(prompt.get(userId))
const rules = reactive({
  model_id: [
    {
      required: true,
      message: t('views.application.applicationForm.form.aiModel.placeholder'),
      trigger: 'blur'
    }
  ],
  prompt: [
    {
      required: true,
      message: t('views.application.applicationForm.form.prompt.placeholder'),
      trigger: 'blur'
    }
  ]
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = prompt.get(userId)
    FormRef.value?.clearValidate()
  }
})

const open = (ids: string[], type: string, _datasetId?: string) => {
  datasetId.value = _datasetId
  getModel()
  idList.value = ids
  apiType.value = type
  dialogVisible.value = true
}

const submitHandle = async (formEl: FormInstance) => {
  if (!formEl) {
    return
  }
  await formEl.validate((valid, fields) => {
    if (valid) {
      // 保存提示词
      prompt.save(user.userInfo?.id as string, form.value)
      if (apiType.value === 'paragraph') {
        const data = {
          ...form.value,
          paragraph_id_list: idList.value
        }
        paragraphApi.batchGenerateRelated(id, documentId, data, loading).then(() => {
          MsgSuccess(t('views.document.generateQuestion.successMessage'))
          emit('refresh')
          dialogVisible.value = false
        })
      } else if (apiType.value === 'document') {
        const data = {
          ...form.value,
          document_id_list: idList.value,
          state_list: stateMap[state.value]
        }
        documentApi.batchGenerateRelated(id, data, loading).then(() => {
          MsgSuccess(t('views.document.generateQuestion.successMessage'))
          emit('refresh')
          dialogVisible.value = false
        })
      } else if (apiType.value === 'dataset') {
        const data = {
          ...form.value,
          state_list: stateMap[state.value]
        }
        datasetApi.generateRelated(id ? id : datasetId.value, data, loading).then(() => {
          MsgSuccess(t('views.document.generateQuestion.successMessage'))
          dialogVisible.value = false
        })
      }
    }
  })
}

function getModel() {
  loading.value = true
  datasetApi
    .getDatasetModel(id ? id : datasetId.value)
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
