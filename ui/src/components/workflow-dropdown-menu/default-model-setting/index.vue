<template>
  <div
    v-show="show"
    v-click-outside="handleClickOutside"
    class="default-model-setting-menu workflow-dropdown-menu border border-r-6 white-bg"
  >
    <div class="title">{{ $t('workflow.setting.defaultModelSetting') }}</div>
    <el-alert :title="$t('workflow.setting.defaultModelSettingTip')" type="info" :closable="false" />
    <el-scrollbar max-height="calc(100vh - 220px)">
      <el-form label-position="top" class="p-12">
        <el-form-item v-for="item in defaultModelTypes" :key="item.type" :label="item.label">
          <div class="flex-between w-full">
            <ModelSelect
              v-model="modelSetting[item.type].model_id"
              :options="defaultModelOptions[item.type]"
              :model-type="item.type"
              :placeholder="$t('views.application.form.aiModel.placeholder')"
              @change="(val: any) => handleModelChange(item.type, val)"
              showFooter
              clearable
              style="flex: 1; min-width: 0"
            />
            <el-button
              class="ml-8"
              :disabled="!modelSetting[item.type].model_id"
              @click="openModelParam(item)"
              icon="Operation"
            />
          </div>
        </el-form-item>
      </el-form>
    </el-scrollbar>
    <div class="flex-between p-12">
      <el-button @click="applyDefaultModelToAll">
        {{ $t('workflow.setting.applyToAll') }}
      </el-button>
      <el-button type="primary" @click="handleSave">
        {{ $t('common.save') }}
      </el-button>
    </div>
    <AIModeParamSettingDialog ref="modelParamDialogRef" @refresh="refreshModelParam" />
  </div>
</template>
<script setup lang="ts">
import { ref, computed, watch, inject } from 'vue'
import { t } from '@/locales'
import { groupBy } from 'lodash'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import ModelSelect from '@/components/model-select/index.vue'
import AIModeParamSettingDialog from '@/views/application/component/AIModeParamSettingDialog.vue'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
  show: { type: Boolean, default: false },
  workflowRef: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'save', 'close'])

const getResourceDetail = inject('getResourceDetail') as any
const apiType = computed(() => {
  const path = window.location.pathname
  if (path.includes('resource-management')) return 'systemManage'
  if (path.includes('shared')) return 'systemShare'
  if (path.includes('share/')) return 'workspaceShare'
  return 'workspace'
})

const defaulTypeLabels: Record<string, string> = {
  LLM: t('workflow.setting.modelType.LLM'),
  TTS: t('workflow.setting.modelType.TTS'),
  STT: t('workflow.setting.modelType.STT'),
  IMAGE: t('workflow.setting.modelType.IMAGE'),
  TTI: t('workflow.setting.modelType.TTI'),
  TTV: t('workflow.setting.modelType.TTV'),
  ITV: t('workflow.setting.modelType.ITV'),
  RERANKER: t('workflow.setting.modelType.RERANKER'),
}
const defaultModelTypes = ['LLM', 'TTS', 'STT', 'IMAGE', 'TTI', 'TTV', 'ITV', 'RERANKER'].map((type) => ({
  type,
  label: defaulTypeLabels[type] || type,
}))
const EMPTY_SETTING = { LLM: {}, TTS: {}, STT: {}, IMAGE: {}, TTI: {}, TTV: {}, ITV: {}, RERANKER: {} }

const modelSetting = ref<any>({ ...EMPTY_SETTING })
const defaultModelOptions = ref<Record<string, any>>({})
const modelParamDialogRef = ref<InstanceType<typeof AIModeParamSettingDialog>>()
const currentModelType = ref('LLM')

watch(
  () => props.show,
  (visible) => {
    if (!visible) return
    modelSetting.value = { ...EMPTY_SETTING }
    for (const { type } of defaultModelTypes) {
      // props.modelValue 为 Vue 响应式 Proxy,structuredClone 无法克隆 Proxy 会抛 DataCloneError;
      // 面板配置为纯 JSON 数据,用 JSON 深拷贝剥离响应式且避免与父层别共享引用
      modelSetting.value[type] = JSON.parse(JSON.stringify((props.modelValue as any)?.[type] || {}))
      loadModelOptions(type)
    }
  },
)

