<script setup lang="ts">
import type { DialogueSource, HistorySetting } from '../../types'

defineOptions({ name: 'AiChatNodeHistorySetting' })

const props = defineProps<{ setting: HistorySetting }>()
const emit = defineEmits<{ update: [setting: HistorySetting] }>()

function updateSetting(changes: Partial<HistorySetting>) {
  emit('update', { ...props.setting, ...changes })
}
</script>

<template>
  <el-form-item label="历史聊天记录" prop="dialogue_number" :rules="{ required: true, message: '请设置历史聊天轮数', trigger: 'change' }">
    <template #label>
      <div class="flex-between w-full gap-3">
        <span>历史聊天记录</span>
        <el-select
          :model-value="setting.dialogue_type"
          :teleported="false"
          class="w-24!"
          size="small"
          @update:model-value="updateSetting({ dialogue_type: $event as DialogueSource })"
        >
          <el-option label="当前节点" value="NODE" />
          <el-option label="整个工作流" value="WORKFLOW" />
        </el-select>
      </div>
    </template>
    <el-input-number
      :model-value="setting.dialogue_number"
      class="w-full!"
      controls-position="right"
      align="left"
      :min="0"
      :step="1"
      step-strictly
      value-on-clear="min"
      @update:model-value="updateSetting({ dialogue_number: Number($event ?? 0) })"
    />
  </el-form-item>
</template>
