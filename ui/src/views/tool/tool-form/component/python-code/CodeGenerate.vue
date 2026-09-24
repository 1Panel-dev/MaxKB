<script setup lang="ts">
import { computed, provide, ref } from 'vue'
import { cloneDeep, groupBy } from 'lodash'
import PythonCodeEditor from '@/components/codemirror-editor/python.vue'
import { MsgSuccess } from '@/utils/message'
import ToolApi from '@/api/admin/workspace/tool/tool'
import SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import ModelApi from '@/api/admin/workspace/model'
import SystemResourceModelApi from '@/api/admin/system/resource-management/model'
import SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import ModelProviderApi from '@/api/admin/model-provider'
import SelectModel from '@/components/business/select-model/index.vue'
import GenerateContent from '@/components/business/generate-content/index.vue'
import { MODEL_STATUS } from '@/api/enums'
import type {
  DynamicFormField,
  ModelItem,
  ModelProviderItem,
  ToolGenerateMessage,
  ToolGenerateCodePayload,
  ToolInputField,
  ToolItem,
} from '@/api/types'
import { isSystemResource, isSystemSharedResource } from '@/utils/resource-context'

defineOptions({ name: 'ToolCodeGenerate' })

const props = withDefaults(
  defineProps<{
    showGenerate?: boolean
    toolForm?: Partial<ToolItem>
  }>(),
  { showGenerate: false },
)
const code = defineModel<string>({ required: true })

// v2 工具代码模板：服务端替换需求、启动参数和输入参数占位符。
const PROMPT_TEMPLATE = `你是资深的 Python 工程师，专注于为 MaxKB 平台的工具 / 数据源场景生成可直接运行的 Python 代码。严格遵守以下规则：

- 仅输出纯 Python 代码块，无任何多余的文字解释、注释以外的说明；
- 代码兼容 Python 3.8 及以上版本，符合 PEP8 编码规范，关键逻辑添加简洁中文注释；
- 仅使用 MaxKB 内置依赖（如 requests、pymysql、pandas、json 等），不引入未声明的第三方库。

{userInput}

请为 MaxKB 工具 生成 Python 代码，需求如下：

- 核心功能：用户输入的主题 / 功能需求
- 启动参数：平台配置的启动参数，如 API 密钥、数据库地址、账号密码等, 已声明参数：{initFieldList}
- 输入参数：平台配置的输入参数，已声明参数：{inputFieldList}
- 函数定义：依次列举所有启动参数和输入参数并声明返回类型
- 输出要求：代码需接收输入参数，启动参数完成业务逻辑，仅输出函数定义
`

// 生成接口：弹窗按当前资源范围选择工具和模型 API。
const requestToolApi = computed(() => {
  if (isSystemResource()) return SystemResourceToolApi
  if (isSystemSharedResource()) return SystemSharedToolApi
  return ToolApi
})
const requestModelApi = computed(() => {
  if (isSystemResource()) return SystemResourceModelApi
  if (isSystemSharedResource()) return SystemSharedModelApi
  return ModelApi
})

// 模型选择：加载当前范围的 LLM，并提供模型参数表单。
const modelOptions = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])
const modelLoading = ref(false)
const modelParamsLoading = ref(false)
const activeModelId = ref('')
const modelParams = ref<Record<string, unknown>>({})

provide('getModelParamsForm', (modelId: string) => {
  modelParamsLoading.value = true
  return requestModelApi.value.getModelParamsForm(modelId).finally(() => {
    modelParamsLoading.value = false
  })
})

function loadModels() {
  modelLoading.value = true
  const workspaceId = props.toolForm?.workspace_id
  const modelRequest =
    'getModelListWithShared' in requestModelApi.value
      ? requestModelApi.value.getModelListWithShared({ model_type: 'LLM', ...(workspaceId ? { workspace_id: workspaceId } : {}) })
      : requestModelApi.value.getModelList({ model_type: 'LLM' })
  return Promise.all([modelRequest, ModelProviderApi.getProviderListByModelType('LLM')])
    .then(([models, providers]) => {
      modelOptions.value = models
      providerOptions.value = providers
      if (activeModelId.value) return
      // 与下拉分组顺序一致，默认选中第一个可用模型并初始化参数。
      const firstModel = Object.values(groupBy(models, 'provider'))
        .flat()
        .find(({ status }) => status === MODEL_STATUS.SUCCESS)
      if (!firstModel) return
      return requestModelApi.value.getModelParamsForm(firstModel.id).then((fields) => {
        activeModelId.value = firstModel.id
        modelParams.value = fields.reduce<Record<string, unknown>>((settings, field) => {
          if (field.show_default_value !== false) settings[field.field] = cloneDeep(field.default_value)
          return settings
        }, {})
      })
    })
    .finally(() => {
      modelLoading.value = false
    })
}

