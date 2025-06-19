<template>
  <div class="h-full">
    <ContentContainer>
      <template #header>
        <div class="shared-header">
          <span class="title">{{ t('views.chatUser.title') }}</span>
          <el-icon size="12">
            <rightOutlined></rightOutlined>
          </el-icon>
          <span class="sub-title">{{ t('views.chatUser.group.title') }}</span>
        </div>
      </template>
      <el-card style="--el-card-padding: 0" class="user-card">
        <div class="flex h-full">
          <div class="user-left border-r p-16">
            <div class="user-left_title flex-between">
              <h4 class="medium">{{ $t('views.chatUser.group.title') }}</h4>
              <el-tooltip effect="dark" :content="`${$t('common.create')}${$t('views.chatUser.group.title')}`"
                placement="top">
                <el-button type="primary" text @click="createOrUpdate()"
                  v-hasPermission="new ComplexPermission([RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
                  [PermissionConst.WORKSPACE_USER_GROUP_CREATE.getWorkspacePermission], [], 'OR')">
                  <AppIcon iconName="app-copy"></AppIcon>
                </el-button>
              </el-tooltip>
            </div>

            <div class="p-8">
              <el-input v-model="filterText" :placeholder="$t('common.search')" prefix-icon="Search" clearable />
            </div>
            <div class="list-height-left">
              <el-scrollbar v-loading="loading">
                <common-list :data="filterList" @click="clickUserGroup" :default-active="current?.id">
                  <template #default="{ row }">
                    <div class="flex-between">
                      <span class="ellipsis" style="max-width: initial;">{{ row.name }}</span>
                      <el-dropdown :teleported="false">
                        <el-button text>
                          <el-icon class="color-secondary">
                            <MoreFilled />
                          </el-icon>
                        </el-button>
                        <template #dropdown>
                          <el-dropdown-menu style="min-width: 80px">
                            <el-dropdown-item @click.stop="createOrUpdate(row)" class="p-8"
                              v-if="hasPermission(new ComplexPermission(
                              [RoleConst.ADMIN,RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
                              [PermissionConst.WORKSPACE_USER_GROUP_EDIT.getWorkspacePermission], [], 'OR'), 'OR')">
                              <AppIcon iconName="app-copy"></AppIcon>
                              {{
                                $t('common.rename')
                              }}
                            </el-dropdown-item>
                            <el-dropdown-item @click.stop="deleteGroup(row)" class="border-t p-8"
                              v-if="row.id !== 'default'&&
                              hasPermission(new ComplexPermission(
                              [RoleConst.ADMIN,RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
                              [PermissionConst.WORKSPACE_USER_GROUP_DELETE.getWorkspacePermission], [], 'OR'), 'OR')"
                            >
                              <AppIcon iconName="app-copy"></AppIcon>
                              {{
                                $t('common.delete')
                              }}
                            </el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </div>
                  </template>
                  <template #empty>
                    <span></span>
                  </template>
                </common-list>
              </el-scrollbar>
            </div>
          </div>

          <!-- 右边 -->
          <div class="user-right" v-loading="rightLoading">
            <div class="flex align-center">
              <h4 class="medium">{{ current?.name }}</h4>
              <el-divider direction="vertical" class="mr-8 ml-8" />
              <AppIcon iconName="app-wordspace" style="font-size: 16px" class="color-input-placeholder"></AppIcon>
              <span class="color-input-placeholder ml-4">
                {{ paginationConfig.total }}
              </span>
            </div>

            <div class="flex-between mb-16" style="margin-top: 20px;">
              <div>
                <el-button type="primary" @click="createUser()"
                  v-hasPermission="new ComplexPermission([RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
                  [PermissionConst.WORKSPACE_USER_GROUP_ADD_MEMBER.getWorkspacePermission], [], 'OR')"
                >
                  {{ t('views.role.member.add') }}
                </el-button>
                <el-button :disabled="multipleSelection.length === 0" @click="handleDeleteUser()"
                  v-hasPermission="new ComplexPermission([RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
                  [PermissionConst.WORKSPACE_USER_GROUP_DELETE.getWorkspacePermission], [], 'OR')"
                >
                  {{ $t('common.delete') }}
                </el-button>
              </div>
              <div class="flex-between complex-search">
                <el-select class="complex-search__left" v-model="searchType" style="width: 120px">
                  <el-option :label="$t('views.login.loginForm.username.label')" value="username" />
                </el-select>
                <el-input v-if="searchType === 'username'" v-model="searchForm.username" @change="getList"
                  :placeholder="$t('common.searchBar.placeholder')" style="width: 220px" clearable />
              </div>
            </div>

            <app-table :data="tableData" :pagination-config="paginationConfig" @sizeChange="handleSizeChange"
              @changePage="getList" @selection-change="handleSelectionChange">
              <el-table-column type="selection" width="55" />
              <el-table-column prop="nick_name" :label="$t('views.userManage.userForm.nick_name.label')" />
              <el-table-column prop="username" :label="$t('views.login.loginForm.username.label')" />
              <el-table-column prop="source" :label="$t('views.userManage.source.label')">
                <template #default="{ row }">
                  {{
                    row.source === 'LOCAL'
                      ? $t('views.userManage.source.local')
                      : row.source === 'wecom'
                        ? $t('views.userManage.source.wecom')
                        : row.source === 'lark'
                          ? $t('views.userManage.source.lark')
                          : row.source === 'dingtalk'
                            ? $t('views.userManage.source.dingtalk')
                            : row.source === 'OAUTH2' || row.source === 'OAuth2'
                              ? 'OAuth2'
                              : row.source
                  }}
                </template>
              </el-table-column>
              <el-table-column :label="$t('common.operation')" width="100" fixed="right">
                <template #default="{ row }">
                  <el-tooltip effect="dark" :content="`${$t('views.role.member.delete.button')}`" placement="top">
                    <el-button type="primary" text @click.stop="handleDeleteUser(row)"
                      v-hasPermission="new ComplexPermission([RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
                      [PermissionConst.WORKSPACE_USER_GROUP_REMOVE_MEMBER.getWorkspacePermission], [], 'OR')"
                    >
                      <el-icon>
                        <EditPen />
                      </el-icon>
                    </el-button>
                  </el-tooltip>
                </template>
              </el-table-column>
            </app-table>
          </div>
        </div>
      </el-card>
    </ContentContainer>
    <CreateOrUpdateGroupDialog ref="createOrUpdateGroupDialogRef" @refresh="refresh" />
    <CreateGroupUserDialog ref="createGroupUserDialogRef" @refresh="getList" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch, reactive } from 'vue'
