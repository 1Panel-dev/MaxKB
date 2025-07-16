<template>
  <div class="resource-authorization p-16-24">
    <div class="flex align-center mb-16">
      <el-breadcrumb separator-icon="ArrowRight">
        <el-breadcrumb-item>{{ t('views.system.resourceAuthorization.title') }}</el-breadcrumb-item>
        <el-breadcrumb-item>
          <h5 class="ml-4 color-text-primary">{{ activeData.label }}</h5>
        </el-breadcrumb-item>
      </el-breadcrumb>
      <!-- 企业版: 工作空间下拉框-->
      <el-divider
        class="ml-24"
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
        <div class="resource-authorization__left border-r">
          <div class="p-24 pb-0">
            <h4 class="mb-12">{{ $t('views.system.resourceAuthorization.member') }}</h4>
            <el-input
              v-model="filterText"
              :placeholder="$t('common.search')"
              prefix-icon="Search"
              clearable
            />
          </div>
          <div class="list-height-left">
            <el-scrollbar>
              <div class="p-8-16">
                <common-list
                  :data="filterMember"
                  v-loading="loading"
                  @click="clickMemberHandle"
                  :default-active="currentUser"
                >
                  <template #default="{ row }">
                    <div class="flex-between">
                      <div class="flex">
                        <span class="mr-8">{{ row.nick_name }}</span>
                        <TagGroup
                          :tags="row.roles"
                          v-if="hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR')"
                        />
                      </div>
                    </div>
                  </template>
                </common-list>
              </div>
            </el-scrollbar>
          </div>
        </div>
        <div class="permission-setting p-24 flex" v-loading="rLoading">
          <div class="resource-authorization__table">
            <h4 class="mb-16">{{ $t('views.system.resourceAuthorization.permissionSetting') }}</h4>
            <!-- <el-tabs
              v-model="activeName"
              @tab-change="handleTabChange"
              class="resource-authorization__tabs"
            >
              <el-tab-pane
                v-for="(item, index) in settingTags"
                :key="item.value"
                :label="item.label"
                :name="item.value"
              > -->
            <PermissionSetting
              :data="activeData.data"
              :type="activeData.type"
              :tableHeight="tableHeight"
              :manage="isManage(currentType)"
              @refreshData="refreshData"
              v-model:isRole="activeData.isRole"
            ></PermissionSetting>
            <!-- </el-tab-pane> -->
            <!-- </el-tabs> -->
          </div>

          <div class="submit-button">
            <el-button
              type="primary"
              @click="submitPermissions"
              v-if="
                hasPermission(
                  permissionObj[(route.meta?.resource as string) || 'APPLICATION'],
                  'OR',
                )
              "
              >{{ $t('common.save') }}</el-button
            >
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import AuthorizationApi from '@/api/system/resource-authorization'
import PermissionSetting from './component/PermissionSetting.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { AuthorizationEnum } from '@/enums/system'
import { t } from '@/locales'
import useStore from '@/stores'
import { cloneDeep } from 'lodash'
import { EditionConst, RoleConst, PermissionConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import type { WorkspaceItem } from '@/api/type/workspace'
import { ComplexPermission } from '@/utils/permission/type'
import { loadPermissionApi } from '@/utils/dynamics-api/permission-api.ts'

const route = useRoute()
const { user } = useStore()
const loading = ref(false)
const rLoading = ref(false)
const memberList = ref<any[]>([]) // 全部成员
const filterMember = ref<any[]>([]) // 搜索过滤后列表
const currentUser = ref<string>('')
const currentType = ref<string>('')
const filterText = ref('')
const tableHeight = ref(0)

const permissionObj = ref<any>({
  APPLICATION: new ComplexPermission(
    [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
    [
      PermissionConst.APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT,
      PermissionConst.APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT
        .getWorkspacePermissionWorkspaceManageRole,
    ],
    [],
    'OR',
  ),
  KNOWLEDGE: new ComplexPermission(
    [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
    [
      PermissionConst.KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT,
      PermissionConst.KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT
        .getWorkspacePermissionWorkspaceManageRole,
    ],
    [],
    'OR',
  ),
  TOOL: new ComplexPermission(
    [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
    [
      PermissionConst.TOOL_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT,
      PermissionConst.TOOL_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT
        .getWorkspacePermissionWorkspaceManageRole,
    ],
    [],
    'OR',
  ),
  MODEL: new ComplexPermission(
    [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
    [
      PermissionConst.MODEL_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT,
      PermissionConst.MODEL_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT
        .getWorkspacePermissionWorkspaceManageRole,
    ],
    [],
    'OR',
  ),
})
const settingTags = reactive([
  {
    label: t('views.knowledge.title'),
    type: AuthorizationEnum.KNOWLEDGE,
    data: [] as any,
    isRole: false,
  },
  {
    label: t('views.application.title'),
    type: AuthorizationEnum.APPLICATION,
    data: [] as any,
    isRole: false,
  },
  {
    label: t('views.tool.title'),
    type: AuthorizationEnum.TOOL,
    data: [] as any,
    isRole: false,
  },
  {
    label: t('views.model.title'),
    type: AuthorizationEnum.MODEL,
    data: [] as any,
    isRole: false,
  },
])

// 当前激活的数据类型（应用/知识库/模型/工具）

const activeData = computed(() => {
  const lastIndex = route.path.lastIndexOf('/')
  const currentPathType = route.path.substring(lastIndex + 1).toUpperCase()
  return settingTags.filter((item) => {
    return item.type === currentPathType
  })[0]
})

watch(filterText, (val: any) => {
  if (val) {
    filterMember.value = memberList.value.filter((v: any) =>
      v.nick_name.toLowerCase().includes(val.toLowerCase()),
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
    .map((item: any, index: number) => {
      return flotTree(item.data, [])
        .filter((v: any) => !v.isFolder)
        .map((v: any) => {
          return {
            target_id: v.id,
            auth_target_type: item.value,
            permission: v.permission,
            auth_type: item.isRole ? 'ROLE' : 'RESOURCE_PERMISSION_GROUP',
          }
        })
    })
    .reduce((pre: any, next: any) => [...pre, ...next], [])
  const workspaceId = currentWorkspaceId.value || user.getWorkspaceId() || 'default'
  AuthorizationApi.putResourceAuthorization(
    workspaceId,
    currentUser.value,
    (route.meta?.resource as string) || 'APPLICATION',
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
  const workspaceId = currentWorkspaceId.value || user.getWorkspaceId() || 'default'
  AuthorizationApi.getUserMember(workspaceId, loading).then((res) => {
    memberList.value = res.data
    filterMember.value = res.data
    if (memberList.value.length > 0) {
      const member = (id && memberList.value.find((p: any) => p.user_id === id)) || null
      currentUser.value = member ? member.id : memberList.value?.[0]?.id
      currentType.value = member ? member.type : memberList.value?.[0]?.type
      getWholeTree(currentUser.value)
    } else {
      activeData.value.data = []
    }
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
      // 判断是否存在子项且全部选中或全部未选中
      const hasPermissions = permissionHalfMap[item.id][type]
      const allTrue = hasPermissions.length && hasPermissions.every((p: boolean) => p)
      const allFalse = hasPermissions.length && hasPermissions.every((p: boolean) => !p)

      // 只有在既有选中又有未选中的情况下才设置为半选状态
      item.permissionHalf[type] = hasPermissions.length && !allTrue && !allFalse

      // 检查子文件夹是否有半选状态
      if (item.children.some((ele: any) => ele.isFolder && ele.permissionHalf[type])) {
        item.permissionHalf[type] = true
      }

      // 如果所有子项都已选中，确保当前项也被选中而不是半选
      if (allTrue) {
        item.permission[type] = true
        item.permissionHalf[type] = false
      }

      // 如果子项中有选中的也有未选中的，则设置为半选状态
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
  const workspaceId = currentWorkspaceId.value || user.getWorkspaceId() || 'default'
  return AuthorizationApi.getSystemFolder(workspaceId, activeData.value.type, {}, loading)
}
function getResourcePermissions(user_id: string) {
  const workspaceId = currentWorkspaceId.value || user.getWorkspaceId() || 'default'
  return AuthorizationApi.getResourceAuthorization(
    workspaceId,
    user_id,
    (route.meta?.resource as string) || 'APPLICATION',
    rLoading,
  )
}
const getWholeTree = async (user_id: string) => {
  const [parentRes, childrenRes] = await Promise.all([getFolder(), getResourcePermissions(user_id)])
  // if (!childrenRes.data || Object.keys(childrenRes.data).length > 0) {
  // settingTags.map((item: any) => {
  let folderIdMap = []
  const folderTree = cloneDeep((parentRes as unknown as any).data)
  if (Object.keys(childrenRes.data).indexOf(activeData.value.type) !== -1) {
    activeData.value.isRole =
      childrenRes.data[activeData.value.type].length > 0 &&
      hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR')
        ? childrenRes.data[activeData.value.type][0].auth_type == 'ROLE'
        : false
    folderIdMap = getFolderIdMap(childrenRes.data[activeData.value.type])
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
    if (activeData.value.type === AuthorizationEnum.MODEL) {
      activeData.value.data = folderTree[0].children
    } else {
      activeData.value.data = folderTree
    }
  } else {
    activeData.value.data = []
  }
  // })
  // }
}

const refreshData = () => {
  settingTags.map((item: any) => {
    if (activeData.value.type === item.type) {
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

const workspaceList = ref<WorkspaceItem[]>([])
const currentWorkspaceId = ref<string | undefined>('')
const currentWorkspace = computed(() => {
  return workspaceList.value.find((w) => w.id == currentWorkspaceId.value)
})
async function getWorkspaceList() {
  const res = await loadPermissionApi('workspace').getSystemWorkspaceList(loading)
  workspaceList.value = res.data
  currentWorkspaceId.value = (user.getWorkspaceId() as string) || 'default'
}

function changeWorkspace(item: WorkspaceItem) {
  currentWorkspaceId.value = item.id
  getMember()
}

onMounted(() => {
  tableHeight.value = window.innerHeight - 300
  window.onresize = () => {
    return (() => {
      tableHeight.value = window.innerHeight - 300
    })()
  }
  if (user.isEE()) {
    getWorkspaceList()
  }
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
    flex: 1;
    overflow: hidden;
    box-sizing: border-box;
    width: 100%;
    flex-direction: column;
    position: relative;
    .submit-button {
      position: absolute;
      top: 24px;
      right: 24px;
    }
  }
  .list-height-left {
    height: calc(100vh - 240px);
  }
}
</style>
