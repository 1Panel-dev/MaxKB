<template>
  <div class="resource-authorization p-16-24">
    <div class="flex align-center mb-16">
      <h2>{{ $t('views.resourceAuthorization.title') }}</h2>
      <!-- 企业版: 工作空间下拉框-->
      <el-divider
        class="mr-16"
        direction="vertical"
        v-if="hasPermission(EditionConst.IS_EE, 'OR')"
      />
      <WorkspaceDropdown
        v-if="hasPermission(EditionConst.IS_EE, 'OR')"
        :data="workspaceList"
        :currentWorkspace="currentWorkspace"
        @changeWorkspace="changeWorkspace"
      />
    </div>

    <el-card style="--el-card-padding: 0">
      <div class="flex main-calc-height">
        <div class="resource-authorization__left border-r p-8">
          <div class="p-8">
            <h4 class="mb-12">{{ $t('views.resourceAuthorization.member') }}</h4>
            <el-input
              v-model="filterText"
              :placeholder="$t('common.search')"
              prefix-icon="Search"
              clearable
            />
          </div>
          <div class="list-height-left">
            <el-scrollbar>
              <common-list
                :data="filterMember"
                class="mt-8"
                v-loading="loading"
                @click="clickMemberHandle"
                :default-active="currentUser"
              >
                <template #default="{ row }">
                  <div class="flex-between">
                    <div class="flex">
                      <span class="mr-8">{{ row.nick_name }}</span>
                      <TagGroup :tags="row.roles" />
                    </div>
                  </div>
                </template>
              </common-list>
            </el-scrollbar>
          </div>
        </div>
        <div class="permission-setting p-16 flex" v-loading="rLoading">
          <div class="resource-authorization__table">
            <h4 class="mb-4">{{ $t('views.resourceAuthorization.permissionSetting') }}</h4>
            <el-tabs v-model="activeName" class="resource-authorization__tabs">
              <el-tab-pane
                v-for="(item, index) in settingTags"
                :key="item.value"
                :label="item.label"
                :name="item.value"
              >
                <PermissionSetting
                  :key="index"
                  :data="item.data"
                  :type="item.value"
                  :tableHeight="tableHeight"
                  :manage="isManage(currentType)"
                  @refreshData="refreshData"
                ></PermissionSetting>
              </el-tab-pane>
            </el-tabs>
          </div>

          <div class="submit-button">
            <el-button type="primary" @click="submitPermissions">{{ $t('common.save') }}</el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, watch, computed } from 'vue'