function loadModelOptions(type: string) {
  const obj =
    apiType.value === 'systemManage'
      ? { model_type: type, workspace_id: (getResourceDetail?.() as any)?.value?.workspace_id }
      : { model_type: type }
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .getSelectModelList(obj)
    .then((res: any) => {
      defaultModelOptions.value[type] = groupBy(res?.data || [], 'provider')
    })
}

function handleModelChange(type: string, _val: any) {
  modelSetting.value[type].model_params_setting = {}
  // 改动实时同步到父层 detail.default_model_setting,使「未点面板保存就发布」也能带上本次编辑;
  // 节点上的 DefaultModelDisplay 也会随之实时更新
  emit('update:modelValue', { ...modelSetting.value })
}

function openModelParam(item: { type: string }) {
  const cfg = modelSetting.value[item.type]
  if (!cfg?.model_id) return
  currentModelType.value = item.type
  modelParamDialogRef.value?.open(cfg.model_id, undefined, cfg.model_params_setting)
}

function refreshModelParam(paramData: any) {
  const type = currentModelType.value
  if (modelSetting.value[type]?.model_id) {
    modelSetting.value[type].model_params_setting = paramData
    emit('update:modelValue', { ...modelSetting.value })
  }
}

function handleSave() {
  emit('update:modelValue', { ...modelSetting.value })
  emit('save')
}

function applyDefaultModelToAll() {
  MsgConfirm(
    t('workflow.setting.applyToAll'),
    t('workflow.setting.applyToAllConfirmMsg'),
    { type: 'warning', customClass: 'apply-to-all-confirm', center: true, confirmButtonText: t('workflow.setting.apply') },
  ).then(() => {
    const graph = props.workflowRef?.getGraphData()
    let count = 0
    // 栈式遍历,循环节点内嵌 graph(loop_body)也入栈覆盖,与发布校验 validate_workflow_default_models 保持一致
    const stack: any[] = [...(graph?.nodes || [])]
    while (stack.length) {
      const node = stack.pop()
      const nd = node?.properties?.node_data
      if (!nd) continue
      if (node.type === 'base-node') {
        // base-node 只有 default/custom(tts 另有 BROWSER),应用默认模型即覆盖 custom
        if (nd.stt_model_enable && nd.stt_model_id_type !== 'default') {
          nd.stt_model_id_type = 'default'
          count++
        }
        if (nd.tts_model_enable && nd.tts_type !== 'BROWSER' && nd.tts_type !== 'DEFAULT') {
          nd.tts_type = 'DEFAULT'
          count++
        }
        if (nd.long_term_enable && nd.long_term_model_id_type !== 'default') {
          nd.long_term_model_id_type = 'default'
          count++
        }
        continue
      }
      const key =
        node.type === 'speech-to-text-node'
          ? 'stt_model_id_type'
          : node.type === 'text-to-speech-node'
            ? 'tts_model_id_type'
            : node.type === 'reranker-node'
              ? 'reranker_model_id_type'
              : nd.model_id_type !== undefined
                ? 'model_id_type'
                : null
      if (key && nd[key] !== 'default') {
        nd[key] = 'default'
        count++
      }
      if (node.type === 'loop-node' && nd.loop_body?.nodes) {
        stack.push(...nd.loop_body.nodes)
      }
    }
    if (count > 0) {
      props.workflowRef?.renderGraphData(graph)
      MsgSuccess(t('workflow.setting.applyToAllSuccess', { count }))
    } else {
      MsgSuccess(t('workflow.setting.applyToAllNone'))
    }
  })
}

function handleClickOutside(e: MouseEvent, _e2?: MouseEvent) {
  const target = e.target as HTMLElement | null
  // ModelSelect 下拉(popper-class select-model)与参数弹窗(el-dialog append-to-body 及其 .el-overlay 遮罩)
  // 都 teleport 到 body,不在面板 DOM 树内,v-click-outside 会误判为"面板外点击"。
  // 此处显式排除:点击这两类浮层内(含弹窗遮罩)视为面板内交互,不关闭。
  if (target && (target.closest('.select-model') || target.closest('.el-overlay'))) return
  emit('close')
}
</script>
<style lang="scss">
@use '../index.scss';

.default-model-setting-menu {
  width: 400px;

  .el-alert {
    margin: 0 12px 12px;
    width: calc(100% - 24px);
  }

  .el-form-item {
    margin-bottom: 12px;
  }
}
</style>
