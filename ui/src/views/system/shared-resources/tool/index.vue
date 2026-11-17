<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { ParamsPage } from '@/api/admin/core/types'
import type { Dict, OptionItem, ToolItem, ToolType } from '@/api/types'
import { RESOURCE_TYPE, TOOL_TYPE } from '@/api/enums'
import CommonSystemApi from '@/api/admin/system/common'
import SystemSharedRelatedResourcesApi from '@/api/admin/system/shared-resources/related-resources'
import SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import SystemSharedToolWorkflowApi from '@/api/admin/system/shared-resources/tool/tool-workflow'
import ButtonCreateTool from '@/views/tool/components/ButtonCreateTool.vue'
import ButtonToolStore from '@/views/tool/components/ButtonToolStore.vue'
import ToolCard from '@/views/tool/tool-card/ToolCard.vue'
import ToolStatusSwitch from '@/views/tool/tool-card/ToolStatusSwitch.vue'
import {
  CopyToolAction,
  DeleteToolAction,
  ExecutionRecordToolAction,
  ExportToolAction,
  InitParamAction,
  McpConfigAction,
  RelatedResourcesToolAction,
} from '@/views/tool/tool-card/action-dropdown'
import EditToolForm from '@/views/tool/tool-form/EditToolForm.vue'
import AuthorizedWorkspaceAction from '../authorized-workspace-action/index.vue'
import { TOOL_TYPE_OPTIONS } from '@/constants'
import perm from '@/permission'

const { t } = useI18n({ useScope: 'global' })

const router = useRouter()

/* 共享工具查询 */
const toolsData = ref<ToolItem[]>([])
const toolQuery = ref<Dict<unknown>>()
const toolType = ref<ToolType | ''>('')
const creatorOptions = ref<OptionItem<string>[]>([])
const infiniteScrollRef = useTemplateRef<{ reset: () => Promise<void> }>('infiniteScrollRef')
const searchFields = computed(() => [
  { label: t('common.name.label'), value: 'name' },
  {
    label: t('common.status.label'),
    value: 'is_active',
    options: [
      { value: true, label: t('common.status.enabled') },
      { value: false, label: t('common.status.disabled') },
    ],
  },
  { label: t('common.labels.creator'), value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])

function loadCreatorOptions(keyword: string) {
  return CommonSystemApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ label: nick_name, value: id }))
  })
}

function loadToolsPage(pagination: ParamsPage) {
  return SystemSharedToolApi.getToolPage(pagination, { ...toolQuery.value, ...(toolType.value ? { tool_type: toolType.value } : {}) })
}

function refreshTools() {
  return infiniteScrollRef.value?.reset()
}

function handleSearchChange(query?: Dict<unknown>) {
  toolQuery.value = query
  refreshTools()
}

/* 共享工具维护 */
const toolOperationLoading = ref(false)
const editToolFormRef = useTemplateRef<InstanceType<typeof EditToolForm>>('editToolFormRef')

function handleOpenEditTool(tool: ToolItem) {
  if (!perm.tool.share.edit()) return
  return editToolFormRef.value?.open(tool)
}

function handleOpenTool(tool: ToolItem, event: MouseEvent) {
  if (tool.tool_type === TOOL_TYPE.WORKFLOW) {
    const target = { name: 'system-shared-workflow-tool', params: { toolId: tool.id } }
    if (event.ctrlKey || event.metaKey) {
      window.open(router.resolve(target).href)
      return
    }
    return router.push(target)
  }
  handleOpenEditTool(tool)
}

function handleToolUpdate(tool: ToolItem) {
  const toolIndex = toolsData.value.findIndex(({ id }) => id === tool.id)
  if (toolIndex >= 0) toolsData.value.splice(toolIndex, 1, tool)
}

function handleOpenWorkflow(tool: ToolItem, event: MouseEvent) {
  const target = { name: 'system-shared-workflow-tool', params: { toolId: tool.id } }
  if (event.ctrlKey || event.metaKey) {
    window.open(router.resolve(target).href)
    return
  }
  return router.push(target)
}
</script>

