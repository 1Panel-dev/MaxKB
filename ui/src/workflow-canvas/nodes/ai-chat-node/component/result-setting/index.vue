<script setup lang="ts">
import { QuestionFilled } from '@element-plus/icons-vue'

defineOptions({ name: 'AiChatNodeResultSetting' })

defineProps<{ enabled: boolean }>()
const emit = defineEmits<{ 'update:enabled': [enabled: boolean] }>()

function changeEnabled(value: boolean | number | string) {
  emit('update:enabled', Boolean(value))
}
</script>

<template>
  <el-form-item>
    <template #label>
      <div class="flex-between w-full">
        <span class="flex items-center gap-1">
          返回内容
          <el-tooltip content="开启后，该节点的回答会作为工作流最终响应的一部分返回给用户" placement="right">
            <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
          </el-tooltip>
        </span>
        <el-switch :model-value="enabled" size="small" @change="changeEnabled" />
      </div>
    </template>
  </el-form-item>
</template>
