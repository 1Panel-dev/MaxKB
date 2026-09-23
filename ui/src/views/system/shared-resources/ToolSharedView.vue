<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { useRouter } from 'vue-router'
import SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import CommonSystemApi from '@/api/admin/system/common'
import type { ParamsPage } from '@/api/admin/core/types'
import type { Dict, OptionItem, ToolItem, ToolType } from '@/api/types'
import { TOOL_TYPE } from '@/api/enums'
import { TOOL_TYPE_OPTIONS } from '@/constants'
import ToolCard from '@/views/tool/tool-card/ToolCard.vue'
import ButtonCreateTool from '@/views/tool/components/ButtonCreateTool.vue'
import { DeleteToolAction, EditToolAction, ExportToolAction, InitParamAction, McpConfigAction } from '@/views/tool/tool-card/action-dropdown'

const router = useRouter()

/* 共享工具查询 */
const toolsData = ref<ToolItem[]>([])
const toolQuery = ref<Dict<unknown>>()
const toolType = ref<ToolType | ''>('')
const creatorOptions = ref<OptionItem<string>[]>([])
const infiniteScrollRef = useTemplateRef<{ reset: () => Promise<void> }>('infiniteScrollRef')
const searchFields = computed(() => [
  { label: '名称', value: 'name' },
  { label: '创建者', value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
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
const editToolActionRefs: Record<string, InstanceType<typeof EditToolAction> | null> = {}

function handleOpenTool(tool: ToolItem, event: MouseEvent) {
  if (tool.tool_type === TOOL_TYPE.WORKFLOW) {
    const target = { name: 'system-shared-tool-workflow', params: { toolId: tool.id } }
    if (event.ctrlKey || event.metaKey) {
      window.open(router.resolve(target).href)
      return
    }
    return router.push(target)
  }
  editToolActionRefs[tool.id]?.handleOpenToolForm()
}

function handleToolUpdate(tool: ToolItem) {
  const toolIndex = toolsData.value.findIndex(({ id }) => id === tool.id)
  if (toolIndex >= 0) toolsData.value.splice(toolIndex, 1, tool)
}
</script>

<template>
  <MkViewLayout class="shared-tool-view">
    <template #default="{ Header }">
      <component :is="Header">
        <div class="flex-align-center gap-4">
          <h4>全部工具</h4>
          <el-divider direction="vertical" />
          <el-select v-model="toolType" class="w-30!" :empty-values="[null, undefined]" @change="refreshTools">
            <el-option v-for="option in TOOL_TYPE_OPTIONS" :key="option.value" :label="option.label" :value="option.value" />
          </el-select>
        </div>
        <div class="flex-align-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <!-- 创建共享工具 -->
          <ButtonCreateTool folder-id="default" :api="SystemSharedToolApi" @refresh="refreshTools" />
        </div>
      </component>
      <div v-loading="toolOperationLoading" class="min-h-0 flex-1">
        <MkInfiniteScroll ref="infiniteScrollRef" v-model="toolsData" :load="loadToolsPage">
          <div class="mk-resource-card-grid">
            <template v-for="tool in toolsData" :key="tool.id">
              <ToolCard
                v-model:loading="toolOperationLoading"
                :api="SystemSharedToolApi"
                :tool="tool"
                :shared="true"
                :store-tools="[]"
                @click="handleOpenTool(tool, $event)"
                @update="handleToolUpdate"
              >
                <template #action-dropdown>
                  <!-- 编辑共享工具 -->
                  <EditToolAction
                    :ref="
                      (instance) => {
                        if (instance) editToolActionRefs[tool.id] = instance as InstanceType<typeof EditToolAction>
                        else delete editToolActionRefs[tool.id]
                      }
                    "
                    label="编辑"
                    :api="SystemSharedToolApi"
                    :tool="tool"
                    @update="handleToolUpdate"
                  />
                  <!-- 配置启动参数 -->
                  <InitParamAction
                    v-if="(tool.init_field_list?.length ?? 0) > 0"
                    v-model:loading="toolOperationLoading"
                    label="启动参数"
                    :api="SystemSharedToolApi"
                    :tool="tool"
                    @update="handleToolUpdate"
                  />
                  <!-- 查看 MCP 配置 -->
                  <McpConfigAction
                    v-if="tool.tool_type === TOOL_TYPE.MCP"
                    v-model:loading="toolOperationLoading"
                    label="MCP 配置详情"
                    :api="SystemSharedToolApi"
                    :tool="tool"
                  />
                  <!-- 导出共享工具 -->
                  <ExportToolAction
                    v-if="!tool.template_id"
                    v-model:loading="toolOperationLoading"
                    label="导出"
                    :api="SystemSharedToolApi"
                    :tool="tool"
                  />
                  <!-- 删除共享工具 -->
                  <DeleteToolAction
                    v-model:loading="toolOperationLoading"
                    label="删除"
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
</template>