<template>
  <MkViewLayout :title="t('tool.title')" class="shared-tool-view">
    <template #default="{ Header }">
      <component :is="Header">
        <div class="flex-align-center gap-4">
          <h4>{{ t('tool.categories.all') }}</h4>
          <el-divider direction="vertical" />
          <el-select v-model="toolType" class="w-30!" :empty-values="[null, undefined]" @change="refreshTools">
            <el-option v-for="option in TOOL_TYPE_OPTIONS" :key="option.value" :label="t(option.labelKey)" :value="option.value" />
          </el-select>
        </div>
        <div class="flex-align-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <!-- 工具商店 -->
          <ButtonToolStore folder-id="default" @refresh="refreshTools" />
          <!-- 创建共享工具 -->
          <ButtonCreateTool v-if="perm.tool.share.create()" folder-id="default" :api="SystemSharedToolApi" @refresh="refreshTools" />
        </div>
      </component>
      <div v-loading="toolOperationLoading" class="min-h-0 flex-1">
        <MkInfiniteScroll ref="infiniteScrollRef" v-model="toolsData" :load="loadToolsPage">
          <div class="mk-resource-card-grid">
            <template v-for="tool in toolsData" :key="tool.id">
              <ToolCard
                v-model:loading="toolOperationLoading"
                :tool="tool"
                :shared="true"
                :store-tools="[]"
                @click="handleOpenTool(tool, $event)"
                @update="handleToolUpdate"
              >
                <template #actions>
                  <!-- 修改工具状态 -->
                  <ToolStatusSwitch
                    :disabled="!perm.tool.share.switch()"
                    v-model:loading="toolOperationLoading"
                    :api="SystemSharedToolApi"
                    :tool="tool"
                    @update="handleToolUpdate"
                  />
                  <el-divider direction="vertical" class="ml-1!" />
                </template>
                <template #action-dropdown>
                  <!-- 编辑共享工具 -->
                  <MkAction
                    v-if="perm.tool.share.edit()"
                    :label="t('common.actions.edit')"
                    icon="icon_edit_outlined"
                    @click="handleOpenEditTool(tool)"
                  />
                  <!-- 复制 -->
                  <CopyToolAction
                    v-if="perm.tool.share.copy()"
                    v-model:loading="toolOperationLoading"
                    :label="t('common.actions.duplicate')"
                    :api="SystemSharedToolApi"
                    :tool="tool"
                    @refresh="refreshTools"
                  />
                  <!-- 工作流 -->
                  <MkDropdownItem v-if="tool.tool_type === TOOL_TYPE.WORKFLOW" @click="handleOpenWorkflow(tool, $event)">
                    <template #icon><MkIcon name="icon_setting" /></template>
                    {{ t('tool.workflow.label') }}
                  </MkDropdownItem>
                  <!-- 启动参数 -->
                  <InitParamAction
                    v-if="(tool.init_field_list?.length ?? 0) > 0"
                    v-model:loading="toolOperationLoading"
                    :label="t('tool.initParams.title')"
                    :api="SystemSharedToolApi"
                    :tool="tool"
                    @update="handleToolUpdate"
                  />
                  <!-- 查看 MCP 配置 -->
                  <McpConfigAction
                    v-if="tool.tool_type === TOOL_TYPE.MCP"
                    v-model:loading="toolOperationLoading"
                    :label="t('resource.mcpConfig.title')"
                    :api="SystemSharedToolApi"
                    :tool="tool"
                  />
                  <!-- 授权工作空间 -->
                  <AuthorizedWorkspaceAction
                    v-if="perm.tool.share.authToWorkspace()"
                    :label="t('resource.workspaceAuthorization.title')"
                    :resource="tool"
                    :resource-type="RESOURCE_TYPE.TOOL"
                  />

                  <!-- 查看关联资源 -->
                  <RelatedResourcesToolAction
                    v-if="perm.tool.share.relateMap()"
                    :label="t('resource.relations.title')"
                    :api="SystemSharedRelatedResourcesApi"
                    :tool="tool"
                  />
                  <!-- 查看执行记录 -->
                  <ExecutionRecordToolAction
                    v-if="(tool.tool_type === TOOL_TYPE.CUSTOM || tool.tool_type === TOOL_TYPE.WORKFLOW) && perm.tool.share.record()"
                    :label="t('resource.executionRecords.view')"
                    :api="SystemSharedToolWorkflowApi"
                    :tool="tool"
                  />
                  <!-- 导出共享工具 -->
                  <ExportToolAction
                    v-if="!tool.template_id && perm.tool.share.export()"
                    v-model:loading="toolOperationLoading"
                    :label="t('common.actions.export')"
                    :api="SystemSharedToolApi"
                    :tool="tool"
                  />
                  <!-- 删除共享工具 -->
                  <DeleteToolAction
                    v-if="perm.tool.share.delete()"
                    v-model:loading="toolOperationLoading"
                    :label="t('common.actions.delete')"
                    :api="SystemSharedToolApi"
                    :tool="tool"
                    @delete="refreshTools"
                  />
                </template>
              </ToolCard>
            </template>
          </div>
          <template #empty><MkEmpty class="mt-24" /></template>
        </MkInfiniteScroll>
      </div>
    </template>
  </MkViewLayout>
  <EditToolForm ref="editToolFormRef" :api="SystemSharedToolApi" @update="handleToolUpdate" />
</template>
