<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { RESOURCE_TYPE, TOOL_TYPE } from '@/api/enums'
import type { ApplicationDetail, ToolItem, TriggerBodyField, TriggerTaskPayload, TriggerTaskSource, TriggerType } from '@/api/types'
import ApplicationParameter from './parameters/ApplicationParameter.vue'
import ToolParameter from './parameters/ToolParameter.vue'
import ApplicationApi from '@/api/admin/workspace/application/application'
import ToolApi from '@/api/admin/workspace/tool/tool'
import WorkflowApi from '@/api/admin/workspace/tool/workflow'
import SelectApplicationDialog from '@/components/business/select-application-dialog/index.vue'
import SelectToolDialog from '@/components/business/select-tool-dialog/index.vue'

const props = defineProps<{
  initialResources: Record<string, Partial<ApplicationDetail & ToolItem>>
  triggerType: TriggerType
  body: TriggerBodyField[]
  disabled: boolean
}>()
const tasks = defineModel<TriggerTaskPayload[]>({ required: true })
const emit = defineEmits<{ change: [] }>()
const loading = defineModel<boolean>('loading', { required: true })
const applicationDialogRef = ref<InstanceType<typeof SelectApplicationDialog>>()
const toolDialogRef = ref<InstanceType<typeof SelectToolDialog>>()
const loadedResources = ref<Record<string, Partial<ApplicationDetail & ToolItem>>>({})
const resources = computed(() => ({ ...props.initialResources, ...loadedResources.value }))
const expandedTaskGroups = ref<TriggerTaskSource[]>([RESOURCE_TYPE.APPLICATION, RESOURCE_TYPE.TOOL])
const expandedTaskKeys = ref<string[]>([])
const parameterRefs = ref<(InstanceType<typeof ApplicationParameter> | InstanceType<typeof ToolParameter>)[]>([])
const taskKey = (task: TriggerTaskPayload) => `${task.source_type}:${task.source_id}`
const taskGroups = computed(() =>
  [
    { type: RESOURCE_TYPE.APPLICATION, label: '智能体' },
    { type: RESOURCE_TYPE.TOOL, label: '工具' },
  ].map((group) => ({ ...group, tasks: tasks.value.filter((task) => task.source_type === group.type) })),
)

/* 选择执行资源并保留已有任务参数 */
function handleOpenApplicationDialog() {
  applicationDialogRef.value?.open(
    tasks.value
      .filter((task) => task.source_type === RESOURCE_TYPE.APPLICATION)
      .map((task) => ({ ...resources.value[taskKey(task)], id: task.source_id })),
  )
}
function handleOpenToolDialog() {
  toolDialogRef.value?.open(
    tasks.value.filter((task) => task.source_type === RESOURCE_TYPE.TOOL).map((task) => ({ ...resources.value[taskKey(task)], id: task.source_id })),
  )
}
function handleSelectResources(source: TriggerTaskSource, selected: { id: string }[]) {
  if (props.disabled) return
  const existingTasks = new Map(tasks.value.filter((task) => task.source_type === source).map((task) => [task.source_id, task]))
  loading.value = true
  // 先完整加载新增资源，任一请求失败时保留原来的关联任务。
  return Promise.all(
    selected.map((resource) => {
      const key = `${source}:${resource.id}`
      if (resources.value[key]) return Promise.resolve({ id: resource.id, resource: resources.value[key]! })
      if (source === RESOURCE_TYPE.APPLICATION)
        return ApplicationApi.getApplicationDetail(resource.id).then((application) => ({ id: resource.id, resource: application }))
      return ToolApi.getToolDetail(resource.id).then((tool) => {
        if (tool.tool_type === TOOL_TYPE.WORKFLOW && !tool.work_flow)
          return WorkflowApi.getToolWorkflow(tool.id).then((workflow) => ({ id: tool.id, resource: { ...tool, work_flow: workflow.work_flow } }))
        return { id: tool.id, resource: tool }
      })
    }),
  )
    .then((selectedResources) => {
      selectedResources.forEach(({ id, resource }) => {
        loadedResources.value[`${source}:${id}`] = resource
      })
      tasks.value = [
        ...tasks.value.filter((task) => task.source_type !== source),
        ...selectedResources.map(({ id }) => existingTasks.get(id) ?? { source_type: source, source_id: id, parameter: {} }),
      ]
      emit('change')
    })
    .finally(() => {
      loading.value = false
    })
}
function handleOpenTaskDialog(type: TriggerTaskSource) {
  if (props.disabled) return
  if (type === RESOURCE_TYPE.APPLICATION) handleOpenApplicationDialog()
  else handleOpenToolDialog()
}