import AuthorizationApi from '@/api/user/resource-authorization'
import PermissionSetting from './component/PermissionSetting.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { AuthorizationEnum } from '@/enums/system'
import { t } from '@/locales'
import useStore from '@/stores'
import { cloneDeep } from 'lodash'
import { EditionConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import WorkspaceApi from '@/api/workspace/workspace.ts'
import type { WorkspaceItem } from '@/api/type/workspace'

const loading = ref(false)
const rLoading = ref(false)
const memberList = ref<any[]>([]) // 全部成员
const filterMember = ref<any[]>([]) // 搜索过滤后列表
const currentUser = ref<string>('')
const currentType = ref<string>('')
const filterText = ref('')

const activeName = ref(AuthorizationEnum.KNOWLEDGE)
const tableHeight = ref(0)
const { user } = useStore()

const settingTags = reactive([
  {
    label: t('views.knowledge.title'),
    value: AuthorizationEnum.KNOWLEDGE,
    data: [] as any,
  },
  {
    label: t('views.application.title'),
    value: AuthorizationEnum.APPLICATION,
    data: [] as any,
  },
])

watch(filterText, (val: any) => {
  if (val) {
    filterMember.value = memberList.value.filter((v: any) =>
      v.username.toLowerCase().includes(val.toLowerCase()),
    )
  } else {
    filterMember.value = memberList.value
  }
})

function isManage(type: string) {
  return type === 'manage'
}

const flotTree = (tree: Array<any>, result: Array<any>) => {
  tree.forEach((tItem) => {
    result.push(tItem)
    if (tItem.children) {
      flotTree(tItem.children, result)
    }
  })
  return result
}
function submitPermissions() {
  const user_resource_permission_list = settingTags
    .map((item: any) => {
      return flotTree(item.data, [])
        .filter((v: any) => !v.isFolder)
        .map((v: any) => {
          return {
            target_id: v.id,
            auth_target_type: item.value,
            permission: v.permission,
            auth_type: 'RESOURCE_PERMISSION_GROUP',
          }
        })
    })
    .reduce((pre, next) => {
      return [...pre, ...next]
    }, [])
  AuthorizationApi.putResourceAuthorization(
    currentWorkspaceId.value || 'default',
    currentUser.value,
    { user_resource_permission_list: user_resource_permission_list },
    rLoading,
  ).then(() => {
    MsgSuccess(t('common.submitSuccess'))
    getWholeTree(currentUser.value)
  })
}

function clickMemberHandle(item: any) {
  currentUser.value = item.id
  currentType.value = item.type
  getWholeTree(item.id)
}

function getMember(id?: string) {
  AuthorizationApi.getUserMember(currentWorkspaceId.value || 'default', loading).then((res) => {
    memberList.value = res.data
    filterMember.value = res.data

    const user = (id && memberList.value.find((p: any) => p.user_id === id)) || null
    currentUser.value = user ? user.id : memberList.value[0].id
    currentType.value = user ? user.type : memberList.value[0].type
    getWholeTree(currentUser.value)
  })
}

const dfsPermissionIndeterminateTrue = (arr: any = [], type: string) => {
  return arr.every((item: any) => {
    if (item.children?.length) {
      item.permission[type] = dfsPermissionIndeterminateTrue(item.children, type)
    }
    return item.permission[type]
  })
}

const dfsPermissionIndeterminate = (
  arr: any = [],
  type: string,
  permissionHalf: any,
  permissionHalfMap: any,
  id: string,
) => {
  arr.forEach((item: any) => {
    if (item.isFolder) {
      if (!permissionHalfMap[item.id]) {
        permissionHalfMap[item.id] = cloneDeep(permissionHalf)
      }
    }

    if (item.children?.length) {
      dfsPermissionIndeterminate(item.children, type, permissionHalf, permissionHalfMap, item.id)
    }

    if (!item.isFolder) {
      permissionHalfMap[id][type] = [...permissionHalfMap[id][type], item.permission[type]]
    }

    if (item.isFolder) {
      item.permissionHalf[type] = permissionHalfMap[item.id][type].length
        ? new Set(permissionHalfMap[item.id][type]).size > 1
        : false
      if (item.children.some((ele: any) => ele.isFolder && ele.permissionHalf[type])) {
        item.permissionHalf[type] = true
      }

      if (
        item.children.some((ele: any) => ele.permission[type]) &&
        item.children.some((ele: any) => !ele.permission[type])
      ) {
        item.permissionHalf[type] = true
      }
    }
  })
}

const dfsFolder = (arr: any[] = [], folderIdMap: any) => {
  arr.forEach((ele) => {
    if (ele.permission) return
    if (ele.children?.length) {
      if (folderIdMap[ele.id]) {
        ele.children = [...ele.children, ...folderIdMap[ele.id]]
      }
      dfsFolder(ele.children, folderIdMap)
    } else {
      ele.children = folderIdMap[ele.id] || []
    }
    ele.isFolder = true
    ele.permission = {
      VIEW: false,
      MANAGE: false,
      ROLE: false,
    }

    ele.permissionHalf = {
      VIEW: false,
      MANAGE: false,
      ROLE: false,
    }
  })
}

function getFolder() {
  return AuthorizationApi.getSystemFolder(
    currentWorkspaceId.value || 'default',
    'KNOWLEDGE',
    {},
    loading,
  )
}
function getResourcePermissions(user_id: string) {
  return AuthorizationApi.getResourceAuthorization(
    currentWorkspaceId.value || 'default',
    user_id,
    rLoading,
  )
}
const getWholeTree = async (user_id: string) => {
  const [parentRes, childrenRes] = await Promise.all([getFolder(), getResourcePermissions(user_id)])
  if (!childrenRes.data || Object.keys(childrenRes.data).length > 0) {
    settingTags.map((item: any) => {
      let folderIdMap = []
      const folderTree = cloneDeep((parentRes as unknown as any).data)
      if (Object.keys(childrenRes.data).indexOf(item.value) !== -1) {
        folderIdMap = getFolderIdMap(childrenRes.data[item.value])
        dfsFolder(folderTree, folderIdMap)
        const permissionHalf = {
          VIEW: [],
          MANAGE: [],
          ROLE: [],
        }
        Object.keys(permissionHalf).forEach((ele) => {
          dfsPermissionIndeterminateTrue(folderTree, ele)
          dfsPermissionIndeterminate(folderTree, ele, cloneDeep(permissionHalf), {}, 'default')
        })
        item.data = folderTree
      }
    })
  }
}

const refreshData = () => {
  settingTags.map((item: any) => {
    if (activeName.value === item.value) {
      const permissionHalf = {
        VIEW: [],
        MANAGE: [],
        ROLE: [],
      }
      Object.keys(permissionHalf).forEach((ele) => {
        dfsPermissionIndeterminateTrue(item.data, ele)
        dfsPermissionIndeterminate(item.data, ele, cloneDeep(permissionHalf), {}, 'default')
      })
    }
  })
}
const getFolderIdMap = (arr: any = []) => {
  return arr.reduce((pre: any, next: any) => {
    if (pre[next.folder_id]) {
      pre[next.folder_id].push(next)
    } else {
      pre[next.folder_id] = [next]
    }
    return pre
  }, {})
}
function ResourcePermissions(user_id: string) {
  AuthorizationApi.getResourceAuthorization(
    currentWorkspaceId.value || 'default',
    user_id,
    rLoading,
  ).then((res) => {
    if (!res.data || Object.keys(res.data).length > 0) {
      settingTags.map((item: any) => {
        if (Object.keys(res.data).indexOf(item.value) !== -1) {
          item.data = res.data[item.value]
          getFolderIdMap(item.data)
        }
      })
    }
  })
}

const workspaceList = ref<WorkspaceItem[]>([])
const currentWorkspaceId = ref<string | undefined>('')
const currentWorkspace = computed(() => {
  return workspaceList.value.find((w) => w.id == currentWorkspaceId.value)
})
async function getWorkspaceList() {
  if (user.isEE()) {
    const res = await WorkspaceApi.getSystemWorkspaceList(loading)
    workspaceList.value = res.data
    currentWorkspaceId.value = 'default'
  }
}

function changeWorkspace(item: WorkspaceItem) {
  currentWorkspaceId.value = item.id
  getMember()
}
function refresh(data?: string[]) {}

onMounted(() => {
  tableHeight.value = window.innerHeight - 330
  window.onresize = () => {
    return (() => {
      tableHeight.value = window.innerHeight - 330
    })()
  }
  getWorkspaceList()
  getMember()
})
</script>

<style lang="scss" scoped>
.resource-authorization {
  .resource-authorization__left {
    box-sizing: border-box;
    width: var(--setting-left-width);
    min-width: var(--setting-left-width);
  }

  .permission-setting {
    box-sizing: border-box;
    width: 100%;
    flex-direction: column;
    position: relative;
    .submit-button {
      position: absolute;
      top: 16px;
      right: 24px;
    }
  }
  .list-height-left {
    height: calc(100vh - 240px);
  }
}
</style>
