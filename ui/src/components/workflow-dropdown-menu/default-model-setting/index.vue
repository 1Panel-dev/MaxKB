<template>
  <div
    v-if="show"
    v-click-outside="handleClickOutside"
    class="default-model-setting-menu workflow-dropdown-menu border border-r-6 white-bg"
  >
    <div class="title">
      <h4 class="mb-4">{{ $t('workflow.setting.defaultModelSetting') }}</h4>
      <p class="mb-8">
        <el-text type="info">{{ $t('workflow.setting.defaultModelSettingTip') }}</el-text>
      </p>
    </div>

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
              :disabled="readonly"
              style="flex: 1; min-width: 0"
            />
            <el-button
              class="ml-8"
              :disabled="readonly || !modelSetting[item.type].model_id || item.type === 'RERANKER'"
              @click="openModelParam(item)"
              icon="Operation"
            />
          </div>
        </el-form-item>
      </el-form>
    </el-scrollbar>
    <div class="flex-between p-12">
      <el-button :disabled="readonly" @click="applyDefaultModelToAll">
        {{ $t('workflow.setting.applyToAll') }}
      </el-button>
      <el-button type="primary" :disabled="readonly || !hasChanges" @click="handleSave">
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
  readonly: { type: Boolean, default: false },
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
const defaultModelTypes = ['LLM', 'TTS', 'STT', 'IMAGE', 'TTI', 'TTV', 'ITV', 'RERANKER'].map(
  (type) => ({
    type,
    label: defaulTypeLabels[type] || type,
  }),
)
const EMPTY_SETTING = {
  LLM: {},
  TTS: {},
  STT: {},
  IMAGE: {},
  TTI: {},
  TTV: {},
  ITV: {},
  RERANKER: {},
}

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
  // 面板改为 v-if 挂载:每次打开都是全新实例,watch 需 immediate 在挂载时即同步暂存副本
  { immediate: true },
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
  // 只改动面板内的暂存副本 modelSetting,不实时同步到父层 detail.default_model_setting;
  // 未点「保存」前,节点默认模型模式不会取到未持久化的配置(发布校验/调试行为一致)
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
  }
}

// 暂存副本与已持久化的 detail.default_model_setting(props.modelValue)是否有实质差异。
// modelSetting 固定含全部 8 个类别(未配置为 {}),而 props.modelValue 仅含已配置类别,
// 故不能直接整对象序列化比较;按类别比较 model_id 与参数即可。
// 只读时无任何可编辑操作,hasChanges 恒为 false。
const hasChanges = computed(
  () =>
    !props.readonly &&
    defaultModelTypes.some(({ type }) => {
      const cur = modelSetting.value[type] || {}
      const base = (props.modelValue || {})[type] || {}
      return (
        (cur.model_id || '') !== (base.model_id || '') ||
        JSON.stringify(cur.model_params_setting || {}) !==
          JSON.stringify(base.model_params_setting || {})
      )
    }),
)

function commitSetting() {
  emit('update:modelValue', { ...modelSetting.value })
}

// 将暂存副本重置为已持久化的配置(用于「不保存」丢弃暂存)。
function resetSetting() {
  modelSetting.value = { ...EMPTY_SETTING }
  for (const { type } of defaultModelTypes) {
    modelSetting.value[type] = JSON.parse(JSON.stringify((props.modelValue as any)?.[type] || {}))
  }
}

function handleSave() {
  commitSetting()
  emit('save')
}

function applyDefaultModelToAll() {
  MsgConfirm(t('workflow.setting.applyToAll'), t('workflow.setting.applyToAllConfirmMsg'), {
    type: 'warning',
    customClass: 'apply-to-all-confirm',
    center: true,
    confirmButtonText: t('workflow.setting.apply'),
  }).then(() => {
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

async function handleClickOutside(e: MouseEvent, _e2?: MouseEvent) {
  // 面板用 v-show 隐藏(未卸载),v-click-outside 的监听仍常驻 document;
  // 隐藏后点击任意处不应再触发关闭/确认逻辑。
  if (!props.show) return
  const target = e.target as HTMLElement | null
  // ModelSelect 下拉(popper-class select-model)与参数弹窗(el-dialog append-to-body 及其 .el-overlay 遮罩)
  // 都 teleport 到 body,不在面板 DOM 树内,v-click-outside 会误判为"面板外点击"。
  // 此处显式排除:点击这两类浮层内(含弹窗遮罩、确认弹窗)视为面板内交互,不关闭。
  if (target && (target.closest('.select-model') || target.closest('.el-overlay'))) return
  if (!hasChanges.value) {
    // 无未保存修改,直接关闭
    emit('close')
    return
  }
  // 有未保存修改,弹确认:「保存修改」/「不保存」/「取消(关闭弹窗)」
  try {
    const action = await MsgConfirm(
      t('common.tip'),
      t('workflow.setting.defaultModelSettingUnsaved'),
      {
        type: 'warning',
        confirmButtonText: t('workflow.setting.saveChanges'),
        cancelButtonText: t('workflow.setting.discardChanges'),
        distinguishCancelAndClose: true,
      },
    )
    // 保存修改并关闭
    if (action === 'confirm') {
      commitSetting()
      emit('save')
      emit('close')
    }
  } catch (action: any) {
    // cancel → 选择「不保存」,丢弃暂存修改,关闭面板;close → 取消,保持面板打开
    if (action === 'close') return
    // 丢弃暂存,重置为已持久化配置,避免隐藏后 hasChanges 残留导致再次点击又弹确认
    resetSetting()
    emit('close')
  }
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
