<template>
  <div class="group p-16-24">
    <div class="mb-16">
      <h2>{{ $t('views.chatUser.title') }}</h2>
      <div class="color-secondary">
        {{
          resource.resource_type === SourceTypeEnum.APPLICATION
            ? $t('views.chatUser.applicationTitleTip')
            : $t('views.chatUser.knowledgeTitleTip')
        }}
      </div>
    </div>
    <el-card style="--el-card-padding: 0">
      <div class="flex">
        <div class="user-left border-r">
          <div class="p-24 pb-0">
            <h4 class="medium mb-12">{{ $t('views.chatUser.group.title') }}</h4>
            <el-input
              v-model="filterText"
              :placeholder="$t('common.search')"
              prefix-icon="Search"
              clearable
            />
          </div>
          <div class="list-height-left">
            <el-scrollbar v-loading="loading">
              <div class="p-16">
                <common-list
                  :data="filterList"
                  @click="clickUserGroup"
                  :default-active="current?.id"
                >
                  <template #default="{ row }">
                    <span class="ellipsis-1" :title="row.name">{{ row.name }}</span>
                  </template>
                  <template #empty>
                    <span></span>
                  </template>
                </common-list>
              </div>
            </el-scrollbar>
          </div>
        </div>

        <!-- 右边 -->
        <div class="user-right" v-loading="rightLoading">
          <div class="flex-between">
            <div class="flex align-center">
              <h4 class="medium ellipsis" :title="current?.name">{{ current?.name || '-' }}</h4>
              <el-divider direction="vertical" class="mr-8 ml-8" />

              <el-icon class="color-input-placeholder">
                <UserFilled />
              </el-icon>
              <span class="color-input-placeholder ml-4">
                {{ paginationConfig.total }}
              </span>
            </div>

            <div
              class="flex align-center"
              v-if="
                route.path.includes('share/')
                  ? false
                  : hasPermission(permissionObj[currentPermissionKey], 'OR')
              "
            >
              <div class="color-secondary mr-8">{{ $t('views.chatUser.autoAuthorization') }}</div>
              <el-switch
                size="small"
                :model-value="current?.is_auth"
                @click="changeAuth"
                :loading="loading"
              ></el-switch>
            </div>
          </div>

          <div class="flex-between mb-16" style="margin-top: 18px">
            <div class="flex complex-search">
              <el-select class="complex-search__left" v-model="searchType" style="width: 120px">
                <el-option :label="$t('views.login.loginForm.username.label')" value="username" />
                <el-option
                  :label="$t('views.userManage.userForm.nick_name.label')"
                  value="nick_name"
                />
                <el-option :label="$t('views.userManage.source.label')" value="source" />
              </el-select>
              <el-input
                v-if="searchType === 'username'"
                v-model="searchForm.username"
                @change="getList"
                :placeholder="$t('common.inputPlaceholder')"
                style="width: 220px"
                clearable
              />
              <el-input
                v-else-if="searchType === 'nick_name'"
                v-model="searchForm.nick_name"
                @change="getList"
                :placeholder="$t('common.inputPlaceholder')"
                style="width: 220px"
                clearable
              />
              <el-select
                v-else-if="searchType === 'source'"
                v-model="searchForm.source"
                @change="getList"
                :placeholder="$t('common.selectPlaceholder')"
                style="width: 220px"
                clearable
              >
                <el-option :label="$t('views.userManage.source.local')" value="LOCAL" />
                <el-option label="CAS" value="CAS" />
                <el-option label="LDAP" value="LDAP" />
                <el-option label="OIDC" value="OIDC" />
                <el-option label="OAuth2" value="OAuth2" />
                <el-option :label="$t('views.userManage.source.wecom')" value="wecom" />
                <el-option :label="$t('views.userManage.source.lark')" value="lark" />
                <el-option :label="$t('views.userManage.source.dingtalk')" value="dingtalk" />
              </el-select>
            </div>
            <el-button
              type="primary"
              :disabled="current?.is_auth"
              @click="handleSave"
              v-if="
                route.path.includes('share/')
                  ? false
                  : hasPermission(permissionObj[currentPermissionKey], 'OR')
              "
            >
              {{ t('common.save') }}
            </el-button>
          </div>

          <app-table
            :data="tableData"
            :pagination-config="paginationConfig"
            @sizeChange="handleSizeChange"
            @changePage="getList"
            :maxTableHeight="350"
          >
            <el-table-column
              prop="nick_name"
              :label="$t('views.userManage.userForm.nick_name.label')"
            />
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
            <el-table-column :width="140" align="center">
              <template #header>
                <el-checkbox
                  :model-value="allChecked"
                  :indeterminate="allIndeterminate"
                  :disabled="current?.is_auth"
                  @change="handleCheckAll"
                  >{{ $t('views.chatUser.authorization') }}
                </el-checkbox>
              </template>
              <template #default="{ row }">
                <el-checkbox
                  v-model="row.is_auth"
                  :indeterminate="row.indeterminate"
                  :disabled="current?.is_auth"
                  @change="(value: boolean) => handleRowChange(value, row)"
                />
              </template>
            </el-table-column>
          </app-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch, reactive, computed } from 'vue'

