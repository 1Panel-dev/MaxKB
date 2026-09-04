<script setup lang="ts">
import { computed } from 'vue'
import ModelSelect from '@/components/business/model-select/index.vue'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { SpeechPlaybackSetting } from '../../types'

defineOptions({ name: 'BaseNodeSpeechPlayback' })

const props = defineProps<{ modelOptions: ModelItem[]; providerOptions: ModelProviderItem[]; setting: SpeechPlaybackSetting }>()
const emit = defineEmits<{ update: [setting: Partial<SpeechPlaybackSetting>] }>()

function updateSetting(patch: Partial<SpeechPlaybackSetting>) {
  emit('update', patch)
}

const enabled = computed({
  get: () => props.setting.tts_model_enable,
  set: (value: boolean) => {
    updateSetting({
      tts_model_enable: value,
      tts_model_id: value ? props.setting.tts_model_id : '',
      tts_type: value ? props.setting.tts_type : 'BROWSER',
    })
  },
})
const autoplay = computed({
  get: () => props.setting.tts_autoplay,
  set: (value: boolean) => updateSetting({ tts_autoplay: value }),
})
const speechType = computed({
  get: () => props.setting.tts_type,
  set: (value: SpeechPlaybackSetting['tts_type']) => updateSetting({ tts_type: value }),
})
const modelId = computed({
  get: () => props.setting.tts_model_id,
  set: (value: string) => updateSetting({ tts_model_id: value }),
})
const modelParams = computed({
  get: () => props.setting.tts_model_params_setting,
  set: (value: Record<string, unknown>) => updateSetting({ tts_model_params_setting: value }),
})
</script>

<template>
  <el-form-item>
    <template #label>
      <div class="flex-between w-full">
        <span>语音播放</span>
        <span class="flex items-center gap-3">
          <el-checkbox v-if="enabled" v-model="autoplay">自动播放</el-checkbox>
          <el-switch v-model="enabled" size="small" />
        </span>
      </div>
    </template>
    <template v-if="enabled">
      <el-radio-group v-model="speechType" class="mb-2">
        <el-radio value="BROWSER">浏览器</el-radio>
        <el-radio value="DEFAULT">默认模型</el-radio>
        <el-radio value="CUSTOM">自定义</el-radio>
      </el-radio-group>
      <el-alert v-if="speechType === 'BROWSER'" class="w-full" title="使用浏览器内置语音播放" type="info" :closable="false" />
      <el-alert v-else-if="speechType === 'DEFAULT'" class="w-full" title="使用系统默认语音合成模型" type="info" :closable="false" />
      <ModelSelect
        v-else
        v-model="modelId"
        v-model:model-params="modelParams"
        can-edit-params
        :options="modelOptions"
        :provider-options="providerOptions"
        placeholder="请选择语音合成模型"
      />
    </template>
  </el-form-item>
</template>
