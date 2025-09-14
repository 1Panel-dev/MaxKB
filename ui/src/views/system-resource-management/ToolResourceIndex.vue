<template>
  <div class="resource-manage_tool p-16-24">
    <el-breadcrumb separator-icon="ArrowRight">
      <el-breadcrumb-item>{{ t('views.system.resource_management.label') }}</el-breadcrumb-item>
      <el-breadcrumb-item>
        <h5 class="ml-4 color-text-primary">{{ t('views.tool.title') }}</h5>
      </el-breadcrumb-item>
    </el-breadcrumb>
    <el-card class="mt-16" style="height: calc(var(--app-main-height) + 20px)">
      <div class="flex-between mb-16">
        <div class="complex-search">
          <el-select
            class="complex-search__left"
            v-model="search_type"
            style="width: 120px"
            @change="search_type_change"
          >
            <el-option :label="$t('common.creator')" value="create_user" />

            <el-option :label="$t('views.tool.form.toolName.label')" value="name" />
          </el-select>
          <el-input
            v-if="search_type === 'name'"
            v-model="search_form.name"
            @change="getList"
            :placeholder="$t('common.searchBar.placeholder')"
            style="width: 220px"
            clearable
          />
          <el-select
            v-else-if="search_type === 'create_user'"
            v-model="search_form.create_user"
            @change="getList"
            filterable
            clearable
            style="width: 220px"
          >
            <el-option v-for="u in user_options" :key="u.id" :value="u.id" :label="u.nick_name" />
          </el-select>
        </div>
      </div>

      <app-table
        :data="toolList"
        :pagination-config="paginationConfig"
        @sizeChange="getList"
        @changePage="getList"
        :maxTableHeight="260"
      >
        <!-- <el-table-column type="selection" width="55" /> -->
        <el-table-column width="220" :label="$t('common.name')" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="table-name flex align-center">
              <el-icon size="24" class="mr-8">
                <el-avatar
                  v-if="row?.icon"
                  shape="square"
                  :size="24"
                  style="background: none"
                  class="mr-8"
                >
                  <img :src="resetUrl(row?.icon)" alt="" />
                </el-avatar>

                <ToolIcon v-else :size="24" :type="row?.tool_type" />
              </el-icon>
              {{ row.name }}
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="tool_type" :label="$t('views.system.resource_management.type')">
          <template #default="scope">
            <span v-if="scope.row.tool_type === 'MCP'"> MCP </span>
            <span v-else-if="scope.row.version">{{ $t('views.tool.toolStore.title') }}</span>
            <span v-else>
              {{
                $t(
                  ToolType[
                    scope.row.template_id ? 'INTERNAL' : ('CUSTOM' as keyof typeof ToolType)
                  ],
                )
              }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.status.label')" width="120">
          <template #default="{ row }">
            <div v-if="row.is_active" class="flex align-center">
              <el-icon class="color-success mr-8" style="font-size: 16px">
                <SuccessFilled />
              </el-icon>
              <span class="color-text-primary">
                {{ $t('common.status.enabled') }}
              </span>
            </div>
            <div v-else class="flex align-center">
              <AppIcon iconName="app-disabled" class="color-secondary mr-8"></AppIcon>
              <span class="color-text-primary">
                {{ $t('common.status.disabled') }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          v-if="user.isEE()"
          width="150"
          prop="workspace_name"
          :label="$t('views.workspace.title')"
          show-overflow-tooltip
        >
          <template #header>
            <div>
              <span>{{ $t('views.workspace.title') }}</span>
              <el-popover :width="200" trigger="click" :visible="workspaceVisible">
                <template #reference>
                  <el-button
                    style="margin-top: -2px"
                    :type="workspaceArr && workspaceArr.length > 0 ? 'primary' : ''"
                    link
                    @click="workspaceVisible = !workspaceVisible"
                  >
                    <el-icon>
                      <Filter />
                    </el-icon>
                  </el-button>
                </template>
                <div class="filter">
                  <div class="form-item mb-16 ml-4">
                    <div @click.stop>
                      <el-input
                        v-model="filterText"
                        :placeholder="$t('common.search')"
                        prefix-icon="Search"
                        clearable
                      />
                      <el-scrollbar height="300" v-if="filterData.length">
                        <el-checkbox-group
                          v-model="workspaceArr"
                          style="display: flex; flex-direction: column"
                        >
                          <el-checkbox
                            v-for="item in filterData"
                            :key="item.value"
                            :label="item.label"
                            :value="item.value"
                          />
                        </el-checkbox-group>
                      </el-scrollbar>
                      <el-empty v-else :description="$t('common.noData')" />
                    </div>
                  </div>
                </div>
                <div class="text-right">
                  <el-button size="small" @click="filterWorkspaceChange('clear')"
                    >{{ $t('common.clear') }}
                  </el-button>
                  <el-button type="primary" @click="filterWorkspaceChange" size="small"
                    >{{ $t('common.confirm') }}
                  </el-button>
                </div>
              </el-popover>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="nick_name" :label="$t('common.creator')" show-overflow-tooltip />
        <el-table-column :label="$t('views.document.table.updateTime')" width="180">
          <template #default="{ row }">
            {{ datetimeFormat(row.update_time) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.createTime')" width="180">
          <template #default="{ row }">
            {{ datetimeFormat(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.operation')" align="left" width="160" fixed="right">
          <template #default="{ row }">
            <span @click.stop>
              <el-switch
                v-model="row.is_active"
                :before-change="() => changeState(row)"
                size="small"
                class="mr-4"
                v-if="permissionPrecise.switch()"
              />
            </span>
            <el-divider direction="vertical" />

            <el-tooltip
              effect="dark"
              :content="$t('common.edit')"
              placement="top"
              v-if="row.template_id && permissionPrecise.edit()"
            >
              <span class="mr-8">
                <el-button
                  type="primary"
                  text
                  @click.stop="addInternalTool(row, true)"
                  :title="$t('common.edit')"
                >
                  <AppIcon iconName="app-edit"></AppIcon>
                </el-button>
              </span>
            </el-tooltip>
            <el-tooltip
              effect="dark"
              :content="$t('common.edit')"
              placement="top"
              v-if="!row.template_id && row.tool_type === 'CUSTOM' && permissionPrecise.edit()"
            >
              <span class="mr-8">
                <el-button
                  type="primary"
                  text
                  @click.stop="openCreateDialog(row)"
                  :title="$t('common.edit')"
                >
                  <AppIcon iconName="app-edit"></AppIcon>
                </el-button>
              </span>
            </el-tooltip>
            <el-tooltip
              effect="dark"
              :content="$t('common.edit')"
              placement="top"
              v-if="!row.template_id && row.tool_type === 'MCP' && permissionPrecise.edit()"
            >
              <span class="mr-8">
                <el-button
                  type="primary"
                  text
                  @click.stop="openCreateMcpDialog(row)"
                  :title="$t('common.edit')"
                >
                  <AppIcon iconName="app-edit"></AppIcon>
                </el-button>
              </span>
            </el-tooltip>

            <el-tooltip
              effect="dark"
              :content="$t('common.copy')"
              placement="top"
              v-if="!row.template_id && permissionPrecise.copy()"
            >
              <span class="mr-8">
                <el-button
                  type="primary"
                  text
                  @click.stop="copyTool(row)"
                  :title="$t('common.copy')"
                >
                  <AppIcon iconName="app-copy"></AppIcon>
                </el-button>
              </span>
            </el-tooltip>
            <el-dropdown trigger="click" v-if="MoreFilledPermission(row)">
              <el-button text @click.stop type="primary">
                <AppIcon iconName="app-more"></AppIcon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-if="row.init_field_list?.length > 0 && permissionPrecise.edit()"
                    @click.stop="configInitParams(row)"
                  >
                    <AppIcon iconName="app-operation" class="color-secondary"></AppIcon>
                    {{ $t('common.param.initParam') }}
                  </el-dropdown-item>

                  <el-dropdown-item
                    @click.stop="openAuthorization(row)"
                    v-if="permissionPrecise.auth()"
                  >
                    <AppIcon
                      iconName="app-resource-authorization"
                      class="color-secondary"
                    ></AppIcon>
                    {{ $t('views.system.resourceAuthorization.title') }}
                  </el-dropdown-item>

                  <el-dropdown-item
                    v-if="
                      !row.template_id && row.tool_type === 'CUSTOM' && permissionPrecise.export()
                    "
                    @click.stop="exportTool(row)"
                  >
                    <AppIcon iconName="app-export" class="color-secondary"></AppIcon>
                    {{ $t('common.export') }}
                  </el-dropdown-item>
                  <el-dropdown-item v-if="row.tool_type === 'MCP' && permissionPrecise.edit()" @click.stop="showMcpConfig(row)">
                    <AppIcon iconName="app-operate-log" class="color-secondary"></AppIcon>
                    {{ $t('views.tool.mcpConfig') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="permissionPrecise.delete()"
                    divided
                    @click.stop="deleteTool(row)"
                  >
                    <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
                    {{ $t('common.delete') }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </app-table>
    </el-card>

    <InitParamDrawer ref="InitParamDrawerRef" @refresh="refresh" />
    <ToolFormDrawer ref="ToolFormDrawerRef" @refresh="refresh" :title="ToolDrawertitle" />
    <McpToolFormDrawer ref="McpToolFormDrawerRef" @refresh="refresh" :title="McpToolDrawertitle" />
    <AddInternalToolDialog ref="AddInternalToolDialogRef" @refresh="confirmAddInternalTool" />
    <McpToolConfigDialog ref="McpToolConfigDialogRef" @refresh="refresh" />
    <ResourceAuthorizationDrawer :type="SourceTypeEnum.TOOL" ref="ResourceAuthorizationDrawerRef" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed, watch } from 'vue'
import { cloneDeep } from 'lodash'
import InitParamDrawer from '@/views/tool/component/InitParamDrawer.vue'
import ToolResourceApi from '@/api/system-resource-management/tool'
import AddInternalToolDialog from '@/views/tool/toolStore/AddInternalToolDialog.vue'
import ToolFormDrawer from '@/views/tool/ToolFormDrawer.vue'
import McpToolFormDrawer from '@/views/tool/McpToolFormDrawer.vue'
import ResourceAuthorizationDrawer from '@/components/resource-authorization-drawer/index.vue'
import { t } from '@/locales'
import { SourceTypeEnum } from '@/enums/common'
import { resetUrl } from '@/utils/common'
import { ToolType } from '@/enums/tool'
import useStore from '@/stores'
import { datetimeFormat } from '@/utils/time'
import { loadPermissionApi } from '@/utils/dynamics-api/permission-api.ts'
import UserApi from '@/api/user/user.ts'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import permissionMap from '@/permission'
import McpToolConfigDialog from '@/views/tool/component/McpToolConfigDialog.vue'

const { user } = useStore()

const search_type = ref('name')
const search_form = ref<any>({
  name: '',
  create_user: '',
})
const user_options = ref<any[]>([])

const loading = ref(false)
const changeStateloading = ref(false)
const toolList = ref<any[]>([])
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})
const workspaceOptions = ref<any[]>([])
const workspaceVisible = ref(false)
const workspaceArr = ref<any[]>([])

const permissionPrecise = computed(() => {
  return permissionMap['tool']['systemManage']
})

const MoreFilledPermission = (row: any) => {
  return (
    permissionPrecise.value.export() ||
    permissionPrecise.value.delete() ||
    permissionPrecise.value.auth() ||
    (row.init_field_list?.length > 0 && permissionPrecise.value.edit())
  )
}

const ResourceAuthorizationDrawerRef = ref()
function openAuthorization(item: any) {
  ResourceAuthorizationDrawerRef.value.open(item.id)
}

function exportTool(row: any) {
  ToolResourceApi.exportTool(row.id, row.name, loading).catch((e: any) => {
    if (e.response.status !== 403) {
      e.response.data.text().then((res: string) => {
        MsgError(`${t('views.application.tip.ExportError')}:${JSON.parse(res).message}`)
      })
    }
  })
}

const McpToolConfigDialogRef = ref()
function showMcpConfig(item: any) {
  ToolResourceApi.getToolById(item?.id, loading).then((res: any) => {
    McpToolConfigDialogRef.value.open(res.data)
  })
}

function deleteTool(row: any) {
  MsgConfirm(
    `${t('views.tool.delete.confirmTitle')}：${row.name} ?`,
    t('views.tool.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      ToolResourceApi.delTool(row.id, loading).then(() => {
        getList()
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {})
}

function configInitParams(item: any) {
  ToolResourceApi.getToolById(item?.id, changeStateloading).then((res: any) => {
    InitParamDrawerRef.value.open(res.data)
  })
}

async function copyTool(row: any) {
  ToolDrawertitle.value = t('views.tool.copyTool')
  const res = await ToolResourceApi.getToolById(row.id, changeStateloading)
  const obj = cloneDeep(res.data)
  delete obj['id']
  obj['name'] = obj['name'] + `  ${t('common.copyTitle')}`
  ToolFormDrawerRef.value.open(obj)
}

const ToolFormDrawerRef = ref()
const McpToolFormDrawerRef = ref()
const ToolDrawertitle = ref('')
const McpToolDrawertitle = ref('')

function openCreateDialog(data?: any) {
  // 有template_id的不允许编辑，是模板转换来的
  if (data?.template_id) {
    return
  }

  ToolDrawertitle.value = t('views.tool.editTool')
  if (data) {
    ToolResourceApi.getToolById(data?.id, loading).then((res: any) => {
      ToolFormDrawerRef.value.open(res.data)
    })
  } else {
    ToolFormDrawerRef.value.open(data)
  }
}

function openCreateMcpDialog(data?: any) {
  // 有template_id的不允许编辑，是模板转换来的
  if (data?.template_id) {
    return
  }

  McpToolDrawertitle.value = data ? t('views.tool.editMcpTool') : t('views.tool.createMcpTool')
  if (data) {
    ToolResourceApi.getToolById(data?.id, loading).then((res: any) => {
      McpToolFormDrawerRef.value.open(res.data)
    })
  } else {
    McpToolFormDrawerRef.value.open(data)
  }
}

const AddInternalToolDialogRef = ref<InstanceType<typeof AddInternalToolDialog>>()
function addInternalTool(data?: any, isEdit?: boolean) {
  AddInternalToolDialogRef.value?.open(data, isEdit)
}

function confirmAddInternalTool(data?: any, isEdit?: boolean) {
  if (isEdit) {
    ToolResourceApi.putTool(data?.id as string, { name: data.name }, loading).then((res: any) => {
      MsgSuccess(t('common.saveSuccess'))
      refresh()
    })
  }
}

const InitParamDrawerRef = ref()
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
      ToolResourceApi.putTool(row.id, obj, changeStateloading)
        .then(() => {
          getList()
          return true
        })
        .catch(() => {
          return false
        })
    })
  } else {
    const res = await ToolResourceApi.getToolById(row.id, changeStateloading)
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
    ToolResourceApi.putTool(row.id, obj, changeStateloading)
      .then(() => {
        getList()
        return true
      })
      .catch(() => {
        return false
      })
  }
}

const filterText = ref('')
const filterData = ref<any[]>([])

watch(
  [() => workspaceOptions.value, () => filterText.value],
  () => {
    if (!filterText.value.length) {
      filterData.value = workspaceOptions.value
    }
    filterData.value = workspaceOptions.value.filter((v: any) =>
      v.label.toLowerCase().includes(filterText.value.toLowerCase()),
    )
  },
  { immediate: true },
)

function filterWorkspaceChange(val: string) {
  if (val === 'clear') {
    workspaceArr.value = []
  }
  getList()
  workspaceVisible.value = false
}
async function getWorkspaceList() {
  if (user.isEE()) {
    const res = await loadPermissionApi('workspace').getSystemWorkspaceList(loading)
    workspaceOptions.value = res.data.map((item: any) => ({
      label: item.name,
      value: item.id,
    }))
  }
}
const search_type_change = () => {
  search_form.value = { name: '', create_user: '' }
}

function getList() {
  const params: any = {}
  if (search_form.value[search_type.value]) {
    params[search_type.value] = search_form.value[search_type.value]
  }
  if (workspaceArr.value.length > 0) {
    params.workspace_ids = JSON.stringify(workspaceArr.value)
  }
  ToolResourceApi.getToolListPage(paginationConfig, params, loading).then((res) => {
    paginationConfig.total = res.data?.total
    toolList.value = res.data?.records
  })
}

function refresh(data?: any) {
  if (data) {
    getList()
  } else {
    paginationConfig.total = 0
    paginationConfig.current_page = 1
    getList()
  }
}

onMounted(() => {
  getWorkspaceList()
  getList()

  UserApi.getAllMemberList('').then((res: any) => {
    user_options.value = res.data
  })
})
</script>

<style lang="scss" scoped></style>
