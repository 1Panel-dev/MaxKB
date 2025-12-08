<template>
  <LayoutContainer showCollapse resizable class="application-manage">
    <template #left>
      <h4 class="p-12-16 pb-0 mt-12">{{ $t('views.application.title') }}</h4>

      <folder-tree
        :source="SourceTypeEnum.APPLICATION"
        :data="folderList"
        :currentNodeKey="folder.currentFolder?.id"
        @handleNodeClick="folderClickHandle"
        @refreshTree="refreshFolder"
        :draggable="true"
      />
    </template>
    <ContentContainer>
      <template #header>
        <FolderBreadcrumb :folderList="folderList" @click="folderClickHandle" />
      </template>
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

              <el-option :label="$t('common.name')" value="name" />

              <el-option :label="$t('common.publishStatus')" value="publish_status" />
            </el-select>
            <el-input
              v-if="search_type === 'name'"
              v-model="search_form.name"
              @change="searchHandle"
              :placeholder="$t('common.searchBar.placeholder')"
              style="width: 220px"
              clearable
            />
            <el-select
              v-else-if="search_type === 'create_user'"
              v-model="search_form.create_user"
              @change="searchHandle"
              filterable
              clearable
              style="width: 220px"
            >
              <el-option v-for="u in user_options" :key="u.id" :value="u.id" :label="u.nick_name" />
            </el-select>
            <el-select
              v-else-if="search_type === 'publish_status'"
              v-model="search_form.publish_status"
              @change="searchHandle"
              filterable
              clearable
              style="width: 220px"
            >
              <el-option :label="$t('common.published')" value="published" />
              <el-option :label="$t('common.unpublished')" value="unpublished" />
            </el-select>
          </div>
          <el-dropdown trigger="click" v-if="permissionPrecise.create()">
            <el-button type="primary" class="ml-8">
              {{ $t('common.create') }}
              <el-icon class="el-icon--right">
                <arrow-down />
              </el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu class="create-dropdown">
                <el-dropdown-item @click="openCreateDialog('SIMPLE')">
                  <div class="flex">
                    <el-avatar shape="square" class="avatar-blue mt-4" :size="32">
                      <img
                        src="@/assets/application/icon_simple_application.svg"
                        style="width: 65%"
                        alt=""
                      />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">{{ $t('views.application.simple') }}</div>
                      <el-text type="info" size="small"
                        >{{ $t('views.application.simplePlaceholder') }}
                      </el-text>
                    </div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item @click="openCreateDialog('WORK_FLOW')">
                  <div class="flex">
                    <el-avatar shape="square" class="avatar-purple mt-4" :size="32">
                      <img
                        src="@/assets/application/icon_workflow_application.svg"
                        style="width: 65%"
                        alt=""
                      />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">{{ $t('views.application.workflow') }}</div>
                      <el-text type="info" size="small"
                        >{{ $t('views.application.workflowPlaceholder') }}
                      </el-text>
                    </div>
                  </div>
                </el-dropdown-item>
                <el-upload
                  class="import-button"
                  ref="elUploadRef"
                  :file-list="[]"
                  action="#"
                  multiple
                  :auto-upload="false"
                  :show-file-list="false"
                  :limit="1"
                  :on-change="(file: any, fileList: any) => importApplication(file)"
                >
                  <el-dropdown-item>
                    <div class="flex align-center w-full">
                      <el-avatar shape="square" class="mt-4" :size="32" style="background: none">
                        <img src="@/assets/icon_import.svg" alt="" />
                      </el-avatar>
                      <div class="pre-wrap ml-8">
                        <div class="lighter">{{ $t('common.importCreate') }}</div>
                      </div>
                    </div>
                  </el-dropdown-item>
                </el-upload>
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
        style="max-height: calc(100vh - 120px)"
      >
        <InfiniteScroll
          :size="applicationList.length"
          :total="paginationConfig.total"
          :page_size="paginationConfig.page_size"
          v-model:current_page="paginationConfig.current_page"
          @load="getList"
          :loading="loading"
        >
          <el-row v-if="applicationList.length > 0" :gutter="15" class="w-full">
            <template v-for="(item, index) in applicationList" :key="index">
              <!-- <el-col
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
                  :description="item.desc || $t('components.noDesc')"
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
                      {{ $t('common.creator') }}: {{ i18n_name(item.nick_name) }}
                    </el-text>
                  </template>
                </CardBox>
              </el-col> -->
              <el-col :xs="24" :sm="12" :md="12" :lg="8" :xl="6" class="mb-16">
                <CardBox
                  :title="item.name"
                  :description="item.desc"
                  class="cursor"
                  @click="goApp(item)"
                >
                  <template #icon>
                    <el-avatar shape="square" :size="32" style="background: none">
                      <img :src="resetUrl(item?.icon, resetUrl('./favicon.ico'))" alt="" />
                    </el-avatar>
                  </template>
                  <template #subTitle>
                    <el-text class="color-secondary lighter" size="small">
                      <auto-tooltip :content="item.username">
                        {{ $t('common.creator') }}: {{ i18n_name(item.nick_name) }}
                      </auto-tooltip>
                    </el-text>
                  </template>
                  <template #tag>
                    <el-tag v-if="isWorkFlow(item.type)" class="warning-tag">
                      {{ $t('views.application.workflow') }}
                    </el-tag>
                    <el-tag class="blue-tag" v-else>
                      {{ $t('views.application.simple') }}
                    </el-tag>
                  </template>

                  <template #footer>
                    <div v-if="item.is_publish" class="flex align-center">
                      <el-icon class="color-success mr-8" style="font-size: 16px">
                        <SuccessFilled />
                      </el-icon>
                      <span class="color-secondary">
                        {{ $t('views.application.status.published') }}
                      </span>
                      <el-divider direction="vertical" />
                      <AppIcon iconName="app-clock" class="color-secondary mr-8"></AppIcon>

                      <span class="color-secondary">{{ dateFormat(item.update_time) }}</span>
                    </div>
                    <div v-else class="flex align-center">
                      <AppIcon iconName="app-disabled" class="color-secondary mr-8"></AppIcon>
                      <span class="color-secondary">
                        {{ $t('views.application.status.unpublished') }}
                      </span>
                    </div>
                  </template>
                  <template #mouseEnter>
                    <div @click.stop>
                      <el-dropdown trigger="click">
                        <el-button text @click.stop>
                          <AppIcon iconName="app-more"></AppIcon>
                        </el-button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item @click.stop="toChat(item)">
                              <AppIcon iconName="app-create-chat" class="color-secondary"></AppIcon>
                              {{ $t('views.application.operation.toChat') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              @click.stop="settingApplication(item)"
                              v-if="permissionPrecise.edit(item.id)"
                            >
                              <AppIcon iconName="app-setting" class="color-secondary"></AppIcon>
                              {{ $t('common.setting') }}
                            </el-dropdown-item>

                            <el-dropdown-item
                              @click.stop="openAuthorization(item)"
                              v-if="permissionPrecise.auth(item.id)"
                            >
                              <AppIcon
                                iconName="app-resource-authorization"
                                class="color-secondary"
                              ></AppIcon>
                              {{ $t('views.system.resourceAuthorization.title') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              @click.stop="openMoveToDialog(item)"
                              v-if="permissionPrecise.edit(item.id) && apiType === 'workspace'"
                            >
                              <AppIcon iconName="app-migrate" class="color-secondary"></AppIcon>
                              {{ $t('common.moveTo') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              @click="copyApplication(item)"
                              v-if="permissionPrecise.create()"
                            >
                              <AppIcon iconName="app-copy" class="color-secondary"></AppIcon>
                              {{ $t('common.copy') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              divided
                              @click.stop="exportApplication(item)"
                              v-if="permissionPrecise.export(item.id)"
                            >
                              <AppIcon iconName="app-export" class="color-secondary"></AppIcon>
                              {{ $t('common.export') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              divided
                              @click.stop="deleteApplication(item)"
                              v-if="permissionPrecise.delete(item.id)"
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
        </InfiniteScroll>
      </div>
    </ContentContainer>
    <CreateApplicationDialog ref="CreateApplicationDialogRef" />
    <CopyApplicationDialog ref="CopyApplicationDialogRef" />
    <CreateFolderDialog ref="CreateFolderDialogRef" @refresh="refreshFolder" />
    <MoveToDialog
      ref="MoveToDialogRef"
      :source="SourceTypeEnum.APPLICATION"
      @refresh="refreshApplicationList"
      v-if="apiType === 'workspace'"
    />
    <ResourceAuthorizationDrawer
      :type="SourceTypeEnum.APPLICATION"
      ref="ResourceAuthorizationDrawerRef"
    />
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed } from 'vue'
import CreateApplicationDialog from '@/views/application/component/CreateApplicationDialog.vue'
import CreateFolderDialog from '@/components/folder-tree/CreateFolderDialog.vue'
import CopyApplicationDialog from '@/views/application/component/CopyApplicationDialog.vue'
import MoveToDialog from '@/components/folder-tree/MoveToDialog.vue'
import ResourceAuthorizationDrawer from '@/components/resource-authorization-drawer/index.vue'
import ApplicationApi from '@/api/application/application'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import useStore from '@/stores'
import { t } from '@/locales'
import { i18n_name } from '@/utils/common'
import { useRouter, useRoute } from 'vue-router'
import { isWorkFlow } from '@/utils/application'
import { resetUrl } from '@/utils/common'
import { dateFormat } from '@/utils/time'
import { SourceTypeEnum } from '@/enums/common'
import permissionMap from '@/permission'
import WorkspaceApi from '@/api/workspace/workspace'
import { hasPermission } from '@/utils/permission'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'

const router = useRouter()

const apiType = computed<'workspace'>(() => {
  return 'workspace'
})
const permissionPrecise = computed(() => {
  return permissionMap['application'][apiType.value]
})

const { folder, application, user } = useStore()

const loading = ref(false)

const search_type = ref('name')
const search_form = ref<any>({
  name: '',
  create_user: '',
  publish_status: undefined,
})

const user_options = ref<any[]>([])

const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0,
})

const folderList = ref<any[]>([])
const applicationList = ref<any[]>([])
const CopyApplicationDialogRef = ref()

const ResourceAuthorizationDrawerRef = ref()
function openAuthorization(item: any) {
  ResourceAuthorizationDrawerRef.value.open(item.id)
}

const MoveToDialogRef = ref()

function openMoveToDialog(data: any) {
  const obj = {
    id: data.id,
    folder_id: data.folder,
  }
  MoveToDialogRef.value?.open(obj)
}

function refreshApplicationList(row: any) {
  const index = applicationList.value.findIndex((v) => v.id === row.id)
  applicationList.value.splice(index, 1)
}

const goApp = (item: any) => {
  router.push({ path: get_route(item) })
}

const get_route = (item: any) => {
  if (
    hasPermission(
      [
        new ComplexPermission(
          [RoleConst.USER],
          [PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(item.id)],
          [],
          'AND',
        ),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.APPLICATION_OVERVIEW_READ.getWorkspacePermissionWorkspaceManageRole,
        PermissionConst.APPLICATION_OVERVIEW_READ.getApplicationWorkspaceResourcePermission(
          item.id,
        ),
      ],
      'OR',
    )
  ) {
    return `/application/workspace/${item.id}/${item.type}/overview`
  } else if (
    hasPermission(
      [
        new ComplexPermission(
          [RoleConst.USER],
          [PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(item.id)],
          [],
          'AND',
        ),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.APPLICATION_EDIT.getWorkspacePermissionWorkspaceManageRole,
        PermissionConst.APPLICATION_EDIT.getApplicationWorkspaceResourcePermission(item.id),
      ],
      'OR',
    )
  ) {
    if (item.type == 'WORK_FLOW') {
      return `/application/workspace/${item.id}/workflow`
    } else {
      return `/application/workspace/${item.id}/${item.type}/setting`
    }
  } else if (
    hasPermission(
      [
        new ComplexPermission(
          [RoleConst.USER],
          [PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(item.id)],
          [EditionConst.IS_EE, EditionConst.IS_PE],
          'AND',
        ),
        new ComplexPermission(
          [RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
          [PermissionConst.APPLICATION_ACCESS_READ.getWorkspacePermissionWorkspaceManageRole],
          [EditionConst.IS_EE, EditionConst.IS_PE],
          'OR',
        ),
        new ComplexPermission(
          [],
          [
            PermissionConst.APPLICATION_ACCESS_READ.getApplicationWorkspaceResourcePermission(
              item.id,
            ),
          ],
          [EditionConst.IS_EE, EditionConst.IS_PE],
          'OR',
        ),
      ],
      'OR',
    )
  ) {
    return `/application/workspace/${item.id}/${item.type}/access`
  } else if (
    hasPermission(
      [
        new ComplexPermission(
          [RoleConst.USER],
          [PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(item.id)],
          [EditionConst.IS_EE, EditionConst.IS_PE],
          'AND',
        ),
        new ComplexPermission(
          [RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
          [PermissionConst.APPLICATION_CHAT_USER_READ.getWorkspacePermissionWorkspaceManageRole],
          [EditionConst.IS_EE, EditionConst.IS_PE],
          'OR',
        ),
        new ComplexPermission(
          [],
          [
            PermissionConst.APPLICATION_CHAT_USER_READ.getApplicationWorkspaceResourcePermission(
              item.id,
            ),
          ],
          [EditionConst.IS_EE, EditionConst.IS_PE],
          'OR',
        ),
      ],
      'OR',
    )
  ) {
    return `/application/workspace/${item.id}/${item.type}/chat-user`
  } else if (
    hasPermission(
      [
        new ComplexPermission(
          [RoleConst.USER],
          [PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(item.id)],
          [],
          'AND',
        ),
        PermissionConst.APPLICATION_CHAT_LOG_READ.getWorkspacePermissionWorkspaceManageRole,
        PermissionConst.APPLICATION_CHAT_LOG_READ.getApplicationWorkspaceResourcePermission(
          item.id,
        ),
      ],
      'OR',
    )
  ) {
    return `/application//workspace${item.id}/${item.type}/chat-log`
  } else return `/application/`
}

const CreateApplicationDialogRef = ref()

function openCreateDialog(type?: string) {
  CreateApplicationDialogRef.value.open(folder.currentFolder?.id || 'default', type)
}

const search_type_change = () => {
  search_form.value = { name: '', create_user: '' }
}

function toChat(row: any) {
  const api =
    row.type == 'WORK_FLOW'
      ? (id: string) => ApplicationApi.getApplicationDetail(id)
      : (id: string) => Promise.resolve({ data: row })
  api(row.id).then((ok) => {
    let aips = ok.data?.work_flow?.nodes
      ?.filter((v: any) => v.id === 'base-node')
      .map((v: any) => {
        return v.properties.api_input_field_list
          ? v.properties.api_input_field_list.map((v: any) => {
              return {
                name: v.variable,
                value: v.default_value,
              }
            })
          : v.properties.input_field_list
            ? v.properties.input_field_list
                .filter((v: any) => v.assignment_method === 'api_input')
                .map((v: any) => {
                  return {
                    name: v.variable,
                    value: v.default_value,
                  }
                })
            : []
      })
      .reduce((x: Array<any>, y: Array<any>) => [...x, ...y])
    aips = aips ? aips : []
    const apiParams = mapToUrlParams(aips) ? '?' + mapToUrlParams(aips) : ''
    ApplicationApi.getAccessToken(row.id, loading).then((res: any) => {
      window.open(application.location + res?.data?.access_token + apiParams)
    })
  })
}

function mapToUrlParams(map: any[]) {
  const params = new URLSearchParams()

  map.forEach((item: any) => {
    params.append(encodeURIComponent(item.name), encodeURIComponent(item.value))
  })

  return params.toString() // 返回 URL 查询字符串
}

function copyApplication(row: any) {
  ApplicationApi.getApplicationDetail(row.id, loading).then((res: any) => {
    if (res?.data) {
      CopyApplicationDialogRef.value.open(
        { ...res.data, model_id: res.data.model },
        folder.currentFolder?.id || 'default',
      )
    }
  })
}

function settingApplication(row: any) {
  if (isWorkFlow(row.type)) {
    router.push({ path: `/application/workspace/${row.id}/workflow` })
  } else {
    router.push({ path: `/application/workspace/${row.id}/${row.type}/setting` })
  }
}

function deleteApplication(row: any) {
  MsgConfirm(
    `${t('views.application.delete.confirmTitle')}${row.name} ?`,
    t('views.application.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      ApplicationApi.delApplication(row.id, loading).then(() => {
        const index = applicationList.value.findIndex((v) => v.id === row.id)
        applicationList.value.splice(index, 1)
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {})
}

const exportApplication = (application: any) => {
  ApplicationApi.exportApplication(application.id, application.name, loading).catch((e) => {
    if (e.response.status !== 403) {
      e.response.data.text().then((res: string) => {
        MsgError(`${t('views.application.tip.ExportError')}:${JSON.parse(res).message}`)
      })
    }
  })
}

const elUploadRef = ref()
const importApplication = (file: any) => {
  const formData = new FormData()
  formData.append('file', file.raw, file.name)
  elUploadRef.value.clearFiles()
  ApplicationApi.importApplication(folder.currentFolder.id, formData, loading)
    .then(async (res: any) => {
      if (res?.data) {
        applicationList.value = []
        user.profile()
      }
    })
    .then(() => {
      getList()
    })
    .catch((e) => {
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
  CreateFolderDialogRef.value.open(SourceTypeEnum.APPLICATION, folder.currentFolder.id)
}

function getFolder(bool?: boolean) {
  const params = {}
  folder.asyncGetFolder(SourceTypeEnum.APPLICATION, params, loading).then((res: any) => {
    folderList.value = res.data
    if (bool) {
      // 初始化刷新
      folder.setCurrentFolder(res.data?.[0] || {})
    }
    getList()
  })
}

function clickFolder(item: any) {
  folder.setCurrentFolder(item)
  paginationConfig.current_page = 1
  applicationList.value = []
  getList()
}

function folderClickHandle(row: any) {
  if (row.id === folder.currentFolder?.id) {
    return
  }
  folder.setCurrentFolder(row)
  paginationConfig.current_page = 1
  applicationList.value = []
  getList()
}

function refreshFolder() {
  paginationConfig.current_page = 1
  applicationList.value = []
  getFolder()
}

function searchHandle() {
  paginationConfig.current_page = 1
  applicationList.value = []
  getList()
}

function getList() {
  const params: any = {
    folder_id: folder.currentFolder?.id || 'default',
  }
  if (search_form.value[search_type.value]) {
    params[search_type.value] = search_form.value[search_type.value]
  }
  ApplicationApi.getApplication(paginationConfig, params, loading).then((res) => {
    paginationConfig.total = res.data.total
    applicationList.value = [...applicationList.value, ...res.data.records]
  })
}

onMounted(() => {
  getFolder(folder.currentFolder?.id ? false : true)
  WorkspaceApi.getAllMemberList(user.getWorkspaceId(), loading).then((res) => {
    user_options.value = res.data
  })
})
</script>

<style lang="scss" scoped></style>
