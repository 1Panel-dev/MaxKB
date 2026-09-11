<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { RESOURCE_TYPE, TOOL_TYPE } from '@/api/enums'
import type { ApplicationDetail, ToolItem, TriggerBodyField, TriggerTaskPayload, TriggerTaskSource, TriggerType } from '@/api/types'
import TaskParameters from './TaskParameters.vue'
import ApplicationApi from '@/api/admin/workspace/application/application'
import ToolApi from '@/api/admin/workspace/tool/tool'
import WorkflowApi from '@/api/admin/workspace/tool/workflow'
import SelectApplicationDialog from '@/components/business/select-application-dialog/index.vue'
import SelectToolDialog from '@/components/business/select-tool-dialog/index.vue'

const props = defineProps<{
  initialResources: Record<string, Partial<ApplicationDetail & ToolItem>>
  active: boolean
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
const parameterRefs = ref<InstanceType<typeof TaskParameters>[]>([])
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
  if (props.disabled || !props.active) return
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
      if (!props.active) return
      selectedResources.forEach(({ id, resource }) => {
        loadedResources.value[`${source}:${id}`] = resource
      })
      tasks.value = [
        ...tasks.value.filter((task) => task.source_type !== source),
        ...selectedResources.map(({ id }) => existingTasks.get(id) ?? { source_type: source, source_id: id, parameter: {} }),
      ]
      void nextTick(expandAll)
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

function handleToggleTaskGroup(type: TriggerTaskSource) {
  if (props.disabled) return
  expandedTaskGroups.value = expandedTaskGroups.value.includes(type)
    ? expandedTaskGroups.value.filter((source) => source !== type)
    : [...expandedTaskGroups.value, type]
}
function handleToggleTask(key: string) {
  if (props.disabled) return
  expandedTaskKeys.value = expandedTaskKeys.value.includes(key)
    ? expandedTaskKeys.value.filter((taskKey) => taskKey !== key)
    : [...expandedTaskKeys.value, key]
}
function handleRemoveTask(task: TriggerTaskPayload) {
  if (props.disabled) return
  tasks.value = tasks.value.filter((current) => current !== task)
}
function expandAll() {
  expandedTaskGroups.value = [RESOURCE_TYPE.APPLICATION, RESOURCE_TYPE.TOOL]
  expandedTaskKeys.value = tasks.value.map(taskKey)
}
function reset() {
  loadedResources.value = {}
  expandedTaskGroups.value = [RESOURCE_TYPE.APPLICATION, RESOURCE_TYPE.TOOL]
  expandedTaskKeys.value = []
}
async function validate() {
  // 分组使用 v-show 保留参数表单，保存时校验所有任务，包括已折叠的任务。
  await nextTick()
  const validations = await Promise.all(parameterRefs.value.map((parameter) => parameter.validate().catch(() => false)))
  return validations.every(Boolean)
}
defineExpose({ validate, expandAll, reset })
</script>

<template>
  <div class="w-full space-y-1">
    <MkCollapse
      v-for="group in taskGroups"
      :key="group.type"
      :expanded="expandedTaskGroups.includes(group.type)"
      :destroy-on-collapse="false"
      trigger-class="py-1!"
      @update:expanded="handleToggleTaskGroup(group.type)"
    >
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
      <div v-if="group.tasks.length" class="mb-2 flex flex-col gap-1">
        <el-card v-for="task in group.tasks" :key="taskKey(task)" class="small" shadow="never">
          <MkCollapse
            :expanded="expandedTaskKeys.includes(taskKey(task))"
            :destroy-on-collapse="false"
            trigger-class="py-0!"
            indicator-position="after"
            @update:expanded="handleToggleTask(taskKey(task))"
          >
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
                <el-button text :disabled="disabled" title="移除任务" @click.stop="handleRemoveTask(task)">
                  <MkIcon name="icon_close_outlined" />
                </el-button>
              </div>
            </template>
            <div class="mt-2">
              <TaskParameters
                ref="parameterRefs"
                v-model="task.parameter"
                :disabled="disabled"
                :source="task.source_type"
                :resource="resources[taskKey(task)]"
                :trigger-type="triggerType"
                :body="body"
              />
            </div>
          </MkCollapse>
        </el-card>
      </div>
    </MkCollapse>
  </div>
  <SelectApplicationDialog ref="applicationDialogRef" @submit="handleSelectResources(RESOURCE_TYPE.APPLICATION, $event)" />
  <SelectToolDialog
    ref="toolDialogRef"
    :tool-types="[TOOL_TYPE.CUSTOM, TOOL_TYPE.WORKFLOW]"
    @submit="handleSelectResources(RESOURCE_TYPE.TOOL, $event)"
  />
</template>
