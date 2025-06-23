<template>
  <LayoutContainer class="tool-manage">
    <template #left>
      <h4 class="p-16 pb-0">{{ $t('views.tool.title') }}</h4>
      <folder-tree
        :source="FolderSource.TOOL"
        :data="folderList"
        :currentNodeKey="currentFolder?.id"
        @handleNodeClick="folderClickHandel"
        @refreshTree="refreshFolder"
        :shareTitle="$t('views.system.share_tool')"
        :showShared="permissionPrecise['is_share']()"
        class="p-8"
      />
    </template>
    <ContentContainer :header="currentFolder?.name">
      <template #search>
        <div class="flex">
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
          <el-dropdown trigger="click" v-if="!isShared">
            <el-button
              type="primary"
              class="ml-8"
              v-hasPermission="[
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              RoleConst.USER.getWorkspaceRole,
              PermissionConst.TOOL_CREATE.getWorkspacePermission,
              ]"
            >
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
                      <img src="@/assets/node/icon_tool.svg" style="width: 58%" alt="" />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">空白创建</div>
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
                  <el-dropdown-item class="w-full">
                    <div class="flex align-center w-full">
                      <el-avatar shape="square" class="mt-4" :size="36" style="background: none">
                        <img src="@/assets/icon_import.svg" alt="" />
                      </el-avatar>
                      <div class="pre-wrap ml-8">
                        <div class="lighter">{{ $t('common.importCreate') }}</div>
                      </div>
                    </div>
                  </el-dropdown-item>
                </el-upload>
                <el-dropdown-item @click="openToolStoreDialog()">
                  <div class="flex align-center">
                    <el-avatar class="avatar-green" shape="square" :size="32">
                      <img src="@/assets/node/icon_tool.svg" style="width: 58%" alt="" />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">
                        {{ $t('views.tool.toolStore.createFromToolStore') }}
                      </div>
                    </div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item @click="openCreateFolder" divided>
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
      </template>

      <div
        v-loading.fullscreen.lock="paginationConfig.current_page === 1 && loading"
        style="max-height: calc(100vh - 140px)"
      >
        <InfiniteScroll
          :size="toolList.length"
          :total="paginationConfig.total"
          :page_size="paginationConfig.page_size"
          v-model:current_page="paginationConfig.current_page"
          @load="getList"
          :loading="loading"
        >
          <el-row v-if="toolList.length > 0" :gutter="15">
            <template v-for="(item, index) in toolList" :key="index">
              <el-col
                v-if="item.resource_type === 'folder'"
                :xs="24"
                :sm="12"
                :md="12"
                :lg="8"
                :xl="6"
                class="mb-16"
              >
                <CardBox
                  :title="item.name"
                  :description="item.desc || $t('common.noData')"
                  class="cursor"
                  @click="clickFolder(item)"
                >
                  <template #icon>
                    <el-avatar shape="square" :size="32" style="background: none">
                      <AppIcon iconName="app-folder" style="font-size: 32px"></AppIcon>
                    </el-avatar>
                  </template>
                  <template #subTitle>
                    <el-text class="color-secondary lighter" size="small">
                      {{ $t('common.creator') }}: {{ item.nick_name }}
                    </el-text>
                  </template>
                </CardBox>
              </el-col>
              <el-col v-else :xs="24" :sm="12" :md="12" :lg="8" :xl="6" class="mb-16">
                <CardBox :title="item.name" :description="item.desc" class="cursor">
                  <template #icon>
                    <el-avatar
                      v-if="isAppIcon(item?.icon)"
                      shape="square"
                      :size="32"
                      style="background: none"
                      class="mr-8"
                    >
                      <img :src="item?.icon" alt="" />
                    </el-avatar>
                    <el-avatar v-else class="avatar-green" shape="square" :size="32">
                      <img src="@/assets/node/icon_tool.svg" style="width: 58%" alt="" />
                    </el-avatar>
                  </template>
                  <template #subTitle>
                    <el-text class="color-secondary lighter" size="small">
                      {{ $t('common.creator') }}: {{ item.nick_name }}
                    </el-text>
                  </template>
                  <template #tag>
                    <el-tag v-if="isShared" type="info" class="info-tag">
                      {{ t('views.system.shared') }}
                    </el-tag>
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
                    <div @click.stop v-if="!isShared">
                      <el-switch
                        v-model="item.is_active"
                        :before-change="() => changeState(item)"
                        size="small"
                        class="mr-4"
                        v-hasPermission="[
                          RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                          RoleConst.USER.getWorkspaceRole,
                          PermissionConst.TOOL_EDIT.getWorkspacePermission,
                        ]"
                      />
                      <el-divider direction="vertical" />
                      <el-dropdown trigger="click">
                        <el-button text @click.stop>
                          <el-icon>
                            <MoreFilled />
                          </el-icon>
                        </el-button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item v-if="item.template_id" @click.stop="addInternalFunction(item, true)">
                              <el-icon>
                                <EditPen />
                              </el-icon>
                              {{ $t('common.edit') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              v-if="
                              !item.template_id &&
                              hasPermission(
                                [
                                  RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                                  RoleConst.USER.getWorkspaceRole,
                                    PermissionConst.TOOL_EDIT
                                      .getWorkspacePermissionWorkspaceManageRole,
                                  PermissionConst.TOOL_EDIT.getWorkspacePermission,
                                ],
                                'OR',
                              )
                              "
                              @click.stop="openCreateDialog(item)"
                            >
                              <el-icon>
                                <EditPen />
                              </el-icon>
                              {{ $t('common.edit') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              v-if="
                              !item.template_id &&
                              hasPermission(
                                [
                                  RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                                  RoleConst.USER.getWorkspaceRole,
                                  PermissionConst.TOOL_EXPORT.getWorkspacePermission,
                                ],
                                'OR',
                              )
                              "
                              @click.stop="copyTool(item)"
                            >
                              <AppIcon iconName="app-copy"></AppIcon>
                              {{ $t('common.copy') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              v-if="item.init_field_list?.length > 0"
                              @click.stop="configInitParams(item)"
                            >
                              <AppIcon iconName="app-operation" class="mr-4"></AppIcon>
                              {{ $t('common.param.initParam') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              v-if="
                              !item.template_id &&
                              hasPermission(
                                [
                                  RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                                  RoleConst.USER.getWorkspaceRole,
                                  PermissionConst.TOOL_EXPORT.getWorkspacePermission,
                                ],
                                'OR',
                              )
                              "
                              @click.stop="exportTool(item)"
                            >
                              <AppIcon iconName="app-export"></AppIcon>
                              {{ $t('common.export') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              v-if="permissionPrecise.delete()"
                              divided
                              @click.stop="deleteTool(item)"
                            >
                              <el-icon><Delete /></el-icon>
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
        </InfiniteScroll>
      </div>
    </ContentContainer>
    <InitParamDrawer ref="InitParamDrawerRef" @refresh="refresh" />
    <ToolFormDrawer ref="ToolFormDrawerRef" @refresh="refresh" :title="ToolDrawertitle" />
    <CreateFolderDialog ref="CreateFolderDialogRef" @refresh="refreshFolder" v-if="!isShared" />
    <ToolStoreDialog ref="toolStoreDialogRef" @refresh="refresh" />
    <AddInternalFunctionDialog ref="addInternalFunctionDialogRef" @refresh="confirmAddInternalFunction" />
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed } from 'vue'
import { cloneDeep, get } from 'lodash'
import ToolApi from '@/api/tool/tool'
import useStore from '@/stores'
import InitParamDrawer from '@/views/tool/component/InitParamDrawer.vue'
import ToolFormDrawer from './ToolFormDrawer.vue'
import CreateFolderDialog from '@/components/folder-tree/CreateFolderDialog.vue'
import { t } from '@/locales'
import { isAppIcon } from '@/utils/common'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import { FolderSource } from '@/enums/common'
import { ComplexPermission } from '@/utils/permission/type'
import ToolStoreDialog from './component/ToolStoreDialog.vue'
import AddInternalFunctionDialog from './component/AddInternalFunctionDialog.vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import permissionMap from '@/permission'
import { useRoute } from 'vue-router'
const route = useRoute()
const { folder, user } = useStore()

const type = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const permissionPrecise = computed(() => {
  return permissionMap['tool'][type.value]
})

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

const loading = ref(false)
const changeStateloading = ref(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0,
})

const folderList = ref<any[]>([])
const toolList = ref<any[]>([])
const currentFolder = ref<any>({})

const isShared = computed(() => {
  return currentFolder.value.id === 'share'
})

const search_type_change = () => {
  search_form.value = { name: '', create_user: '' }
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
    ToolApi.getToolById(data?.id, changeStateloading).then((res) => {
      ToolFormDrawerRef.value.open(res.data)
    })
  } else {
    ToolFormDrawerRef.value.open(data)
  }
}

function getList() {
  const params = {
    folder_id: currentFolder.value?.id || user.getWorkspaceId(),
    scope: 'WORKSPACE',
  }
  loadSharedApi('tool', isShared.value)
    .getToolListPage(paginationConfig, params, loading)
    .then((res: any) => {
      paginationConfig.total = res.data?.total
      toolList.value = [...toolList.value, ...res.data?.records]
    })
}

function clickFolder(item: any) {
  currentFolder.value.id = item.id
  toolList.value = []
  getList()
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

function refresh(data?: any) {
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

const toolStoreDialogRef = ref<InstanceType<typeof ToolStoreDialog>>()
function openToolStoreDialog() {
  toolStoreDialogRef.value?.open(currentFolder.value.id)
}

const addInternalFunctionDialogRef = ref<InstanceType<typeof AddInternalFunctionDialog>>()
function addInternalFunction(data?: any, isEdit?: boolean) {
  addInternalFunctionDialogRef.value?.open(data, isEdit)
}

function confirmAddInternalFunction(data?: any, isEdit?: boolean) {
  if (isEdit) {
    ToolApi.putTool(data?.id as string, { name: data.name }, loading).then((res) => {
      MsgSuccess(t('common.saveSuccess'))
      refresh()
    })
  }
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

// 文件夹相关
const CreateFolderDialogRef = ref()
function openCreateFolder() {
  CreateFolderDialogRef.value.open(FolderSource.TOOL, currentFolder.value.id)
}
function getFolder(bool?: boolean) {
  const params = {}
  folder.asyncGetFolder(FolderSource.TOOL, params, loading).then((res: any) => {
    folderList.value = res.data
    if (bool) {
      // 初始化刷新
      currentFolder.value = res.data?.[0] || {}
    }
    getList()
  })
}
function refreshFolder() {
  toolList.value = []
  getFolder()
}

function folderClickHandel(row: any) {
  currentFolder.value = row
  toolList.value = []
  getList()
}

onMounted(() => {
  getFolder(true)
})
</script>

<style lang="scss" scoped></style>