import SystemGroupApi from '@/api/system/user-group'
import { t } from '@/locales'
import type { ChatUserGroupUserItem } from '@/api/type/systemChatUser'
import iconMap from '@/components/app-icon/icons/common'
import CreateOrUpdateGroupDialog from './component/CreateOrUpdateGroupDialog.vue'
import CreateGroupUserDialog from './component/CreateGroupUserDialog.vue'
import type { ListItem } from '@/api/type/common'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'
import { hasPermission } from '@/utils/permission/index'

const filterText = ref('')
const loading = ref(false)
const list = ref<ListItem[]>([])
const filterList = ref<ListItem[]>([]) // 搜索过滤后列表
const current = ref<ListItem>()

const rightOutlined = iconMap['right-outlined'].iconReader()

async function getUserGroupList() {
  try {
    const res = await SystemGroupApi.getUserGroup(loading)
    list.value = res.data
    filterList.value = filter(list.value, filterText.value)
  } catch (error) {
    console.error(error)
  }
}

onMounted(async () => {
  await getUserGroupList()
  current.value = list.value[0]
})

function filter(list: ListItem[], filterText: string) {
  if (!filterText.length) {
    return list
  }
  return list.filter((v: ListItem) =>
    v.name.toLowerCase().includes(filterText.toLowerCase()),
  )
}

watch(filterText, (val: string) => {
  filterList.value = filter(list.value, val)
})

function clickUserGroup(item: ListItem) {
  current.value = item
}

const createOrUpdateGroupDialogRef = ref<InstanceType<typeof CreateOrUpdateGroupDialog>>()

function createOrUpdate(item?: ListItem) {
  createOrUpdateGroupDialogRef.value?.open(item);
}

function deleteGroup(item: ListItem) {
  MsgConfirm(
    `${t('views.chatUser.group.delete.confirmTitle')}${item.name} ?`,
    t('views.chatUser.group.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      SystemGroupApi.delUserGroup(item.id as string, loading).then(async () => {
        MsgSuccess(t('common.deleteSuccess'))
        await getUserGroupList()
        current.value = item.id === current.value?.id ? list.value[0] : current.value
      })
    })
    .catch(() => {
    })
}

async function refresh(group?: ListItem) {
  await getUserGroupList();
  // 创建角色后选中新建的角色
  current.value = group ? group : current.value
}

const rightLoading = ref(false)

const searchType = ref('username')
const searchForm = ref<Record<string, any>>({
  username: '',
})
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

const tableData = ref<ChatUserGroupUserItem[]>([])

async function getList() {
  if (!current.value?.id) return
  try {
    const res = await SystemGroupApi.getUserListByGroup(current.value?.id, paginationConfig, searchForm.value.username, rightLoading)
    tableData.value = res.data.records
    paginationConfig.total = res.data.total
  } catch (error) {
    console.error(error)
  }
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

watch(() => current.value?.id, () => {
  getList()
})

const createGroupUserDialogRef = ref<InstanceType<typeof CreateGroupUserDialog>>()

function createUser() {
  createGroupUserDialogRef.value?.open(current.value?.id as string);
}

const multipleSelection = ref<any[]>([])

function handleSelectionChange(val: any[]) {
  multipleSelection.value = val
}

function handleDeleteUser(item?: ChatUserGroupUserItem) {
  MsgConfirm(
    item ? `${t('views.workspace.member.delete.confirmTitle')}${item.nick_name} ?` : t('views.chatUser.group.batchDeleteMember', { count: multipleSelection.value.length }),
    '',
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      SystemGroupApi.postRemoveMember(current.value?.id as string, { group_relation_ids: item ? [item.user_group_relation_id] : multipleSelection.value.map(item => (item.user_group_relation_id)) }, loading).then(async () => {
        MsgSuccess(t('common.deleteSuccess'))
        await getList()
      })
    })
    .catch(() => {
    })
}
</script>

<style lang="scss" scoped>
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

.content-container {
  height: 100%;
  display: flex;
  flex-direction: column;

  :deep(.content-container__main) {
    flex: 1;
    overflow: hidden;
  }
}

:deep(.user-card) {
  height: 100%;
  overflow: hidden;
}

.user-left {
  box-sizing: border-box;
  width: var(--setting-left-width);
  min-width: var(--setting-left-width);

  .user-left_title {
    padding: 8px;
  }

  .list-height-left {
    height: calc(100vh - 271px);

    :deep(.common-list li) {
      padding-right: 4px;
      padding-left: 8px;
    }
  }
}

.user-right {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 24px;
}
</style>