import { t } from '@/locales'
import type { ChatUserGroupItem, ChatUserGroupUserItem } from '@/api/type/workspaceChatUser'
import { useRoute } from 'vue-router'
import { SourceTypeEnum } from '@/enums/common'
import { MsgSuccess } from '@/utils/message'
import { ComplexPermission } from '@/utils/permission/type'
import { RoleConst, PermissionConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const route = useRoute()

const {
  params: { id, folderId },
} = route as any

const permissionObj = ref<any>({
  APPLICATION: new ComplexPermission(
    [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole, RoleConst.USER.getWorkspaceRole],
    [
      PermissionConst.APPLICATION_CHAT_USER_EDIT,
      PermissionConst.APPLICATION_CHAT_USER_EDIT.getApplicationWorkspaceResourcePermission(id),
    ],
    [],
    'OR',
  ),
  KNOWLEDGE: new ComplexPermission(
    [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole, RoleConst.USER.getWorkspaceRole],
    [
      PermissionConst.KNOWLEDGE_CHAT_USER_EDIT,
      PermissionConst.KNOWLEDGE_CHAT_USER_EDIT.getKnowledgeWorkspaceResourcePermission(id),
    ],
    [],
    'OR',
  ),
  RESOURCE_APPLICATION: [RoleConst.ADMIN, PermissionConst.RESOURCE_APPLICATION_CHAT_USER_EDIT],
  RESOURCE_KNOWLEDGE: [RoleConst.ADMIN, PermissionConst.RESOURCE_KNOWLEDGE_CHAT_USER_EDIT],
  SHAREDKNOWLEDGE: new ComplexPermission(
    [RoleConst.ADMIN],
    [PermissionConst.SHARED_KNOWLEDGE_CHAT_USER_EDIT],
    [],
    'OR',
  ),
})

const currentPermissionKey = computed(() => {
  if (route.path.includes('shared')) return 'SHAREDKNOWLEDGE'
  if (route.path.includes('resource-management')) {
    if (route.meta?.resourceType === 'KNOWLEDGE') {
      return 'RESOURCE_KNOWLEDGE'
    } else if (route.meta?.resourceType === 'APPLICATION') {
      return 'RESOURCE_APPLICATION'
    }
  }
  return route.meta?.resourceType as string
})

const resource = reactive({
  resource_id: route.params.id as string,
  resource_type: route.meta.resourceType as string,
})

const filterText = ref('')
const loading = ref(false)
const list = ref<ChatUserGroupItem[]>([])
const filterList = ref<ChatUserGroupItem[]>([]) // 搜索过滤后列表
const current = ref<ChatUserGroupItem>()
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

async function getUserGroupList() {
  try {
    const res = await loadSharedApi({
      type: 'chatUser',
      isShared: isShared.value,
      systemType: apiType.value,
    }).getUserGroupList(resource, loading)
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

function filter(list: ChatUserGroupItem[], filterText: string) {
  if (!filterText.length) {
    return list
  }
  return list.filter((v: ChatUserGroupItem) =>
    v.name.toLowerCase().includes(filterText.toLowerCase()),
  )
}

watch(filterText, (val: string) => {
  filterList.value = filter(list.value, val)
})

const checkedMap = reactive<Record<string, boolean>>({}) // 选中的

function clickUserGroup(item: ChatUserGroupItem) {
  // 清空跨组勾选缓存
  for (const key in checkedMap) delete checkedMap[key]
  current.value = item
}

async function changeAuth() {
  const params = [{ user_group_id: current.value?.id as string, is_auth: !current.value?.is_auth }]
  try {
    await loadSharedApi({
      type: 'chatUser',
      systemType: apiType.value,
    }).editUserGroupList(resource, params, loading)
    await getUserGroupList()
    current.value = {
      name: current.value?.name as string,
      id: current.value?.id as string,
      is_auth: !current.value?.is_auth,
    }
    getList()
  } catch (error) {
    console.error(error)
  }
}

const rightLoading = ref(false)

const searchType = ref('username')
const searchForm = ref<Record<string, any>>({
  username: '',
  nick_name: '',
  source: '',
})
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

const tableData = ref<ChatUserGroupUserItem[]>([])

const isShared = computed(() => {
  return folderId === 'share'
})

async function getList() {
  if (!current.value?.id) return
  const params: any = {}
  const searchValue = searchForm.value[searchType.value as keyof typeof searchForm.value]
  if (searchValue !== undefined && searchValue !== null && searchValue !== '') {
    params[searchType.value] = searchValue
  }
  try {
    const res = await loadSharedApi({
      type: 'chatUser',
      isShared: isShared.value,
      systemType: apiType.value,
    }).getUserGroupUserList(resource, current.value?.id, paginationConfig, params, rightLoading)
    // 更新缓存和回显状态
    res.data.records.forEach((item: any) => {
      if (checkedMap[item.id] === undefined) {
        checkedMap[item.id] = item.is_auth
      }
      item.is_auth = checkedMap[item.id]
    })

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

watch(
  () => current.value?.id,
  () => {
    paginationConfig.current_page = 1
    getList()
  },
)

const allChecked = computed(
  () => tableData.value.length > 0 && tableData.value.every((item) => checkedMap[item.id]),
)

const allIndeterminate = computed(
  () => !allChecked.value && tableData.value.some((item) => checkedMap[item.id]),
)

const handleCheckAll = (checked: boolean) => {
  tableData.value.forEach((item) => {
    item.is_auth = checked
    checkedMap[item.id] = checked
  })
}

const handleRowChange = (value: boolean, row: ChatUserGroupUserItem) => {
  row.is_auth = value
  checkedMap[row.id] = value
}

async function handleSave() {
  try {
    const params = Object.entries(checkedMap).map(([id, is_auth]) => ({
      chat_user_id: id,
      is_auth,
    }))
    await loadSharedApi({
      type: 'chatUser',
      systemType: apiType.value,
    }).putUserGroupUser(resource, current.value?.id as string, params, rightLoading)
    MsgSuccess(t('common.saveSuccess'))
  } catch (error) {
    console.error(error)
  }
}
</script>

<style lang="scss" scoped>
.user-left {
  box-sizing: border-box;
  width: var(--setting-left-width);
  min-width: var(--setting-left-width);

  .list-height-left {
    height: calc(100vh - 251px);
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
