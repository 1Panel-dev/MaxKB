<template>
  <div class="resource-manage_tool">
    <div class="shared-header">
      <span class="title">{{ t('views.system.resource_management') }}</span>
      <el-icon size="12">
        <rightOutlined></rightOutlined>
      </el-icon>
      <span class="sub-title">{{ t('views.tool.title') }}</span>
    </div>
    <div class="table-content">
      <div class="flex-between complex-search">
        <el-select
          class="complex-search__left"
          v-model="search_type"
          style="width: 120px"
          @change="search_type_change"
        >
          <el-option :label="$t('common.creator')" value="create_user" />

          <el-option :label="$t('views.model.modelForm.modeName.label')" value="name" />
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
          clearable
          style="width: 220px"
        >
          <el-option v-for="u in user_options" :key="u.id" :value="u.id" :label="u.username" />
        </el-select>
      </div>
      <div class="table-knowledge">
        <el-table height="100%" :data="toolList" style="width: 100%">
          <el-table-column type="selection" width="55" />
          <el-table-column width="220" :label="$t('common.name')">
            <template #default="scope">
              <div class="table-name flex align-center">
                <el-icon size="24">
                  <el-avatar
                    v-if="isAppIcon(scope.row?.icon)"
                    shape="square"
                    :size="24"
                    style="background: none"
                    class="mr-8"
                  >
                    <img :src="scope.row?.icon" alt="" />
                  </el-avatar>
                  <el-avatar v-else class="avatar-green" shape="square" :size="24">
                    <img src="@/assets/node/icon_tool.svg" style="width: 58%" alt="" />
                  </el-avatar>
                </el-icon>
                {{ scope.row.name }}
              </div>
            </template>
          </el-table-column>
          <el-table-column
            property="type"
            :label="$t('views.application.form.appType.label')"
            width="120"
          />
          <el-table-column width="100" property="workspace_id">
            <template #header>
              <div class="flex align-center">
                {{ $t('views.role.member.workspace') }}

                <el-popover placement="bottom">
                  <template #reference
                    ><el-icon style="margin-left: 4px; cursor: pointer" size="16">
                      <AppIcon iconName="app-filter_outlined"></AppIcon> </el-icon
                  ></template>
                  <div>
                    <el-checkbox
                      v-model="checkAll"
                      :indeterminate="isIndeterminate"
                      @change="handleCheckAllChange"
                    >
                      {{ $t('views.document.feishu.allCheck') }}
                    </el-checkbox>
                    <el-checkbox-group
                      v-model="checkedWorkspaces"
                      @change="handleCheckedWorkspacesChange"
                    >
                      <el-checkbox
                        v-for="workspace in workspaces"
                        :key="workspace"
                        :label="workspace"
                        :value="workspace"
                      >
                        {{ workspace }}
                      </el-checkbox>
                    </el-checkbox-group>
                  </div>
                </el-popover>
              </div>
            </template>
          </el-table-column>
          <el-table-column property="creator" :label="$t('common.creator')" />
          <el-table-column
            property="update_time"
            sortable
            width="180"
            :formatter="formatter"
            :label="$t('views.document.table.updateTime')"
          />
          <el-table-column
            width="180"
            property="create_time"
            sortable
            :formatter="formatter"
            :label="$t('common.createTime')"
          />
          <el-table-column
            class-name="operation-column_text"
            width="160"
            fixed="right"
            :label="$t('common.operation')"
          >
            <template #default="scope">
              <el-switch
                v-model="scope.row.is_active"
                :before-change="() => changeState(scope.row)"
                size="small"
                class="mr-4"
              />
              <el-divider direction="vertical" />
              <el-button
                text
                type="primary"
                v-if="!scope.row.template_id"
                :disabled="!canEdit(scope.row)"
                @click.stop="openCreateDialog(scope.row)"
              >
                <el-icon size="16">
                  <EditPen />
                </el-icon>
              </el-button>

              <el-button
                text
                type="primary"
                v-if="scope.row.init_field_list?.length > 0"
                :disabled="!canEdit(scope.row)"
                @click.stop="configInitParams(scope.row)"
              >
                <el-icon size="16">
                  <AppIcon iconName="app-operation" class="mr-4"></AppIcon>
                </el-icon>
              </el-button>
              <el-button
                text
                type="primary"
                :disabled="!canEdit(scope.row)"
                @click.stop="deleteTool(scope.row)"
              >
                <el-icon size="16">
                  <Delete />
                </el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="table__pagination mt-16">
        <el-pagination
          v-model:current-page="paginationConfig.current_page"
          v-model:page-size="paginationConfig.page_size"
          :page-sizes="pageSizes"
          :total="paginationConfig.total"
          layout="total, prev, pager, next, sizes"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
    <InitParamDrawer ref="InitParamDrawerRef" @refresh="refresh" />
    <ToolFormDrawer ref="ToolFormDrawerRef" @refresh="refresh" :title="ToolDrawertitle" />
    <CreateFolderDialog ref="CreateFolderDialogRef" @refresh="refreshFolder" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed } from 'vue'
