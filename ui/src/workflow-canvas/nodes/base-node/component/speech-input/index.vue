<script setup lang="ts">
import { computed } from 'vue'
import ModelSelect from '@/components/business/model-select/index.vue'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { SpeechInputSetting } from '../../types'

defineOptions({ name: 'BaseNodeSpeechInput' })

const props = defineProps<{ modelOptions: ModelItem[]; providerOptions: ModelProviderItem[]; setting: SpeechInputSetting }>()
const emit = defineEmits<{ update: [setting: Partial<SpeechInputSetting>] }>()

function updateSetting(patch: Partial<SpeechInputSetting>) {
  emit('update', patch)
}

const enabled = computed({
  get: () => props.setting.stt_model_enable,
  set: (value: boolean) => {
    updateSetting({
      stt_model_enable: value,
      stt_model_id: value ? props.setting.stt_model_id : '',
      stt_model_id_type: props.setting.stt_model_id_type || 'default',
    })
  },
})
const autosend = computed({
  get: () => props.setting.stt_autosend,
  set: (value: boolean) => updateSetting({ stt_autosend: value }),
})
const modelIdType = computed({
  get: () => props.setting.stt_model_id_type,
  set: (value: SpeechInputSetting['stt_model_id_type']) => updateSetting({ stt_model_id_type: value }),
})
const modelId = computed({
  get: () => props.setting.stt_model_id,
  set: (value: string) => updateSetting({ stt_model_id: value }),
})
const modelParams = computed({
  get: () => props.setting.stt_model_params_setting,
  set: (value: Record<string, unknown>) => updateSetting({ stt_model_params_setting: value }),
})
</script>

<template>
  <el-form-item>
    <template #label>
      <div class="flex-between w-full">
        <span>语音输入</span>
        <span class="flex items-center gap-3">
          <el-checkbox v-if="enabled" v-model="autosend">识别后自动发送</el-checkbox>
          <el-switch v-model="enabled" size="small" />
        </span>
      </div>
    </template>
    <template v-if="enabled">
      <el-radio-group v-model="modelIdType" class="mb-2">
        <el-radio value="default">默认模型</el-radio>
        <el-radio value="custom">自定义</el-radio>
      </el-radio-group>
      <el-alert v-if="modelIdType === 'default'" class="w-full" title="使用系统默认语音识别模型" type="info" :closable="false" />
      <ModelSelect
        v-else
        v-model="modelId"
        v-model:model-params="modelParams"
        can-edit-params
        :options="modelOptions"
        :provider-options="providerOptions"
        placeholder="请选择语音识别模型"
      />
    </template>
  </el-form-item>
</template>
