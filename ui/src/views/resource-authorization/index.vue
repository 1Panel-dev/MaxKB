<template>
  <div class="resource-authorization p-16-24">
    <h2 class="mb-16">{{ $t('views.userManage.title') }}</h2>
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
                    <div>
                      <span class="mr-8">{{ row.nick_name }}</span>
                      <el-tag v-if="isManage(row.type)" class="default-tag">{{
                        $t('views.resourceAuthorization.manage')
                      }}</el-tag>
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
import { onMounted, ref, reactive, watch } from 'vue'
import AuthorizationApi from '@/api/user/resource-authorization'
import PermissionSetting from './component/PermissionSetting.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { AuthorizationEnum } from '@/enums/system'
import { t } from '@/locales'
import useStore from '@/stores'
import { cloneDeep } from 'lodash'

const loading = ref(false)
const rLoading = ref(false)
const memberList = ref<any[]>([]) // 全部成员
const filterMember = ref<any[]>([]) // 搜索过滤后列表
const currentUser = ref<string>('')
const currentType = ref<string>('')
const filterText = ref('')

const activeName = ref(AuthorizationEnum.KNOWLEDGE)
const tableHeight = ref(0)
const { folder } = useStore()

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

function submitPermissions() {
  const obj: any = {
    user_resource_permission_list: [],
  }
  settingTags.map((item: any) => {
    item.data.map((v: any) => {
      obj['user_resource_permission_list'].push({
        target_id: v.id,
        auth_target_type: v.auth_target_type,
        permission: v.permission,
        auth_type: 'RESOURCE_PERMISSION_GROUP',
      })
    })
  })
  AuthorizationApi.putResourceAuthorization(currentUser.value, obj, rLoading).then(() => {
    MsgSuccess(t('common.submitSuccess'))
    ResourcePermissions(currentUser.value)
  })
}

function clickMemberHandle(item: any) {
  currentUser.value = item.id
  currentType.value = item.type
  ResourcePermissions(item.id)
}

function getMember(id?: string) {
  AuthorizationApi.getUserMember(loading).then((res) => {
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
  return folder.asyncGetFolder('KNOWLEDGE', {}, loading)
}

function getResourcePermissions(user_id: string) {
  return AuthorizationApi.getResourceAuthorization(user_id, rLoading)
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
  AuthorizationApi.getResourceAuthorization(user_id, rLoading).then((res) => {
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

function refresh(data?: string[]) {}

onMounted(() => {
  tableHeight.value = window.innerHeight - 330
  window.onresize = () => {
    return (() => {
      tableHeight.value = window.innerHeight - 330
    })()
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