import { cloneDeep, get } from 'lodash'
import ToolApi from '@/api/resource-management/tool'
import useStore from '@/stores/modules-resource-management'
import InitParamDrawer from '@/views/resource-management/tool/component/InitParamDrawer.vue'
import iconMap from '@/components/app-icon/icons/common'
import ToolFormDrawer from './ToolFormDrawer.vue'
import CreateFolderDialog from '@/components/folder-tree/CreateFolderDialog.vue'
import { t } from '@/locales'
import { isAppIcon } from '@/utils/common'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import type { CheckboxValueType } from 'element-plus'

const { folder, user } = useStore()

const InitParamDrawerRef = ref()
const search_type = ref('name')
const search_form = ref<{
  name: string
  create_user: string
}>({
  name: '',
  create_user: '',
})
const user_options = ref<any[]>([])
let toolListbp = []
const loading = ref(false)
const changeStateloading = ref(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0,
})
const rightOutlined = iconMap['right-outlined'].iconReader()

const folderList = ref<any[]>([])
const toolList = ref<any[]>([])
const currentFolder = ref<any>({})
const pageSizes = [10, 20, 50, 100]
const checkAll = ref(false)
const isIndeterminate = ref(true)
const checkedWorkspaces = ref([])
let workspaces = []

const handleCheckAllChange = (val: CheckboxValueType) => {
  checkedWorkspaces.value = val ? workspaces : []
  isIndeterminate.value = false
  toolList.value = val ? [...toolListbp] : []
}
const handleCheckedWorkspacesChange = (value: CheckboxValueType[]) => {
  const checkedCount = value.length
  checkAll.value = checkedCount === workspaces.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < workspaces.length
  toolList.value = toolListbp.filter((ele) => value.includes(ele.workspace_id))
}

const handleSizeChange = (val) => {
  console.log(val)
}
const handleCurrentChange = (val) => {
  console.log(val)
}
const search_type_change = () => {
  search_form.value = { name: '', create_user: '' }
}
const canEdit = (row: any) => {
  // return user.userInfo?.id === row?.user_id
  return true
}

const ToolFormDrawerRef = ref()
const ToolDrawertitle = ref('')

function openCreateDialog(data?: any) {
  // 有template_id的不允许编辑，是模板转换来的
  if (data?.template_id) {
    return
  }
  ToolDrawertitle.value = data ? t('views.tool.editTool') : t('views.tool.createTool')
  if (data) {
    if (canEdit(data)) {
      ToolApi.getToolById(data?.id, changeStateloading).then((res) => {
        ToolFormDrawerRef.value.open(res.data)
      })
    }
  } else {
    ToolFormDrawerRef.value.open(data)
  }
}

function getFolder() {
  const params = {}
  folder.asyncGetFolder('TOOL', params, loading).then((res: any) => {
    folderList.value = res.data
    currentFolder.value = res.data?.[0] || {}
    getList()
  })
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
      ToolApi.putTool(row.id, obj, changeStateloading)
        .then(() => {
          return true
        })
        .catch(() => {
          return false
        })
    })
  } else {
    const res = await ToolApi.getToolById(row.id, changeStateloading)
    if (
      !res.data.init_params &&
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
    ToolApi.putTool(row.id, obj, changeStateloading)
      .then(() => {
        return true
      })
      .catch(() => {
        return false
      })
  }
}
const formatter = (_, __, value) => {
  return value ? new Date(value).toLocaleString() : '-'
}
function refresh(data: any) {
  if (data) {
    const index = toolList.value.findIndex((v) => v.id === data.id)
    // if (user.userInfo && data.user_id === user.userInfo.id) {
    //   data.username = user.userInfo.username
    // } else {
    //   data.username = userOptions.value.find((v) => v.value === data.user_id)?.label
    // }
    toolList.value.splice(index, 1, data)
  }
  paginationConfig.total = 0
  paginationConfig.current_page = 1
  toolList.value = []
  getList()
}

