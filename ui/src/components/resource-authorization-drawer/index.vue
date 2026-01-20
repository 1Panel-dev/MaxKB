<template>
  <el-drawer
    v-model="drawerVisible"
    :title="$t('views.system.resourceAuthorization.title')"
    size="850"
    :append-to-body="true"
  >
    <div class="flex-between mb-16">
      <el-button
        type="primary"
        :disabled="multipleSelection.length === 0"
        @click="openMulConfigureDialog"
        >{{ $t('views.system.resourceAuthorization.setting.configure') }}</el-button
      >

      <div class="flex-between complex-search">
        <el-select
          class="complex-search__left"
          v-model="searchType"
          style="width: 100px"
          @change="search_type_change"
        >
          <el-option :label="$t('views.userManage.userForm.nick_name.label')" value="nick_name" />
          <el-option :label="$t('views.login.loginForm.username.label')" value="username" />
          <el-option :label="$t('views.model.modelForm.permissionType.label')" value="permission" />
          <el-option
            v-if="hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR')"
            :label="$t('views.role.member.role')"
            value="role"
          />
        </el-select>
        <el-input
          v-if="searchType === 'nick_name'"
          v-model="searchForm.nick_name"
          @change="searchHandle"
          :placeholder="$t('common.search')"
          style="width: 220px"
          clearable
        />
        <el-input
          v-if="searchType === 'username'"
          v-model="searchForm.username"
          @change="searchHandle"
          :placeholder="$t('common.search')"
          style="width: 220px"
          clearable
        />
        <el-input
          v-if="searchType === 'role'"
          v-model="searchForm.role"
          @change="searchHandle"
          :placeholder="$t('common.search')"
          style="width: 220px"
          clearable
        />
        <el-select
          v-else-if="searchType === 'permission'"
          v-model="searchForm.permission"
          @change="searchHandle"
          filterable
          clearable
          multiple
          :reserve-keyword="false"
          collapse-tags
          collapse-tags-tooltip
          style="width: 220px"
        >
          <template v-for="(item, index) in permissionOptions" :key="index">
            <el-option :label="item.label" :value="item.value" />
          </template>
        </el-select>
      </div>
    </div>

    <app-table
      ref="multipleTableRef"
      class="mt-16"
      :data="permissionData"
      :pagination-config="paginationConfig"
      @sizeChange="handleSizeChange"
      @changePage="getPermissionList"
      @selection-change="handleSelectionChange"
      :maxTableHeight="200"
      :row-key="(row: any) => row.id"
      v-loading="loading"
    >
      <el-table-column type="selection" width="55" :reserve-selection="true" />
      <el-table-column
        prop="nick_name"
        :label="$t('views.userManage.userForm.nick_name.label')"
        min-width="120"
        show-overflow-tooltip
      />
      <el-table-column
        prop="username"
        min-width="120"
        show-overflow-tooltip
        :label="$t('views.login.loginForm.username.label')"
      />
      <el-table-column
        v-if="hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR')"
        prop="role_name"
        :label="$t('views.role.member.role')"
        width="160"
      >
        <template #default="{ row }">
          <TagGroup class="cursor" style="width: fit-content" :tags="row.role_name" />
        </template>
      </el-table-column>
      <el-table-column :label="$t('common.operation')" align="left" width="340">
        <template #default="{ row }">
          <el-radio-group
            v-model="row.permission"
            @change="(val: any) => permissionsHandle(val, row)"
          >
            <template v-for="(item, index) in getFolderPermissionOptions()" :key="index">
              <el-radio :value="item.value" class="mr-16">{{ item.label }}</el-radio>
            </template>
          </el-radio-group>
        </template>
      </el-table-column>
    </app-table>
    <!-- 单个资源授权提示框 -->
    <el-dialog
      v-model="singleSelectDialogVisible"
      :title="$t('views.system.resourceAuthorization.setting.effectiveResource')"
      destroy-on-close
      @close="closeSingleSelectDialog"
      width="500px"
    >
      <el-radio-group v-model="authAllChildren" class="radio-block">
        <el-radio :value="false">
          <p class="color-text-primary lighter">
            {{ $t('views.system.resourceAuthorization.setting.currentOnly') }}
          </p>
        </el-radio>
        <el-radio :value="true">
          <p class="color-text-primary lighter">
            {{ $t('views.system.resourceAuthorization.setting.includeAll') }}
          </p>
        </el-radio>
      </el-radio-group>
      <template #footer>
        <div class="dialog-footer mt-24">
          <el-button @click="closeSingleSelectDialog">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="confirmSinglePermission">{{
            $t('common.confirm')
          }}</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 批量配置 弹出层 -->
    <el-dialog
      v-model="dialogVisible"
      :title="$t('views.system.resourceAuthorization.setting.configure')"
      destroy-on-close
      @close="closeDialog"
      width="500px"
    >
      <el-radio-group v-model="radioPermission" class="radio-block">
        <template v-for="(item, index) in getFolderPermissionOptions()" :key="index">
          <el-radio :value="item.value" class="mr-16">
            <p class="color-text-primary lighter">{{ item.label }}</p>
            <el-text class="color-secondary lighter">{{ item.desc }}</el-text>
          </el-radio>
        </template>
      </el-radio-group>
      <!-- 如果是文件夹，显示子资源选项 -->
      <div v-if="isFolder" class="mt-16">
        <el-divider />
        <div class="color-text-primary mb-8">
          {{ $t('views.system.resourceAuthorization.setting.effectiveResource') }}
        </div>
        <el-radio-group v-model="batchAuthAllChildren" class="radio-block">
          <el-radio :value="false">
            <p class="color-text-primary lighter">
              {{ $t('views.system.resourceAuthorization.setting.currentOnly') }}
            </p>
          </el-radio>
          <el-radio :value="true">
            <p class="color-text-primary lighter">
              {{ $t('views.system.resourceAuthorization.setting.includeAll') }}
            </p>
          </el-radio>
        </el-radio-group>
      </div>
      <template #footer>
        <div class="dialog-footer mt-24">
          <el-button @click="closeDialog"> {{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="submitDialog"> {{ $t('common.confirm') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, onMounted, watch, computed, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { getPermissionOptions } from '@/views/system/resource-authorization/constant'
import AuthorizationApi from '@/api/system/resource-authorization'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import permissionMap from '@/permission'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
const route = useRoute()
import useStore from '@/stores'
import { hasPermission } from '@/utils/permission/index'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'

const { user } = useStore()
const props = defineProps<{
  type: string
  isFolder?: boolean
  isRootFolder?: boolean
}>()

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const folderType = computed(() => {
  if (route.path.includes('application')) {
    return 'application'
  } else if (route.path.includes('knowledge')) {
    return 'knowledge'
  } else if (route.path.includes('tool')) {
    return 'tool'
  } else {
    return 'application'
  }
})

const permissionPrecise = computed(() => {
  return permissionMap[folderType.value!]['workspace']
})

// 取出文件夹id
function getAllFolderIds(data: any) {
  if (!data) return []
  return [data.id, ...(data.children?.flatMap((child: any) => getAllFolderIds(child)) || [])]
}

const RESOURCE_PERMISSION_MAP = {
  application:
    PermissionConst.APPLICATION_RESOURCE_AUTHORIZATION.getWorkspacePermissionWorkspaceManageRole,
  knowledge:
    PermissionConst.KNOWLEDGE_RESOURCE_AUTHORIZATION.getWorkspacePermissionWorkspaceManageRole,
  tool: PermissionConst.TOOL_RESOURCE_AUTHORIZATION.getWorkspacePermissionWorkspaceManageRole,
}

const resourceAuthorizationOfManager = computed(() => {
  return RESOURCE_PERMISSION_MAP[folderType.value]
})

// 过滤没有Manage权限的文件夹ID
function filterHasPermissionFolderIds(folderIds: string[]) {
  if (
    hasPermission(
      [RoleConst.WORKSPACE_MANAGE.getWorkspaceRole, resourceAuthorizationOfManager.value],
      'OR',
    )
  ) {
    return folderIds
  } else {
    return folderIds.filter((id) => permissionPrecise.value.folderManage(id))
  }
}

function confirmSinglePermission() {
  if (!pendingPermissionChange.value) return
  const { val, row } = pendingPermissionChange.value
  let folderIds: string[] = []
  if (authAllChildren.value && folderData.value) {
    const allFolderIds = getAllFolderIds(folderData.value)
    folderIds = filterHasPermissionFolderIds(allFolderIds)
  }
  const obj = [
    {
      user_id: row.id,
      permission: val,
      include_children: authAllChildren.value,
      ...(folderIds.length > 0 && { folder_ids: folderIds }),
    },
  ]
  submitPermissions(obj)
  singleSelectDialogVisible.value = false
  authAllChildren.value = false
  pendingPermissionChange.value = null
  getPermissionList()
}

const permissionOptionMap = computed(() => {
  return {
    rootFolder: getPermissionOptions(true, true),
    folder: getPermissionOptions(false, false),
  }
})

const getFolderPermissionOptions = () => {
  if (props.isRootFolder) {
    return permissionOptionMap.value.rootFolder
  }
  if (props.isFolder) {
    return permissionOptionMap.value.folder
  }
  return getPermissionOptions(false, false)
}

const permissionOptions = computed(() => {
  return getPermissionOptions()
})
const drawerVisible = ref(false)
const multipleTableRef = ref()

watch(drawerVisible, (bool) => {
  if (!bool) {
    targetId.value = ''
    searchType.value = 'nick_name'
    searchForm.value = { nick_name: '', username: '', permission: undefined }
    permissionData.value = []
    paginationConfig.current_page = 1
    paginationConfig.total = 0
    multipleSelection.value = []
    multipleTableRef.value?.clearSelection()
  }
})

const loading = ref(false)
const targetId = ref('')
const folderData = ref<any>(null)
const permissionData = ref<any[]>([])
const searchType = ref('nick_name')
const searchForm = ref<any>({
  nick_name: '',
  username: '',
  role: '',
  permission: undefined,
})

const search_type_change = () => {
  searchForm.value = { nick_name: '', username: '', role: '', permission: undefined }
}

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

function handleSizeChange() {
  paginationConfig.current_page = 1
  getPermissionList()
}
function searchHandle() {
  paginationConfig.current_page = 1
  getPermissionList()
}

const multipleSelection = ref<any[]>([])

const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
}

const dialogVisible = ref(false)
const singleSelectDialogVisible = ref(false)
const pendingPermissionChange = ref<{ val: any; row: any } | null>(null)
const radioPermission = ref('')
const authAllChildren = ref(false)
function openMulConfigureDialog() {
  if (multipleSelection.value.length === 0) {
    return
  }
  dialogVisible.value = true
}

const batchAuthAllChildren = ref(false)
function submitDialog() {
  if (multipleSelection.value.length === 0 || !radioPermission.value) {
    return
  }
  let folderIds: string[] = []
  if (props.isFolder && batchAuthAllChildren.value && folderData.value) {
    const allFolderIds = getAllFolderIds(folderData.value)
    folderIds = filterHasPermissionFolderIds(allFolderIds)
  }

  const obj = multipleSelection.value.map((item) => ({
    user_id: item.id,
    permission: radioPermission.value,
    include_children: batchAuthAllChildren.value,
    ...(folderIds.length > 0 && { folder_ids: folderIds }),
  }))
  submitPermissions(obj)
  closeDialog()
}

function closeSingleSelectDialog() {
  singleSelectDialogVisible.value = false
  authAllChildren.value = false
  pendingPermissionChange.value = null
  getPermissionList()
}

function closeDialog() {
  dialogVisible.value = false
  radioPermission.value = ''
  batchAuthAllChildren.value = false
  multipleSelection.value = []
  multipleTableRef.value?.clearSelection()
}

function permissionsHandle(val: any, row: any) {
  if (props.isFolder) {
    singleSelectDialogVisible.value = true
    pendingPermissionChange.value = { val, row }
    return
  }
  const obj = [
    {
      user_id: row.id,
      permission: val,
    },
  ]
  submitPermissions(obj)
}

function submitPermissions(obj: any) {
  const workspaceId = user.getWorkspaceId() || 'default'
  loadSharedApi({ type: 'resourceAuthorization', systemType: apiType.value })
    .putResourceAuthorization(workspaceId, targetId.value, props.type, obj, loading)
    .then(() => {
      MsgSuccess(t('common.submitSuccess'))
      getPermissionList()
    })
}
const getPermissionList = () => {
  const workspaceId = user.getWorkspaceId() || 'default'
  const params: any = {}
  if (searchForm.value[searchType.value]) {
    params[searchType.value] = searchForm.value[searchType.value]
  }
  loadSharedApi({ type: 'resourceAuthorization', systemType: apiType.value })
    .getResourceAuthorization(
      workspaceId,
      targetId.value,
      props.type,
      paginationConfig,
      params,
      loading,
    )
    .then((res: any) => {
      permissionData.value =
        res.data.records.map((item: any) => {
          if (props.isRootFolder && item.permission === 'NOT_AUTH') {
            return { ...item, permission: 'VIEW' }
          }
          return item
        }) || []
      paginationConfig.total = res.data.total || 0
    })
}

const open = (id: string, folder_data?: any) => {
  targetId.value = id
  folderData.value = folder_data
  drawerVisible.value = true
  getPermissionList()
}
defineExpose({
  open,
})
</script>
<style lang="scss" scoped></style>