function handleRemoveTask(task: TriggerTaskPayload) {
  if (props.disabled) return
  tasks.value = tasks.value.filter((current) => current !== task)
}

function reset() {
  loadedResources.value = {}
  expandedTaskGroups.value = [RESOURCE_TYPE.APPLICATION, RESOURCE_TYPE.TOOL]
  expandedTaskKeys.value = []
}
async function validate() {
  // 先展开所有任务，等待参数表单挂载后再统一校验。
  expandedTaskGroups.value = [RESOURCE_TYPE.APPLICATION, RESOURCE_TYPE.TOOL]
  expandedTaskKeys.value = tasks.value.map(taskKey)
  await nextTick()
  const validations = await Promise.all(parameterRefs.value.map((parameter) => parameter.validate().catch(() => false)))
  return validations.every(Boolean)
}
defineExpose({ validate, reset })
</script>

<template>
  <div class="w-full space-y-2">
    <template v-for="group in taskGroups" :key="group.type">
      <MkCollapse trigger-class="py-0!" :default-expanded="true">
        <template #label>
          <div class="flex-between min-w-0 flex-1">
            <span
              >{{ group.label }}<span v-if="group.tasks.length">（{{ group.tasks.length }}）</span></span
            >
            <!-- 添加该分组的执行任务 -->
            <el-button text type="primary" :disabled="disabled" :title="`添加${group.label}`" @click.stop="handleOpenTaskDialog(group.type)">
              <MkIcon name="icon_add_outlined" />
            </el-button>
          </div>
        </template>

        <div v-if="group.tasks.length" class="mt-2 flex flex-col gap-1">
          <template v-for="task in group.tasks" :key="taskKey(task)">
            <el-card class="small" shadow="never">
              <MkCollapse trigger-class="py-0!">
                <template #label>
                  <div class="flex-between min-w-0 flex-1">
                    <span class="flex min-w-0 items-center gap-2">
                      <ApplicationIcon
                        v-if="task.source_type === RESOURCE_TYPE.APPLICATION"
                        :icon="resources[taskKey(task)]?.icon"
                        :size="20"
                        class="shrink-0 small"
                      />
                      <ToolIcon
                        v-else
                        :icon="resources[taskKey(task)]?.icon"
                        :type="resources[taskKey(task)]?.tool_type"
                        :size="20"
                        class="shrink-0 small"
                      />
                      <span class="truncate" :title="resources[taskKey(task)]?.name || task.source_id">{{
                        resources[taskKey(task)]?.name || task.source_id
                      }}</span>
                    </span>
                    <!-- 移除执行任务 -->
                    <el-button text :disabled="disabled" @click.stop="handleRemoveTask(task)">
                      <MkIcon name="icon_close_outlined" />
                    </el-button>
                  </div>
                </template>
                <div class="my-2">
                  <ApplicationParameter
                    v-if="task.source_type === RESOURCE_TYPE.APPLICATION"
                    ref="parameterRefs"
                    v-model="task.parameter"
                    :disabled="disabled"
                    :application="resources[taskKey(task)]"
                    :trigger-type="triggerType"
                    :body="body"
                  />
                  <ToolParameter
                    v-else
                    ref="parameterRefs"
                    v-model="task.parameter"
                    :disabled="disabled"
                    :tool="resources[taskKey(task)]"
                    :trigger-type="triggerType"
                    :body="body"
                  />
                </div>
              </MkCollapse>
            </el-card>
          </template>
        </div>
      </MkCollapse>
    </template>
  </div>
  <SelectApplicationDialog ref="applicationDialogRef" @submit="handleSelectResources(RESOURCE_TYPE.APPLICATION, $event)" />
  <SelectToolDialog
    ref="toolDialogRef"
    :tool-types="[TOOL_TYPE.CUSTOM, TOOL_TYPE.WORKFLOW]"
    @submit="handleSelectResources(RESOURCE_TYPE.TOOL, $event)"
  />
</template>