function refreshFolder() {
  toolList.value = []
  getFolder()
  getList()
}

function folderClickHandel(row: any) {
  currentFolder.value = row
  toolList.value = []
  getList()
}

function clickFolder(item: any) {
  currentFolder.value.id = item.id
  toolList.value = []
  getList()
}

function copyTool(row: any) {
  ToolDrawertitle.value = t('views.tool.copyTool')
  const obj = cloneDeep(row)
  delete obj['id']
  obj['name'] = obj['name'] + `  ${t('views.tool.form.title.copy')}`
  ToolFormDrawerRef.value.open(obj)
}

function exportTool(row: any) {
  ToolApi.exportTool(row.id, row.name, loading).catch((e: any) => {
    if (e.response.status !== 403) {
      e.response.data.text().then((res: string) => {
        MsgError(`${t('views.application.tip.ExportError')}:${JSON.parse(res).message}`)
      })
    }
  })
}

function deleteTool(row: any) {
  MsgConfirm(
    `${t('views.tool.delete.confirmTitle')}${row.name} ?`,
    t('views.tool.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      ToolApi.delTool(row.id, loading).then(() => {
        const index = toolList.value.findIndex((v) => v.id === row.id)
        toolList.value.splice(index, 1)
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {})
}

function configInitParams(item: any) {
  ToolApi.getToolById(item?.id, changeStateloading).then((res) => {
    InitParamDrawerRef.value.open(res.data)
  })
}

const CreateFolderDialogRef = ref()
function openCreateFolder() {
  CreateFolderDialogRef.value.open('TOOL', currentFolder.value.parent_id)
}

const elUploadRef = ref()
function importTool(file: any) {
  const formData = new FormData()
  formData.append('file', file.raw, file.name)
  elUploadRef.value.clearFiles()
  ToolApi.postImportTool(formData, loading)
    .then(async (res: any) => {
      if (res?.data) {
        toolList.value = []
        getList()
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

function getList() {
  const params = {
    folder_id: currentFolder.value?.id || localStorage.getItem('workspace_id'),
    scope: 'WORKSPACE',
  }
  ToolApi.getToolList(paginationConfig, params, loading).then((res) => {
    paginationConfig.total = res.data?.total
    toolListbp = [...res.data?.records]
    workspaces = [...new Set(toolListbp.map((ele) => ele.workspace_id))]
    checkedWorkspaces.value = [...workspaces]
    checkAll.value = true
    handleCheckAllChange(true)
  })
}

onMounted(() => {
  getList()
})
</script>

<style lang="scss" scoped>
.resource-manage_tool {
  padding: 16px 24px;
  .complex-search {
    width: 280px;
  }
  .complex-search__left {
    width: 75px;
  }

  .el-avatar {
    --el-avatar-size: 24px !important;
  }

  .table-content {
    padding: 24px;
    background-color: #fff;
    border-radius: 4px;
    box-shadow: 0px 2px 4px 0px #1f23291f;
    margin-top: 16px;
    height: calc(100vh - 180px);

    .table-knowledge {
      height: calc(100% - 100px);
      margin-top: 16px;

      .table-name {
        .el-icon {
          margin-right: 8px;
        }
      }

      .operation-column_text {
        .el-button.is-text {
          --el-button-text-color: #3370ff;
        }
        .el-button.is-text:not(.is-disabled):hover {
          background-color: #3370ff1a;
        }
        .el-button + .el-button,
        .el-button + .el-dropdown {
          margin-left: 4px;
        }
      }
    }

    .table__pagination {
      display: flex;
      align-items: center;
      justify-content: flex-end;
    }
  }
  .shared-header {
    color: #646a73;
    font-weight: 400;
    font-size: 14px;
    line-height: 22px;
    display: flex;
    align-items: center;

    :deep(.el-icon i) {
      height: 12px;
    }

    .sub-title {
      color: #1f2329;
    }
  }
}
</style>
