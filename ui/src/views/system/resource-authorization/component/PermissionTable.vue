<template>
  <div class="permission-setting p-24 flex">
    <div class="resource-authorization__table">
      <h4 class="mb-16">{{ $t('views.system.resourceAuthorization.permissionSetting') }}</h4>
      <div class="flex-between mb-16">
        <el-button
          type="primary"
          v-if="
            hasPermission(permissionObj[(route.meta?.resource as string) || 'APPLICATION'], 'OR')
          "
          :disabled="multipleSelection.length === 0"
          @click="openMulConfigureDialog"
          >{{ $t('views.system.resourceAuthorization.setting.configure') }}</el-button
        >

        <div class="flex-between complex-search">
          <el-select
            class="complex-search__left"
            v-model="searchType"
            style="width: 80px"
            @change="search_type_change"
          >
            <el-option :label="$t('common.name')" value="name" />
            <el-option
              :label="$t('views.model.modelForm.permissionType.label')"
              value="permission"
            />
          </el-select>
          <el-input
            v-if="searchType === 'name'"
            v-model="searchForm.name"
            :placeholder="$t('common.searchBar.placeholder')"
            style="width: 220px"
            clearable
          />
          <el-select
            v-else-if="searchType === 'permission'"
            v-model="searchForm.permission"
            filterable
            clearable
            multiple
            :reserve-keyword="false"
            collapse-tags
            collapse-tags-tooltip
            style="width: 220px"
          >
            <template v-for="(item, index) in getPermissionOptions()" :key="index">
              <el-option :label="item.label" :value="item.value" />
            </template>
          </el-select>
        </div>
      </div>

      <app-table
        ref="multipleTableRef"
        class="mt-16"
        :data="filteredData"
        @select="select"
        @select-all="selectAll"
        :maxTableHeight="260"
        :row-key="(row: any) => row.id"
        style="min-width: 600px"
        :expand-row-keys="defaultExpandKeys"
        :default-expand-all="searchForm.name || searchForm.permission?.length > 0"
        show-overflow-tooltip
      >
        <el-table-column type="selection" width="55" :reserve-selection="true"> </el-table-column>
        <el-table-column prop="name" :label="$t('common.name')">
          <template #default="{ row }">
            <span style="vertical-align: sub">
              <!--  文件夹 icon -->
              <AppIcon
                v-if="row.resource_type === 'folder'"
                iconName="app-folder"
                style="font-size: 20px"
              ></AppIcon>
              <!--  知识库 icon -->
              <KnowledgeIcon :size="20" v-else-if="isKnowledge" :type="row.icon" />
              <!--  应用/工具 自定义 icon -->
              <el-avatar
                v-else-if="isAppIcon(row?.icon) && !isModel"
                style="background: none"
                shape="square"
                :size="20"
              >
                <img :src="resetUrl(row?.icon)" alt="" />
              </el-avatar>
              <!--  应用 icon -->
              <LogoIcon v-else-if="isApplication" height="20px" />
              <!-- 工具 icon -->
              <ToolIcon v-else-if="isTool" :size="20" :type="row?.tool_type" />
              <!-- 模型 icon -->
              <span
                v-else-if="isModel"
                style="width: 20px; height: 20px; display: inline-block"
                :innerHTML="getProviderIcon(row)"
              ></span>
            </span>
            {{ row?.name }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('views.model.modelForm.permissionType.label')" align="left">
          <template #default="{ row }">
            <el-radio-group
              v-model="row.permission"
              @change="(val: any) => submitPermissions(val, row)"
            >
              <template v-for="(item, index) in getRowPermissionOptions(row)" :key="index">
                <el-radio :value="item.value" class="mr-16">{{ item.label }}</el-radio>
              </template>
            </el-radio-group>
          </template>
        </el-table-column>
      </app-table>
    </div>

    <!-- 批量配置 弹出层 -->
    <el-dialog
      v-model="dialogVisible"
      :title="$t('views.system.resourceAuthorization.setting.configure')"
      destroy-on-close
      @close="closeDialog"
    >
      <el-radio-group v-model="radioPermission" class="radio-block">
        <template v-for="(item, index) in permissionOptions" :key="index">
          <el-radio :value="item.value" class="mr-16">
            <p class="color-text-primary lighter">{{ item.label }}</p>
            <el-text class="color-secondary lighter">{{ item.desc }}</el-text>
          </el-radio>
        </template>
      </el-radio-group>
      <template #footer>
        <div class="dialog-footer mt-24">
          <el-button @click="closeDialog"> {{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="submitDialog"> {{ $t('common.confirm') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { Provider } from '@/api/type/model'
import { SourceTypeEnum } from '@/enums/common'
import { isAppIcon, resetUrl } from '@/utils/common'
import { RoleConst, PermissionConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { getPermissionOptions } from '@/views/system/resource-authorization/constant'
import useStore from '@/stores'
import { TreeToFlatten } from '@/utils/array'

const { model, user } = useStore()
const route = useRoute()
const props = defineProps<{
  data: any[]
  type: string
  getData?: () => void
}>()
const emit = defineEmits(['submitPermissions'])

const defaultExpandKeys = ref<Array<string>>([])
const isComputedFirst = ref(true) // 仅第一次获得数据的时候需要计算一次展开属性

watch(
  () => props.data,
  (newData) => {
    if (newData && newData.length > 0 && isComputedFirst.value) {
      defaultExpandKeys.value = props.data?.length > 0 ? [props.data[0]?.id] : []
      isComputedFirst.value = false
    }
  },
  { immediate: true },
)

// const defaultExpandKeys = computed(() => {
// const searchName = searchForm.value.name || ''
// const searchPermissions = searchForm.value.permission ?? []
// if (!searchName && (!searchPermissions || searchPermissions.length === 0)) {
// return props.data?.length > 0 ? [props.data[0]?.id] : []

// }
// const expandIds: string[] = []
// // 传入过滤后的数据
// const collectExpandIds = (nodes: any[]) => {
//   nodes.forEach((node) => {
//     if (node.children && node.children.length > 0) {
//       expandIds.push(node.id)
//       collectExpandIds(node.children)
//     }
//   })
// }
// collectExpandIds(filteredData.value)
// return expandIds
// })

const permissionOptionMap = computed(() => {
  return {
    rootFolder: getPermissionOptions(true, true),
    folder: getPermissionOptions(true, false),
    resource: getPermissionOptions(false, false),
  }
})

const getRowPermissionOptions = (row: any) => {
  const isFolder = row.resource_type === 'folder'
  const isRoot = isFolder && row.folder_id === null
  if (isRoot) {
    return permissionOptionMap.value.rootFolder
  }
  if (isFolder) {
    return permissionOptionMap.value.folder
  }
  return permissionOptionMap.value.resource
}

const permissionOptions = computed(() => {
  if (
    multipleSelection.value.some(
      (item) => item.resource_type === 'folder' && item.folder_id == null,
    )
  ) {
    return permissionOptionMap.value.rootFolder
  } else if (multipleSelection.value.some((item) => item.resource_type === 'folder')) {
    return permissionOptionMap.value.folder
  } else {
    return permissionOptionMap.value.resource
  }
})
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
const isKnowledge = computed(() => props.type === SourceTypeEnum.KNOWLEDGE)
const isApplication = computed(() => props.type === SourceTypeEnum.APPLICATION)
const isTool = computed(() => props.type === SourceTypeEnum.TOOL)
const isModel = computed(() => props.type === SourceTypeEnum.MODEL)

const multipleTableRef = ref()
const searchType = ref('name')
const searchForm = ref<any>({
  name: '',
  permission: undefined,
})

const search_type_change = () => {
  searchForm.value = { name: '', permission: undefined }
}

const filterTreeData = () => {
  const searchName = searchForm.value.name || ''
  const searchPermissions = searchForm.value.permission ?? []

  if (!searchName && (!searchPermissions || searchPermissions.length === 0)) {
    return props.data
  }

  const filterNodes = (treeData: any[], name: string, permissions: any[]): any[] => {
    if (!treeData || treeData.length === 0) return []

    const result: any[] = []

    for (const node of treeData) {
      const cloneNode = { ...node }

      let isMatch = false
      if (searchType.value === 'name') {
        isMatch = node.name.toLowerCase().includes(name.toLowerCase())
      } else if (searchType.value === 'permission') {
        isMatch = node.permission && permissions.includes(node.permission)
      }

      let filteredChildren: any[] = []
      if (node.children && node.children.length > 0) {
        filteredChildren = filterNodes(node.children, name, permissions)
      }
      if (isMatch || filteredChildren.length > 0) {
        cloneNode.children = filteredChildren
        result.push(cloneNode)
      }
    }
    return result
  }
  return filterNodes(props.data, searchName, searchPermissions)
}

const filteredData = computed(() => {
  return filterTreeData()
})

const multipleSelection = ref<any[]>([])
const selectObj: any = {}
const selectAll = (selection: any[]) => {
  multipleSelection.value = selection
}
const select = (val: any[], active: any) => {
  if (active.resource_type === 'folder') {
    if (!val.some((item) => item.id == active.id)) {
      if (selectObj[active.id] === undefined) {
        selectObj[active.id] = 0
      }
      if (selectObj[active.id] % 2 == 0) {
        TreeToFlatten([active])
          .filter((item: any) => item.id != active.id)
          .forEach((item: any) => {
            if (multipleSelection.value.some((select) => item.id == select.id)) {
              multipleTableRef.value?.toggleRowSelection(item, true)
            }
          })
        multipleSelection.value = multipleTableRef.value.getSelectionRows()
      } else {
        multipleSelection.value = val
      }
      selectObj[active.id] = selectObj[active.id] + 1
    } else {
      multipleSelection.value = val
    }
  } else {
    multipleSelection.value = val
  }
}
const dialogVisible = ref(false)
const radioPermission = ref('')
function openMulConfigureDialog() {
  if (multipleSelection.value.length === 0) {
    return
  }
  dialogVisible.value = true
}
function submitDialog() {
  if (multipleSelection.value.length === 0 || !radioPermission.value) {
    return
  }
  const obj = multipleSelection.value.map((item) => ({
    target_id: item.id,
    permission: radioPermission.value,
  }))
  emit('submitPermissions', obj)
  closeDialog()
}
function closeDialog() {
  dialogVisible.value = false
  radioPermission.value = ''
  multipleSelection.value = []
  multipleTableRef.value?.clearSelection()
}

function submitPermissions(value: string, row: any) {
  const obj = [
    {
      target_id: row.id,
      permission: value,
    },
  ]
  const emitSubmitPermissions = (treeData: any[], ids: Array<string>, result: Array<any>) => {
    if (!treeData || treeData.length === 0) return []
    for (const node of treeData) {
      const isRecursion = node.permission == 'NOT_AUTH' && ids.includes(node.id)
      if (node.children && node.children.length > 0 && !isRecursion) {
        emitSubmitPermissions(node.children, ids, result)
      }
      const isMatch = node.permission == 'NOT_AUTH' && ids.includes(node.id)
      if (isMatch) {
        ids.push(node.folder_id)
        result.push({
          target_id: node.id,
          permission: 'VIEW',
        })
      }
    }
    return result
  }
  if (['VIEW', 'MANAGE', 'ROLE'].includes(value)) {
    emitSubmitPermissions(props.data, [row.folder_id], obj)
  }
  emit('submitPermissions', obj)
}
const provider_list = ref<Array<Provider>>([])

function getProvider() {
  model.asyncGetProvider().then((res: any) => {
    provider_list.value = res?.data
  })
}

const getProviderIcon = computed(() => {
  return (row: any) => {
    return provider_list.value.find((p) => p.provider === row.icon)?.icon
  }
})
onMounted(() => {
  if (isModel.value) {
    getProvider()
  }
})

defineExpose({
  searchForm,
  searchType,
})
</script>
<style lang="scss" scoped>
.permission-setting {
  flex: 1;
  overflow: hidden;
  box-sizing: border-box;
  width: 100%;
  flex-direction: column;
}
</style>
