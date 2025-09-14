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
            @change="searchHandle"
            :placeholder="$t('common.searchBar.placeholder')"
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
        :data="props.data"
        :pagination-config="paginationConfig"
        @sizeChange="handleSizeChange"
        @changePage="props.getData"
        @selection-change="handleSelectionChange"
        :maxTableHeight="320"
        :row-key="(row: any) => row.id"
      >
        <el-table-column type="selection" width="55" :reserve-selection="true" />
        <el-table-column prop="name" :label="$t('common.name')">
          <template #default="{ row }">
            <el-space :size="8">
              <!--  知识库 icon -->
              <KnowledgeIcon :size="20" v-if="isKnowledge" :type="row.icon" />
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
              <span :title="row?.name" class="ellipsis-1">
                {{ row?.name }}
              </span>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column :label="$t('views.model.modelForm.permissionType.label')" align="left">
          <template #default="{ row }">
            <el-radio-group
              v-model="row.permission"
              @change="(val: any) => submitPermissions(val, row)"
            >
              <template v-for="(item, index) in permissionOptions" :key="index">
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
import { ref, onMounted, watch, computed, reactive } from 'vue'
import { useRoute } from 'vue-router'
import type { Provider } from '@/api/type/model'
import { SourceTypeEnum } from '@/enums/common'
import { isAppIcon, resetUrl } from '@/utils/common'
import { RoleConst, PermissionConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
import { getPermissionOptions } from '@/views/system/resource-authorization/constant'
import useStore from '@/stores'

const { model, user } = useStore()
const route = useRoute()
const props = defineProps<{
  data: any[]
  type: string
  getData?: () => void
}>()
const emit = defineEmits(['submitPermissions'])

const permissionOptions = computed(() => {
  return getPermissionOptions()
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

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

function handleSizeChange() {
  paginationConfig.current_page = 1
  if (props.getData) {
    props.getData()
  }
}
function searchHandle() {
  paginationConfig.current_page = 1
  if (props.getData) {
    props.getData()
  }
}

const multipleSelection = ref<any[]>([])

const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
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
  paginationConfig,
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
