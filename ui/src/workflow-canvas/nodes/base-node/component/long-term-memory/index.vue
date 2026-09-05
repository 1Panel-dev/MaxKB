<script setup lang="ts">
import { useTemplateRef } from 'vue'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { LongTermSetting } from '../../types'
import LongTermSettingDialog from './LongTermSettingDialog.vue'

defineOptions({ name: 'LongTermMemorySetting' })

const props = defineProps<{
  enabled: boolean
  modelOptions: ModelItem[]
  providerOptions: ModelProviderItem[]
  setting: LongTermSetting
}>()
const emit = defineEmits<{
  'update:enabled': [enabled: boolean]
  'update:setting': [setting: LongTermSetting]
}>()

const dialogRef = useTemplateRef<InstanceType<typeof LongTermSettingDialog>>('dialogRef')

function changeEnabled(value: boolean | number | string) {
  emit('update:enabled', Boolean(value))
}

function openSettings() {
  dialogRef.value?.open(props.setting)
}
</script>

<template>
  <div class="mb-4 flex-between w-full">
    <span class="flex items-center gap-1">
      长期记忆
      <el-tooltip
        content="开启后，从开启时间记录新对话并按周期生成记忆，可通过 {{开始.memory}} 变量在系统提示词中调用。关闭后，将清空对话用户的长期记忆，再次开启将重新从开启时点开始累积。"
        placement="right"
      >
        <MkIcon name="icon_info_outlined" class="text-N600!" />
      </el-tooltip>
    </span>
    <span class="flex items-center gap-2">
      <el-button v-if="enabled" text type="primary" title="长期记忆设置" @click="openSettings">
        <MkIcon name="icon-setting" />
      </el-button>
      <el-switch :model-value="enabled" size="small" @change="changeEnabled" />
    </span>
  </div>

  <LongTermSettingDialog ref="dialogRef" :model-options="modelOptions" :provider-options="providerOptions" @submit="emit('update:setting', $event)" />
</template>
