<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import type { FormInstance } from 'element-plus'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
import { fileTooltip } from '@/workflow-canvas/config/constants'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowImageToVideoNode' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()

interface ImageToVideoNodeForm {
  model_id: string
  model_id_type: 'custom' | 'default' | 'reference'
  model_id_reference: string[]
  prompt: string
  negative_prompt: string
  dialogue_number: number
  dialogue_type: 'NODE' | 'WORKFLOW'
  first_frame_url: string[]
  is_result: boolean
  last_frame_url: string[]
  model_params_setting: Record<string, unknown>
}

const formRef = useTemplateRef<FormInstance>('formRef')

const store = useWorkflowStore(apiType)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

const defaultForm: ImageToVideoNodeForm = {
  model_id: '',
  model_id_type: 'default',
  model_id_reference: [],
  prompt: '{{开始.question}}',
  negative_prompt: '',
  dialogue_number: 0,
  dialogue_type: 'NODE',
  first_frame_url: ['start-node', 'image'],
  is_result: true,
  last_frame_url: [],
  model_params_setting: {},
}
const savedForm = model.properties.node_data as Partial<ImageToVideoNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  model_id_type: savedForm ? (savedForm.model_id_type ?? 'custom') : defaultForm.model_id_type,
  model_id_reference: Array.isArray(savedForm?.model_id_reference) ? savedForm.model_id_reference : [],
  model_params_setting: savedForm?.model_params_setting ?? {},
  prompt: savedForm?.prompt ?? defaultForm.prompt,
  negative_prompt: savedForm?.negative_prompt ?? defaultForm.negative_prompt,
  dialogue_type: savedForm?.dialogue_type ?? defaultForm.dialogue_type,
  dialogue_number: savedForm?.dialogue_number ?? defaultForm.dialogue_number,
  is_result: savedForm ? savedForm.is_result : defaultForm.is_result,
  first_frame_url: savedForm ? (Array.isArray(savedForm.first_frame_url) ? savedForm.first_frame_url : []) : defaultForm.first_frame_url,
  last_frame_url: Array.isArray(savedForm?.last_frame_url) ? savedForm.last_frame_url : [],
}

const formData = computed<ImageToVideoNodeForm>({
  get: () => model.properties.node_data as ImageToVideoNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const showSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function updateNodeData(setting: Partial<ImageToVideoNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  model.validate = validate
  store.getModelList({ model_type: 'ITV' }).then((data) => {
    modelList.value = data
  })
  store.getProviderList().then((data) => {
    providerOptions.value = data
  })
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <NodeModelSelect
          :node-model="model"
          :form-data="formData"
          model-type="ITV"
          label="图生视频模型"
          :options="modelList"
          :provider-options="providerOptions"
          @update="updateNodeData"
        />

        <!-- 提示词(正向) -->
        <el-form-item class="mk-hide-asterisk" prop="prompt" :rules="{ required: true, message: '请输入正向提示词', trigger: 'blur' }">
          <template #label>
            <div class="flex items-center gap-1">
              <span class="mk-required">提示词(正向)</span>

              <el-tooltip content="正向提示词，用来描述基于首帧图片生成视频时的运动和画面变化" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </el-tooltip>
            </div>
          </template>
          <MdEditorMagnify v-model="formData.prompt" title="提示词(正向)" @wheel="handleNodeWheel" />
        </el-form-item>

        <!-- 提示词(负向) -->
        <el-form-item prop="negative_prompt">
          <template #label>
            <div class="flex items-center gap-1">
              <span>提示词(负向)</span>
              <el-tooltip content="反向提示词，用来描述不希望在画面中看到的内容，可以对画面进行限制" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </el-tooltip>
            </div>
          </template>
          <MdEditorMagnify
            v-model="formData.negative_prompt"
            title="提示词(负向)"
            placeholder="请描述不想生成的视频内容，比如：颜色、血腥内容"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

        <!-- 首帧图片 -->
        <el-form-item class="mk-hide-asterisk" prop="first_frame_url" :rules="{ required: true, message: '请选择首帧图片', trigger: 'change' }">
          <template #label>
            <span class="flex items-center gap-1">
              <span class="mk-required">首帧图片</span>
              <el-tooltip placement="right">
                <template #content>
                  <div class="font-mono whitespace-pre-wrap">{{ fileTooltip }}</div>
                </template>
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </el-tooltip>
            </span>
          </template>
          <NodeCascader v-model="formData.first_frame_url" :node-model="model" placeholder="请选择首帧图片" />
        </el-form-item>

        <!-- 尾帧图片 -->
        <el-form-item prop="last_frame_url">
          <template #label>
            <span class="flex items-center gap-1">
              尾帧图片
              <el-tooltip placement="right">
                <template #content>
                  <div class="font-mono whitespace-pre-wrap">{{ fileTooltip }}</div>
                </template>
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </el-tooltip>
            </span>
          </template>
          <NodeCascader v-model="formData.last_frame_url" :node-model="model" placeholder="请选择尾帧图片" />
        </el-form-item>

        <!-- 返回内容 -->
        <div class="flex-between w-full" v-if="showSettings">
          <span class="flex items-center gap-1">
            返回内容
            <el-tooltip content="关闭后该节点的内容则不输出给用户。如果你想让用户看到该节点的输出内容，请打开开关。" placement="right">
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </el-tooltip>
          </span>
          <span>
            <el-switch v-model="formData.is_result" size="small" />
          </span>
        </div>
      </el-form>
    </div>
  </NodeContainer>
</template>