// 生成上下文：打开时复制当前参数定义，关闭后清理模型配置。
const initFieldList = ref<DynamicFormField[]>([])
const inputFieldList = ref<ToolInputField[]>([])
const generateVisible = ref(false)
// 允许先打开弹窗选模型，打开后统一通过 disabled 控制提交。
const generateDisabled = computed(() => generateVisible.value && (!activeModelId.value || modelLoading.value || modelParamsLoading.value))

function initGenerate() {
  generateVisible.value = true
  initFieldList.value = cloneDeep(props.toolForm?.init_field_list ?? [])
  inputFieldList.value = cloneDeep(props.toolForm?.input_field_list ?? [])
  return loadModels()
}

function resetData() {
  generateVisible.value = false
  initFieldList.value = []
  inputFieldList.value = []
  activeModelId.value = ''
  modelParams.value = {}
}

function requestGenerateCode(messages: ToolGenerateMessage[]) {
  const payload: ToolGenerateCodePayload = {
    messages,
    prompt: PROMPT_TEMPLATE,
    init_field_list: cloneDeep(initFieldList.value),
    input_field_list: cloneDeep(inputFieldList.value),
    model_id: activeModelId.value,
    model_params_setting: cloneDeep(modelParams.value),
  }
  return requestToolApi.value.postToolGenerateCode(payload)
}

// 结果回写：去除代码围栏，放大时通过插槽回调替换编辑器草稿。
function handleReplaceCode(value: string, replaceCode?: (value: string) => void) {
  const content = value.trim()
  const codeBlock = content.match(/^```(?:python|py)?[^\S\r\n]*\r?\n([\s\S]*?)\r?\n```$/i)
  const nextCode = codeBlock?.[1] ?? content
  if (replaceCode) {
    replaceCode(nextCode)
  } else {
    code.value = nextCode
  }
  MsgSuccess('替换成功')
}
</script>

<template>
  <section>
    <div class="mb-4 flex-between">
      <div class="flex-align-center gap-2">
        <h4 class="mk-title-decoration mk-required">工具内容（Python）</h4>
        <span class="text-N600">使用工具时不显示</span>
      </div>
      <!-- 生成工具代码 -->
      <GenerateContent
        v-if="showGenerate && props.toolForm"
        title="生成 Python 代码"
        placeholder="请描述这个工具的功能"
        empty-text="Python 代码显示在这里"
        :disabled="generateDisabled"
        :request="requestGenerateCode"
        @open="initGenerate"
        @closed="resetData"
        @replace="handleReplaceCode"
      >
        <template #header-extra="{ loading }">
          <div class="flex-align-center gap-4 w-70!">
            <SelectModel
              v-model="activeModelId"
              v-model:model-params="modelParams"
              :options="modelOptions"
              :provider-options="providerOptions"
              :disabled="loading || modelLoading || modelParamsLoading"
              can-edit-params
              can-add
              teleported
              @refresh="loadModels"
            />
            <el-divider direction="vertical" />
          </div>
        </template>
      </GenerateContent>
    </div>

    <el-form-item prop="code">
      <PythonCodeEditor v-model="code" title="工具内容（Python）">
        <template v-if="showGenerate && props.toolForm" #header-extra="{ replaceCode }">
          <!-- 在放大的编辑器中生成工具代码 -->
          <GenerateContent
            title="生成 Python 代码"
            placeholder="请描述这个工具的功能"
            empty-text="Python 代码显示在这里"
            :disabled="generateDisabled"
            :request="requestGenerateCode"
            @open="initGenerate"
            @closed="resetData"
            @replace="handleReplaceCode($event, replaceCode)"
          >
            <template #header-extra="{ loading }">
              <div class="flex-align-center gap-4 w-70!">
                <SelectModel
                  v-model="activeModelId"
                  v-model:model-params="modelParams"
                  :options="modelOptions"
                  :provider-options="providerOptions"
                  :disabled="loading || modelLoading || modelParamsLoading"
                  can-edit-params
                  can-add
                  teleported
                  @refresh="loadModels"
                />
                <el-divider direction="vertical" />
              </div>
            </template>
          </GenerateContent>
        </template>
      </PythonCodeEditor>
    </el-form-item>
  </section>
</template>
