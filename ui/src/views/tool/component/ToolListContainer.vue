<template>
  <ContentContainer>
    <template #header>
      <slot name="header"></slot>
    </template>
    <template #search>
      <div class="flex">
        <div class="flex-between complex-search">
          <el-select
            class="complex-search__left"
            v-model="search_type"
            style="width: 90px"
            @change="search_type_change"
          >
            <el-option :label="$t('common.creator')" value="create_user" />
            <el-option :label="$t('common.name')" value="name" />
          </el-select>
          <el-input
            v-if="search_type === 'name'"
            v-model="search_form.name"
            @change="searchHandle"
            :placeholder="$t('common.searchBar.placeholder')"
            style="width: 190px"
            clearable
          />
          <el-select
            v-else-if="search_type === 'create_user'"
            v-model="search_form.create_user"
            @change="searchHandle"
            filterable
            clearable
            style="width: 190px"
          >
            <el-option v-for="u in user_options" :key="u.id" :value="u.id" :label="u.nick_name" />
          </el-select>
        </div>
        <span class="ml-8" v-if="!isShared && (permissionPrecise.batchMove() || permissionPrecise.batchDelete())">
          <el-button @click="batchSelectedHandle(true)" v-if="isBatch === false">
            <AppIcon iconName="app-batch-delete" class="mr-4" />
            {{ $t('views.paragraph.setting.batchSelected') }}
          </el-button>
          <el-button @click="batchSelectedHandle(false)" v-if="isBatch === true">
            <AppIcon iconName="app-batch-delete" class="mr-4" />
            {{ $t('views.paragraph.setting.cancelSelected') }}
          </el-button>
        </span>
        <div v-if="isBatch === false">
          <span class="ml-8" v-if="!isShared && permissionPrecise.create()">
            <el-button @click="openToolStoreDialog()">
              <AppIcon iconName="app-tool-store" class="mr-4" />
              {{ $t('views.tool.toolStore.title') }}
            </el-button>
          </span>

          <el-dropdown trigger="click">
            <el-button type="primary" class="ml-8" v-if="!isShared && permissionPrecise.create()">
              {{ $t('common.create') }}
              <el-icon class="el-icon--right">
                <arrow-down />
              </el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu class="create-dropdown">
                <el-dropdown-item @click="openCreateDialog()">
                  <div class="flex align-center">
                    <el-avatar class="avatar-green" shape="square" :size="32">
                      <img src="@/assets/tool/icon_tool.svg" style="width: 58%" alt="" />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">{{ $t('views.tool.title') }}</div>
                    </div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item @click="openCreateWorkflowDialog()">
                  <div class="flex align-center">
                    <el-avatar class="avatar-green mt-4" shape="square" :size="32">
                      <img src="@/assets/workflow/logo_workflow.svg" style="width: 60%" alt="" />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">{{ $t('workflow.workflow') }}</div>
                    </div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item @click="openCreateSkillDialog()">
                  <div class="flex align-center">
                    <el-avatar shape="square" :size="32">
                      <img src="@/assets/tool/icon_skill.svg" style="width: 58%" alt="" />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">Skills</div>
                    </div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item @click="openCreateMcpDialog()">
                  <div class="flex align-center">
                    <el-avatar shape="square" :size="32">
                      <img src="@/assets/tool/icon_mcp.svg" style="width: 75%" alt="" />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">MCP</div>
                    </div>
                  </div>
                </el-dropdown-item>

                <el-dropdown-item @click="openCreateDataSourceDialog()">
                  <div class="flex align-center">
                    <el-avatar class="avatar-purple" shape="square" :size="32">
                      <img src="@/assets/tool/icon_datasource.svg" style="width: 58%" alt="" />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">{{ $t('views.tool.dataSource.title') }}</div>
                    </div>
                  </div>
                </el-dropdown-item>
                <el-upload
                  ref="elUploadRef"
                  :file-list="[]"
                  action="#"
                  multiple
                  :auto-upload="false"
                  :show-file-list="false"
                  :limit="1"
                  :on-change="(file: any, fileList: any) => importTool(file)"
                  class="import-button"
                >
                  <el-dropdown-item v-if="permissionPrecise.import()">
                    <div class="flex align-center w-full">
                      <el-avatar shape="square" :size="32" style="background: none">
                        <img src="@/assets/icon_import.svg" alt="" />
                      </el-avatar>
                      <div class="pre-wrap ml-8">
                        <div class="lighter">{{ $t('common.importCreate') }}</div>
                      </div>
                    </div>
                  </el-dropdown-item>
                </el-upload>
                <el-dropdown-item @click="openCreateFolder" divided v-if="apiType === 'workspace'">
                  <div class="flex align-center">
                    <AppIcon iconName="app-folder" style="font-size: 32px"></AppIcon>

                    <div class="pre-wrap ml-4">
                      <div class="lighter">
                        {{ $t('components.folder.addFolder') }}
                      </div>
                    </div>
                  </div>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </template>

    <div
      v-loading.fullscreen.lock="paginationConfig.current_page === 1 && loading"
      style="max-height: calc(100vh - 120px)"
    >
      <InfiniteScroll
        :size="tool.toolList.length"
        :total="paginationConfig.total"
        :page_size="paginationConfig.page_size"
        v-model:current_page="paginationConfig.current_page"
        @load="getList"
        :loading="loading"
      >
        <el-checkbox-group v-model="multipleSelection" @change="handleCheckedChatChange">
          <el-row v-if="tool.toolList.length > 0" :gutter="15" class="w-full">
            <template v-for="(item, index) in tool.toolList" :key="index">
              <el-col :xs="24" :sm="12" :md="12" :lg="8" :xl="6" class="mb-16">
                <CardBox
                  :title="item.name"
                  :description="item.desc"
                  class="cursor"
                  :class="[multipleSelection.includes(item.id) ? 'border-active' : '']"
                  @click.stop="openEditDialog(item)"
                  :disabled="!permissionPrecise.edit(item.id) || isBatch"
                >
                  <template #icon>
                    <el-avatar v-if="item?.icon" shape="square" :size="32" style="background: none">
                      <img :src="resetUrl(item?.icon)" alt="" />
                    </el-avatar>
                    <ToolIcon v-else :size="32" :type="item?.tool_type" />
                  </template>
                  <template #title>
                    <div class="flex align-center">
                      <span class="ellipsis-1" :title="item.name">
                        {{ item.name }}
                      </span>
                      <el-tag
                        v-if="item.version"
                        class="ml-4"
                        size="small"
                        type="info"
                        effect="plain"
                      >
                        {{ item.version }}
                      </el-tag>
                    </div>
                  </template>
                  <template #subTitle>
                    <el-text class="color-secondary lighter flex align-center" size="small">
                      <span
                        :title="i18n_name(item.nick_name)"
                        class="ellipsis"
                        style="max-width: 90px"
                      >
                        {{ i18n_name(item.nick_name) }}
                      </span>
                      <span class="ml-4 mr-4"> {{ $t('common.createdIn') }}</span>
                      <span> {{ dateFormat(item.create_time) }}</span>
                    </el-text>
                  </template>
                  <template #tag="{ hoverShow }">
                    <el-checkbox :value="item.id" v-if="isBatch" @change="checkboxChange(item)" />
                    <div v-else>
                      <el-tag v-if="isShared" size="small" type="info" class="info-tag">
                        {{ t('views.shared.title') }}
                      </el-tag>
                      <el-tooltip
                        effect="dark"
                        :content="$t('views.tool.updatedVersion')"
                        v-if="
                          showUpdateStoreTool(item) && !isShared && permissionPrecise.edit(item.id)
                        "
                      >
                        <el-button text @click.stop="updateStoreTool(item)">
                          <el-icon v-if="hoverShow">
                            <Refresh />
                          </el-icon>
                          <div v-else class="dot-success"></div>
                        </el-button>
                      </el-tooltip>
                    </div>
                  </template>

                  <template #footer>
                    <div v-if="item.is_active" class="flex align-center">
                      <el-icon class="color-success mr-8" style="font-size: 16px">
                        <SuccessFilled />
                      </el-icon>
                      <span class="color-secondary">
                        {{ $t('common.status.enabled') }}
                      </span>
                    </div>
                    <div v-else class="flex align-center">
                      <AppIcon iconName="app-disabled" class="color-secondary mr-8"></AppIcon>
                      <span class="color-secondary">
                        {{ $t('common.status.disabled') }}
                      </span>
                    </div>
                  </template>
                  <template #mouseEnter>
                    <div @click.stop v-if="!isShared && MoreFieldPermission(item.id)">
                      <el-switch
                        v-model="item.is_active"
                        :before-change="() => changeState(item)"
                        size="small"
                        class="mr-4"
                        v-if="permissionPrecise.switch(item.id)"
                      />
                      <el-divider direction="vertical" />
                      <el-dropdown trigger="click">
                        <el-button text @click.stop>
                          <AppIcon iconName="app-more"></AppIcon>
                        </el-button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item
                              v-if="item.tool_type === 'MCP'"
                              @click.stop="showMcpConfig(item)"
                            >
                              <AppIcon iconName="app-operate-log" class="color-secondary"></AppIcon>
                              {{ $t('views.tool.mcp.mcpConfig') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              v-if="item.template_id && permissionPrecise.edit(item.id)"
                              @click.stop="addInternalTool(item, true)"
                            >
                              <AppIcon iconName="app-edit" class="color-secondary"></AppIcon>
                              {{ $t('common.edit') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              v-else-if="
                                item.tool_type === 'WORKFLOW' && permissionPrecise.edit(item.id)
                              "
                              @click.stop="openCreateWorkflowDialog(item)"
                            >
                              <AppIcon iconName="app-edit" class="color-secondary"></AppIcon>
                              {{ $t('common.edit') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              v-else-if="permissionPrecise.edit(item.id)"
                              @click.stop="openEditDialog(item)"
                            >
                              <AppIcon iconName="app-edit" class="color-secondary"></AppIcon>
                              {{ $t('common.edit') }}
                            </el-dropdown-item>

                            <el-dropdown-item
                              v-if="item.tool_type === 'WORKFLOW'"
                              @click.stop="toWorkflow(item)"
                            >
                              <AppIcon iconName="app-workflow" class="color-secondary"></AppIcon>
                              {{ $t('workflow.workflow') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              v-if="!item.template_id && permissionPrecise.copy(item.id)"
                              @click.stop="copyTool(item)"
                            >
                              <AppIcon iconName="app-copy" class="color-secondary"></AppIcon>
                              {{ $t('common.copy') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              v-if="
                                item.init_field_list?.length > 0 && permissionPrecise.edit(item.id)
                              "
                              @click.stop="configInitParams(item)"
                            >
                              <AppIcon iconName="app-operation" class="color-secondary"></AppIcon>
                              {{ $t('common.param.initParam') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              @click.stop="openAuthorization(item)"
                              v-if="apiType === 'workspace' && permissionPrecise.auth(item.id)"
                            >
                              <AppIcon
                                iconName="app-resource-authorization"
                                class="color-secondary"
                              ></AppIcon>
                              {{ $t('views.system.resourceAuthorization.title') }}
                            </el-dropdown-item>

                            <el-dropdown-item
                              @click.stop="openTriggerDrawer(item)"
                              v-if="
                                ['workspace', 'systemManage'].includes(apiType) &&
                                (item.tool_type === 'CUSTOM' || item.tool_type === 'WORKFLOW') &&
                                permissionPrecise.trigger_read(item.id)
                              "
                            >
                              <AppIcon iconName="app-trigger" class="color-secondary"></AppIcon>
                              {{ $t('views.trigger.title') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              text
                              @click.stop="openResourceMappingDrawer(item)"
                              v-if="permissionPrecise.relate_map(item.id)"
                            >
                              <AppIcon
                                iconName="app-resource-mapping"
                                class="color-secondary"
                              ></AppIcon>
                              {{ $t('views.system.resourceMapping.title') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              text
                              @click.stop="openToolRecordDrawer(item)"
                              v-if="
                                (item.tool_type === 'CUSTOM' || item.tool_type === 'WORKFLOW') &&
                                permissionPrecise.record(item.id)
                              "
                            >
                              <AppIcon
                                iconName="app-schedule-report"
                                class="color-secondary"
                              ></AppIcon>
                              {{ $t('common.ExecutionRecord.subTitle') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              @click.stop="openMoveToDialog(item)"
                              v-if="permissionPrecise.copy(item.id) && apiType === 'workspace'"
                            >
                              <AppIcon iconName="app-migrate" class="color-secondary"></AppIcon>
                              {{ $t('common.moveTo') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              v-if="isSystemShare"
                              @click.stop="openAuthorizedWorkspaceDialog(item)"
                            >
                              <AppIcon iconName="app-lock" class="color-secondary"></AppIcon>
                              {{ $t('views.shared.authorized_workspace') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              v-if="!item.template_id && permissionPrecise.export(item.id)"
                              @click.stop="exportTool(item)"
                            >
                              <AppIcon iconName="app-export" class="color-secondary"></AppIcon>
                              {{ $t('common.export') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              v-if="permissionPrecise.delete(item.id)"
                              divided
                              @click.stop="deleteTool(item)"
                            >
                              <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
                              {{ $t('common.delete') }}
                            </el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </div>
                  </template>
                </CardBox>
              </el-col>
            </template>
          </el-row>
          <el-empty :description="$t('common.noData')" v-else />
        </el-checkbox-group>
      </InfiniteScroll>
    </div>
    <!-- 批量操作拦 -->
    <div class="mul-operation border-t w-full flex align-center" v-if="isBatch">
      <el-checkbox
        v-model="checkAll"
        :indeterminate="isIndeterminate"
        @change="handleCheckAllChange"
      >
        {{ $t('common.allCheck') }}
      </el-checkbox>
      <el-button
        class="ml-16"
        :disabled="multipleSelection.length === 0"
        @click="openMoveToDialog()"
        v-if="permissionPrecise.batchMove()"
      >
        {{ $t('common.moveTo') }}
      </el-button>

      <el-button
        :disabled="multipleSelection.length === 0"
        @click="deleteMulTool"
        v-if="permissionPrecise.batchDelete()"
      >
        {{ $t('common.delete') }}
      </el-button>
      <span class="color-secondary ml-24 mr-16">
        {{ $t('common.selected') }} {{ multipleSelection.length }}
        {{ $t('views.document.items') }}
      </span>
      <span class="color-secondary mr-16">
        {{ $t('common.total') }} {{ paginationConfig.total }}
        {{ $t('views.document.items') }}
      </span>
      <el-button link type="primary" @click="batchSelectedHandle(false)">
        {{ $t('views.paragraph.setting.cancelSelected') }}
      </el-button>
    </div>
    <InitParamDrawer ref="InitParamDrawerRef" @refresh="refresh" />
    <ToolFormDrawer ref="ToolFormDrawerRef" @refresh="refresh" :title="ToolDrawertitle" />
    <McpToolFormDrawer ref="McpToolFormDrawerRef" @refresh="refresh" :title="McpToolDrawertitle" />
    <SkillToolFormDrawer
      ref="SkillToolFormDrawerRef"
      @refresh="refresh"
      :title="SkillToolDrawertitle"
    />
    <DataSourceToolFormDrawer
      ref="DataSourceToolFormDrawerRef"
      @refresh="refresh"
      :title="DataSourceToolDrawertitle"
    />
    <CreateFolderDialog ref="CreateFolderDialogRef" v-if="!isShared" @refresh="refreshFolder" />
    <ToolStoreDialog ref="toolStoreDialogRef" :api-type="apiType" @refresh="refresh" />
    <AddInternalToolDialog ref="AddInternalToolDialogRef" @refresh="confirmAddInternalTool" />
    <McpToolConfigDialog ref="McpToolConfigDialogRef" @refresh="refresh" />
    <AuthorizedWorkspace
      ref="AuthorizedWorkspaceDialogRef"
      v-if="isSystemShare"
    ></AuthorizedWorkspace>
    <MoveToDialog
      ref="MoveToDialogRef"
      :source="SourceTypeEnum.TOOL"
      @refresh="refreshToolList"
      v-if="apiType === 'workspace'"
    />
    <ResourceAuthorizationDrawer
      :type="SourceTypeEnum.TOOL"
      ref="ResourceAuthorizationDrawerRef"
      v-if="apiType === 'workspace'"
    />
    <ToolStoreDescDrawer ref="toolStoreDescDrawerRef" />
    <ResourceMappingDrawer ref="resourceMappingDrawerRef"></ResourceMappingDrawer>
    <ResourceTriggerDrawer
      ref="resourceTriggerDrawerRef"
      :source="SourceTypeEnum.TOOL"
    ></ResourceTriggerDrawer>
    <ExecutionRecordDrawer ref="toolRecordDrawerRef" />
    <WorkflowFormDialog
      ref="workflowFormDialogRef"
      :title="workflowFormDialogtitle"
    ></WorkflowFormDialog>
  </ContentContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed, watch } from 'vue'
import { cloneDeep } from 'lodash'
import { useRoute, onBeforeRouteLeave, useRouter } from 'vue-router'
import type { CheckboxValueType } from 'element-plus'
import InitParamDrawer from '@/views/tool/component/InitParamDrawer.vue'
import ToolFormDrawer from '@/views/tool/ToolFormDrawer.vue'
import McpToolFormDrawer from '@/views/tool/McpToolFormDrawer.vue'
import SkillToolFormDrawer from '@/views/tool/SkillToolFormDrawer.vue'
import DataSourceToolFormDrawer from '@/views/tool/DataSourceToolFormDrawer.vue'
import CreateFolderDialog from '@/components/folder-tree/CreateFolderDialog.vue'
import AuthorizedWorkspace from '@/views/system-shared/AuthorizedWorkspaceDialog.vue'
import ToolStoreDialog from '@/views/tool/tool-store/ToolStoreDialog.vue'
import AddInternalToolDialog from '@/views/tool/tool-store/AddInternalToolDialog.vue'
import MoveToDialog from '@/components/folder-tree/MoveToDialog.vue'
import ResourceAuthorizationDrawer from '@/components/resource-authorization-drawer/index.vue'
import McpToolConfigDialog from '@/views/tool/component/McpToolConfigDialog.vue'
import ResourceTriggerDrawer from '@/views/trigger/ResourceTriggerDrawer.vue'
import ToolStoreDescDrawer from '@/views/tool/component/ToolStoreDescDrawer.vue'
import ResourceMappingDrawer from '@/components/resource_mapping/index.vue'
import WorkflowFormDialog from '../WorkflowFormDialog.vue'
import ExecutionRecordDrawer from '@/views/tool-workflow/execution-record/ExecutionRecordDrawer.vue'
import ToolStoreApi from '@/api/tool/store.ts'
import { resetUrl, i18n_name } from '@/utils/common'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import { SourceTypeEnum } from '@/enums/common'
import { dateFormat } from '@/utils/time'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import permissionMap from '@/permission'
import useStore from '@/stores'
import { t } from '@/locales'

import bus from '@/bus'
const router = useRouter()
const route = useRoute()

const { folder, user, tool } = useStore()
onBeforeRouteLeave((to, from) => {
  tool.setToolList([])
})
const emit = defineEmits(['refreshFolder'])

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const isShared = computed(() => {
  return folder.currentFolder.id === 'share'
})
const isSystemShare = computed(() => {
  return apiType.value === 'systemShare'
})

const permissionPrecise = computed(() => {
  return permissionMap['tool'][apiType.value]
})

const MoreFieldPermission = (id: any) => {
  return (
    permissionPrecise.value.edit(id) ||
    permissionPrecise.value.export(id) ||
    permissionPrecise.value.delete(id) ||
    permissionPrecise.value.auth(id) ||
    permissionPrecise.value.relate_map(id) ||
    permissionPrecise.value.trigger_read(id) ||
    permissionPrecise.value.record(id) ||
    isSystemShare.value
  )
}

const resourceTriggerDrawerRef = ref<InstanceType<typeof ResourceTriggerDrawer>>()
const openTriggerDrawer = (data: any) => {
  resourceTriggerDrawerRef.value?.open(data)
}

const resourceMappingDrawerRef = ref<InstanceType<typeof ResourceMappingDrawer>>()
const openResourceMappingDrawer = (tool: any) => {
  resourceMappingDrawerRef.value?.open('TOOL', tool)
}

const ResourceAuthorizationDrawerRef = ref()

function openAuthorization(item: any) {
  ResourceAuthorizationDrawerRef.value.open(item.id)
}

const toolRecordDrawerRef = ref<InstanceType<typeof ExecutionRecordDrawer>>()
const openToolRecordDrawer = (data: any) => {
  toolRecordDrawerRef.value?.open(data)
}

const InitParamDrawerRef = ref()
const search_type = ref('name')
const search_form = ref<any>({
  name: '',
  create_user: '',
})
const user_options = ref<any[]>([])

const loading = ref(false)
const changeStateloading = ref(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0,
})

const search_type_change = () => {
  search_form.value = { name: '', create_user: '' }
}
const ToolFormDrawerRef = ref()
const McpToolFormDrawerRef = ref()
const SkillToolFormDrawerRef = ref()
const DataSourceToolFormDrawerRef = ref()
const ToolDrawertitle = ref('')
const McpToolDrawertitle = ref('')
const SkillToolDrawertitle = ref('')
const DataSourceToolDrawertitle = ref('')

// 批量操作
const isBatch = ref(false)
const multipleSelection = ref<any[]>([])
const checkAll = ref(false)
const isIndeterminate = computed(() => {
  return multipleSelection.value.length > 0 && multipleSelection.value.length < tool.toolList.length
})
function batchSelectedHandle(bool: boolean) {
  isBatch.value = bool
  multipleSelection.value = []
  checkAll.value = false
}

const handleCheckAllChange = (val: CheckboxValueType) => {
  multipleSelection.value = val ? tool.toolList.map((v) => v.id) : []
  checkAll.value = val as boolean
}
const handleCheckedChatChange = (value: CheckboxValueType[]) => {
  const checkedCount = value.length
  checkAll.value = checkedCount === tool.toolList.length
}

const checkboxChange = (data?: any) => {
  const index = multipleSelection.value.indexOf(data?.id)
  if (index === -1) {
    multipleSelection.value.push(data?.id)
  } else {
    multipleSelection.value.splice(index, 1)
  }
  checkAll.value = multipleSelection.value.length === tool.toolList.length
}

function deleteMulTool() {
  MsgConfirm(
    `${t('views.document.delete.confirmTitle1')} ${multipleSelection.value.length} ${t('views.tool.delete.confirmTitle2')}`,
    t('views.paragraph.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      loadSharedApi({ type: 'tool', systemType: apiType.value })
        .delMulTool(multipleSelection.value, loading)
        .then(() => {
          batchSelectedHandle(false)
          paginationConfig.current_page = 1
          tool.setToolList([])
          getList()
          MsgSuccess(t('views.document.delete.successMessage'))
        })
    })
    .catch(() => {})
}

function openEditDialog(data?: any) {
  if (isBatch.value) {
    const index = multipleSelection.value.indexOf(data?.id)
    if (index === -1) {
      multipleSelection.value.push(data?.id)
    } else {
      multipleSelection.value.splice(index, 1)
    }
    checkAll.value = multipleSelection.value.length === tool.toolList.length
    return
  }
  // 有template_id的不允许编辑，是模板转换来的
  if (data?.template_id) {
    return
  }
  // 共享过来的工具不让编辑
  if (isShared.value) {
    return
  }
  if (data) {
    bus.emit('select_node', data.folder_id)
  }
  // 有版本号的展示readme，是商店更新过来的
  if (data?.version) {
    let readMe = ''
    storeTools.value
      .filter((item) => item.id === data.template_id)
      .forEach((item) => {
        readMe = item.readMe
      })
    toolStoreDescDrawerRef.value?.open(readMe, data)
    return
  }

  // mcp工具
  if (data?.tool_type === 'MCP') {
    openCreateMcpDialog(data)
    return
  }
  // 数据源工具
  if (data?.tool_type === 'DATA_SOURCE') {
    openCreateDataSourceDialog(data)
    return
  }
  // 技能
  if (data?.tool_type === 'SKILL') {
    openCreateSkillDialog(data)
    return
  }
  // 工作流
  if (data?.tool_type === 'WORKFLOW') {
    toWorkflow(data)
    return
  }
  ToolDrawertitle.value = t('views.tool.editTool')
  if (data) {
    loadSharedApi({ type: 'tool', systemType: apiType.value })
      .getToolById(data?.id, loading)
      .then((res: any) => {
        ToolFormDrawerRef.value.open(res.data)
      })
  }
}

const MoveToDialogRef = ref()

function openMoveToDialog(data?: any) {
  let obj
  if (isBatch.value) {
    obj = {
      id_list: multipleSelection.value,
    }
  } else {
    obj = {
      id: data.id,
      folder_id: data.folder,
    }
  }

  MoveToDialogRef.value?.open(obj)
}

function refreshToolList(row: any) {
  if (row) {
    // 不是根目录才会移除
    if (folder.currentFolder?.parent_id) {
      const list = cloneDeep(tool.toolList)
      const index = list.findIndex((v) => v.id === row.id)
      list.splice(index, 1)
      tool.setToolList(list)
    }
  } else {
    batchSelectedHandle(false)
    paginationConfig.current_page = 1
    tool.setToolList([])
    getList()
  }
}

const AuthorizedWorkspaceDialogRef = ref()

function openAuthorizedWorkspaceDialog(row: any) {
  if (AuthorizedWorkspaceDialogRef.value) {
    AuthorizedWorkspaceDialogRef.value.open(row, 'Tool')
  }
}

const toolStoreDescDrawerRef = ref<InstanceType<typeof ToolStoreDescDrawer>>()

function openCreateDialog() {
  ToolDrawertitle.value = t('views.tool.createTool')
  ToolFormDrawerRef.value.open()
}

function openCreateMcpDialog(data?: any) {
  // 有template_id的不允许编辑，是模板转换来的
  if (data?.template_id) {
    return
  }
  // 共享过来的工具不让编辑
  if (isShared.value) {
    return
  }
  McpToolDrawertitle.value = data
    ? t('views.tool.mcp.editMcpTool')
    : t('views.tool.mcp.createMcpTool')
  if (data) {
    loadSharedApi({ type: 'tool', systemType: apiType.value })
      .getToolById(data?.id, loading)
      .then((res: any) => {
        McpToolFormDrawerRef.value.open(res.data)
      })
  } else {
    McpToolFormDrawerRef.value.open(data)
  }
}

function openCreateSkillDialog(data?: any) {
  // 有版本号的展示readme，是商店更新过来的
  if (data?.version) {
    let readMe = ''
    storeTools.value
      .filter((item) => item.id === data.template_id)
      .forEach((item) => {
        readMe = item.readMe
      })
    toolStoreDescDrawerRef.value?.open(readMe, data)
    return
  }
  // 有template_id的不允许编辑，是模板转换来的
  if (data?.template_id) {
    return
  }
  // 共享过来的工具不让编辑
  if (isShared.value) {
    return
  }
  SkillToolDrawertitle.value = data
    ? t('views.tool.skill.editSkillTool')
    : t('views.tool.skill.createSkillTool')
  if (data) {
    loadSharedApi({ type: 'tool', systemType: apiType.value })
      .getToolById(data?.id, loading)
      .then((res: any) => {
        SkillToolFormDrawerRef.value.open(res.data)
      })
  } else {
    SkillToolFormDrawerRef.value.open(data)
  }
}

function toWorkflow(data: any) {
  const folderId = data.scope === 'SHARED' ? 'shared' : data.folder_id
  router.push({ name: 'ToolWorkflow', params: { id: data.id, folderId: folderId } })
}

const workflowFormDialogRef = ref<InstanceType<typeof WorkflowFormDialog>>()
const workflowFormDialogtitle = ref('')
const openCreateWorkflowDialog = (data?: any) => {
  // 有template_id的不允许编辑，是模板转换来的
  if (data?.template_id) {
    return
  }
  // 共享过来的工具不让编辑
  if (isShared.value) {
    return
  }
  workflowFormDialogtitle.value = data
    ? t('common.edit')
    : t('views.tool.toolWorkflow.creatToolWorkflow')
  if (data) {
    loadSharedApi({ type: 'tool', systemType: apiType.value })
      .getToolById(data?.id, loading)
      .then((res: any) => {
        toWorkflow( res.data)
        workflowFormDialogRef.value?.open(res.data)
      })
  } else {
    workflowFormDialogRef.value?.open(data)
  }
}
function openCreateDataSourceDialog(data?: any) {
  // 有template_id的不允许编辑，是模板转换来的
  if (data?.template_id) {
    return
  }
  // 共享过来的工具不让编辑
  if (isShared.value) {
    return
  }
  DataSourceToolDrawertitle.value = data
    ? t('views.tool.dataSource.editDataSource')
    : t('views.tool.dataSource.createDataSource')
  if (data) {
    loadSharedApi({ type: 'tool', systemType: apiType.value })
      .getToolById(data?.id, loading)
      .then((res: any) => {
        DataSourceToolFormDrawerRef.value.open(res.data)
      })
  } else {
    DataSourceToolFormDrawerRef.value.open(data)
  }
}

async function changeState(row: any) {
  if (row.is_active) {
    MsgConfirm(
      `${t('views.tool.disabled.confirmTitle')}${row.name} ?`,
      t('views.tool.disabled.confirmMessage'),
      {
        confirmButtonText: t('common.status.disable'),
        confirmButtonClass: 'danger',
      },
    ).then(() => {
      const obj = {
        is_active: !row.is_active,
      }
      loadSharedApi({ type: 'tool', systemType: apiType.value })
        .putTool(row.id, obj, changeStateloading)
        .then(() => {
          const list = cloneDeep(tool.toolList)
          const index = list.findIndex((v) => v.id === row.id)
          list[index].is_active = !row.is_active
          tool.setToolList(list)
          return true
        })
        .catch(() => {
          return false
        })
    })
  } else {
    const res = await loadSharedApi({ type: 'tool', systemType: apiType.value }).getToolById(
      row.id,
      changeStateloading,
    )
    if (row.tool_type === 'WORKFLOW' && !res.data.is_publish) {
      MsgConfirm(t('common.tip'), t('views.tool.toolWorkflow.toActiveTip')).then(() => {
        toWorkflow(row)
      })
      return
    }
    if (
      (!res.data.init_params || Object.keys(res.data.init_params).length === 0) &&
      res.data.init_field_list &&
      res.data.init_field_list.length > 0 &&
      res.data.init_field_list.filter((item: any) => item.default_value && item.show_default_value)
        .length !== res.data.init_field_list.length
    ) {
      InitParamDrawerRef.value.open(res.data, !row.is_active)
      return false
    }
    const obj = {
      is_active: !row.is_active,
    }
    loadSharedApi({ type: 'tool', systemType: apiType.value })
      .putTool(row.id, obj, changeStateloading)
      .then(() => {
        const list = cloneDeep(tool.toolList)
        const index = list.findIndex((v) => v.id === row.id)
        list[index].is_active = !row.is_active
        tool.setToolList(list)
        return true
      })
      .catch(() => {
        return false
      })
  }
}

async function copyTool(row: any) {
  // mcp工具
  if (row?.tool_type === 'MCP') {
    bus.emit('select_node', row.folder_id)
    await copyMcpTool(row)
    return
  }
  // 数据源工具
  if (row?.tool_type === 'DATA_SOURCE') {
    bus.emit('select_node', row.folder_id)
    await copyDataSource(row)
    return
  }
  // 技能
  if (row?.tool_type === 'SKILL') {
    bus.emit('select_node', row.folder_id)
    await copySkillTool(row)
    return
  }
  ToolDrawertitle.value = t('views.tool.copyTool')
  const res = await loadSharedApi({ type: 'tool', systemType: apiType.value }).getToolById(
    row.id,
    changeStateloading,
  )
  const obj = cloneDeep(res.data)
  delete obj['id']
  obj['name'] = obj['name'] + `  ${t('common.copyTitle')}`
  ToolFormDrawerRef.value.open(obj)
}

async function copyMcpTool(row: any) {
  McpToolDrawertitle.value = t('views.tool.mcp.copyMcpTool')
  const res = await loadSharedApi({ type: 'tool', systemType: apiType.value }).getToolById(
    row.id,
    changeStateloading,
  )
  const obj = cloneDeep(res.data)
  delete obj['id']
  obj['name'] = obj['name'] + `  ${t('common.copyTitle')}`
  McpToolFormDrawerRef.value.open(obj)
}

async function copyDataSource(row: any) {
  DataSourceToolDrawertitle.value = t('views.tool.dataSource.copyDataSource')
  const res = await loadSharedApi({ type: 'tool', systemType: apiType.value }).getToolById(
    row.id,
    changeStateloading,
  )
  const obj = cloneDeep(res.data)
  delete obj['id']
  obj['name'] = obj['name'] + `  ${t('common.copyTitle')}`
  DataSourceToolFormDrawerRef.value.open(obj)
}

async function copySkillTool(row: any) {
  SkillToolDrawertitle.value = t('views.tool.skill.copySkillTool')
  const res = await loadSharedApi({ type: 'tool', systemType: apiType.value }).getToolById(
    row.id,
    changeStateloading,
  )
  const obj = cloneDeep(res.data)
  delete obj['id']
  obj['name'] = obj['name'] + `  ${t('common.copyTitle')}`
  SkillToolFormDrawerRef.value.open(obj)
}

function exportTool(row: any) {
  loadSharedApi({ type: 'tool', systemType: apiType.value })
    .exportTool(row.id, row.name, loading)
    .catch((e: any) => {
      if (e.response.status !== 403) {
        e.response.data.text().then((res: string) => {
          MsgError(`${t('views.application.tip.ExportError')}:${JSON.parse(res).message}`)
        })
      }
    })
}

function deleteTool(row: any) {
  MsgConfirm(
    `${t('views.tool.delete.confirmTitle')}：${row.name} ?`,
    row.resource_count > 0 ? t('views.tool.delete.resourceCountMessage', row.resource_count) : '',
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      loadSharedApi({ type: 'tool', systemType: apiType.value })
        .delTool(row.id, loading)
        .then(() => {
          const list = cloneDeep(tool.toolList)
          const index = list.findIndex((v) => v.id === row.id)
          list.splice(index, 1)
          tool.setToolList(list)
          MsgSuccess(t('common.deleteSuccess'))
        })
    })
    .catch(() => {})
}

function configInitParams(item: any) {
  loadSharedApi({ type: 'tool', systemType: apiType.value })
    .getToolById(item?.id, changeStateloading)
    .then((res: any) => {
      InitParamDrawerRef.value.open(res.data)
    })
}

const toolStoreDialogRef = ref<InstanceType<typeof ToolStoreDialog>>()

function openToolStoreDialog() {
  toolStoreDialogRef.value?.open(folder.currentFolder.id)
}

const AddInternalToolDialogRef = ref<InstanceType<typeof AddInternalToolDialog>>()

function addInternalTool(data?: any, isEdit?: boolean) {
  AddInternalToolDialogRef.value?.open(data, isEdit)
}

function confirmAddInternalTool(data?: any, isEdit?: boolean) {
  if (isEdit) {
    loadSharedApi({ type: 'tool', systemType: apiType.value })
      .putTool(data?.id as string, { name: data.name }, loading)
      .then((res: any) => {
        MsgSuccess(t('common.saveSuccess'))
        refresh()
      })
  }
}

const storeTools = ref<any[]>([])

function getStoreToolList() {
  ToolStoreApi.getStoreToolList({ name: '' }, loading).then((res: any) => {
    storeTools.value = res.data.apps
  })
}

function showUpdateStoreTool(item: any) {
  for (const tool of storeTools.value) {
    if (tool.id === item.template_id && tool.version !== item.version) {
      item.downloadUrl = tool.downloadUrl
      item.downloadCallbackUrl = tool.downloadCallbackUrl
      item.icon = tool.icon
      item.versions = tool.versions
      item.label = tool.label
      return true
    }
  }
}

function updateStoreTool(item: any) {
  MsgConfirm(
    t('views.tool.toolStore.confirmTip') + item.name,
    t('views.tool.toolStore.updateStoreToolMessage'),
    {
      cancelButtonText: t('common.cancel'),
      confirmButtonText: t('common.confirm'),
    },
  )
    .then(() => {
      const obj = {
        download_url: item.downloadUrl,
        download_callback_url: item.downloadCallbackUrl,
        icon: item.icon,
        versions: item.versions,
        label: item.label,
      }
      loadSharedApi({ type: 'tool', systemType: apiType.value })
        .updateStoreTool(item.id, obj, loading)
        .then(async (res: any) => {
          if (res?.data) {
            tool.setToolList([])
            return user.profile().then(() => {
              getList()
            })
          }
        })
    })
    .catch(() => {})
}

const elUploadRef = ref()

function importTool(file: any) {
  const formData = new FormData()
  formData.append('file', file.raw, file.name)
  formData.append('folder_id', folder.currentFolder.id || user.getWorkspaceId())
  elUploadRef.value.clearFiles()
  loadSharedApi({ type: 'tool', systemType: apiType.value })
    .postImportTool(formData, loading)
    .then(async (res: any) => {
      if (res?.data) {
        tool.setToolList([])
        return user.profile().then(() => {
          getList()
        })
      }
    })
    .catch((e: any) => {
      if (e.code === 400) {
        MsgConfirm(t('common.tip'), t('views.application.tip.professionalMessage'), {
          cancelButtonText: t('common.confirm'),
          confirmButtonText: t('common.professional'),
        }).then(() => {
          window.open('https://maxkb.cn/pricing.html', '_blank')
        })
      }
    })
}

const McpToolConfigDialogRef = ref()

function showMcpConfig(item: any) {
  loadSharedApi({ type: 'tool', systemType: apiType.value })
    .getToolById(item?.id, loading)
    .then((res: any) => {
      McpToolConfigDialogRef.value.open(res.data)
    })
}

function refresh(data?: any) {
  if (data) {
    const list = cloneDeep(tool.toolList)
    const index = list.findIndex((v) => v.id === data.id)
    list.splice(index, 1, data)
    tool.setToolList(list)
  } else {
    paginationConfig.total = 0
    paginationConfig.current_page = 1
    tool.setToolList([])
    getList()
  }
}

// 文件夹相关
const CreateFolderDialogRef = ref()

function openCreateFolder() {
  CreateFolderDialogRef.value.open(SourceTypeEnum.TOOL, folder.currentFolder.id)
}

watch(
  () => folder.currentFolder,
  (newValue) => {
    if (newValue && newValue.id) {
      paginationConfig.current_page = 1
      tool.setToolList([])
      getList()
    }
  },
  { deep: true, immediate: true },
)

watch(
  () => tool.tool_type,
  () => {
    paginationConfig.current_page = 1
    tool.setToolList([])
    getList()
  },
)

function getList() {
  const params: any = {
    folder_id: folder.currentFolder?.id || user.getWorkspaceId(),
    scope: apiType.value === 'systemShare' ? 'SHARED' : 'WORKSPACE',
    tool_type: tool.tool_type || '',
  }
  if (search_form.value[search_type.value]) {
    params[search_type.value] = search_form.value[search_type.value]
  }
  loadSharedApi({ type: 'tool', isShared: isShared.value, systemType: apiType.value })
    .getToolListPage(paginationConfig, params, loading)
    .then((res: any) => {
      paginationConfig.total = res.data?.total
      tool.setToolList([...tool.toolList, ...res.data?.records])
    })
}

function refreshFolder() {
  emit('refreshFolder')
}

function searchHandle() {
  paginationConfig.current_page = 1
  tool.setToolList([])
  getList()
}

onMounted(() => {
  if (apiType.value !== 'workspace') {
    getList()
  }
  loadSharedApi({ type: 'workspace', isShared: isShared.value, systemType: apiType.value })
    .getAllMemberList(user.getWorkspaceId(), loading)
    .then((res: any) => {
      user_options.value = res.data
    })
  getStoreToolList()
})
</script>

<style lang="scss" scoped></style>
