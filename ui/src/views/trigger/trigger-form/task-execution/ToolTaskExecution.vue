<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import { RESOURCE_TYPE } from '@/api/enums'
import type { ToolItem, TriggerBodyField, TriggerTaskPayload, TriggerType } from '@/api/types'
import TaskParameterForm from './components/TaskParameterForm.vue'

const props = defineProps<{ tool?: Partial<ToolItem>; triggerType: TriggerType; body: TriggerBodyField[]; disabled: boolean }>()
const tasks = defineModel<TriggerTaskPayload[]>({ required: true })
const task = computed(() => tasks.value[0])
const expanded = ref(true)
const parameterRef = useTemplateRef<InstanceType<typeof TaskParameterForm>>('parameterRef')

/* 固定当前资源，仅编辑执行参数。 */
async function validate() {
  expanded.value = true
  await nextTick()
  return task.value ? (parameterRef.value?.validate().catch(() => false) ?? false) : false
}
defineExpose({ validate })
</script>

<template>
  <el-card v-if="task" class="small" shadow="never">
    <MkCollapse v-model:expanded="expanded">
      <template #label>
        <div class="flex-align-center min-w-0 gap-2">
          <ToolIcon :icon="props.tool?.icon" :type="props.tool?.tool_type" :size="20" class="shrink-0" />
          <span class="truncate" :title="props.tool?.name || task.source_id">{{ props.tool?.name || task.source_id }}</span>
        </div>
      </template>
      <TaskParameterForm
        ref="parameterRef"
        v-model="task.parameter"
        class="mt-2"
        :resource="{ type: RESOURCE_TYPE.TOOL, data: props.tool }"
        :trigger-type="triggerType"
        :body="body"
        :disabled="disabled"
      />
    </MkCollapse>
  </el-card>
</template>
