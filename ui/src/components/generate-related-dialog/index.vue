<template>
  <el-dialog
    title="生成问题"
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
            <p>提示词中的 {data} 为分段内容的占位符，执行时替换为分段内容发送给 AI 模型；</p>
            <p>
              AI
              模型根据分段内容生成相关问题，请将生成的问题放至&lt;question&gt;&lt;/question&gt;标签中，系统会自动关联标签中的问题；
            </p>
            <p>生成效果依赖于所选模型和提示词，用户可自行调整至最佳效果。</p>
          </div>
        </div>
        <el-form-item label="AI 模型" prop="model_id">
          <el-select
            v-model="form.model_id"
            :placeholder="$t('views.application.applicationForm.form.aiModel.placeholder')"
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
                  <el-tag v-if="item.permission_type === 'PUBLIC'" type="info" class="info-tag ml-8"
                    >公用
                  </el-tag>
                </div>
                <el-icon class="check-icon" v-if="item.id === form.model_id">
                  <Check />
                </el-icon>
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
                <el-icon class="check-icon" v-if="item.id === form.model_id">
                  <Check />
                </el-icon>
              </el-option>
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="提示词" prop="prompt">
          <el-input v-model="form.prompt" placeholder="请输入提示词" :rows="7" type="textarea" />
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submitHandle(FormRef)" :disabled="!model || loading">
          确定
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
import { relatedObject } from '@/utils/utils'
import type { Provider } from '@/api/type/model'
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
const providerOptions = ref<Array<Provider>>([])
const idList = ref<string[]>([])
const apiType = ref('') // 文档document或段落paragraph

const FormRef = ref()
const userId = user.userInfo?.id as string
const form = ref(prompt.get(userId))

const rules = reactive({
  model_id: [{ required: true, message: '请选择AI 模型', trigger: 'blur' }],
  prompt: [{ required: true, message: '请输入提示词', trigger: 'blur' }]
})

const open = (ids: string[], type: string) => {
  getProvider()
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
        const data = { ...form.value, paragraph_id_list: idList.value }
        paragraphApi.batchGenerateRelated(id, documentId, data, loading).then(() => {
          MsgSuccess('生成问题成功')
          emit('refresh')
          dialogVisible.value = false
        })
      } else if (apiType.value === 'document') {
        const data = { ...form.value, document_id_list: idList.value }
        documentApi.batchGenerateRelated(id, data, loading).then(() => {
          MsgSuccess('生成问题成功')
          emit('refresh')
          dialogVisible.value = false
        })
      }
    }
  })
}

function getModel() {
  loading.value = true
  datasetApi
    .getDatasetModel(id)
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

defineExpose({ open })
</script>
<style lang="scss" scope>
.update-info {
  background: #d6e2ff;
  line-height: 25px;
}
</style>
