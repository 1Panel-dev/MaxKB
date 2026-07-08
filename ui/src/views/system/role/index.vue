<template>
  <div class="role-manage p-16-24">
    <h2 class="mb-16">{{ $t('views.role.title') }}</h2>
    <el-card style="--el-card-padding: 0" class="main-calc-height">
      <div class="flex">
        <div class="role-left border-r">
          <div class="p-24 pb-0">
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
                <div class="color-secondary lighter ml-8 mb-8">
                  <span>{{ $t('views.role.internalRole') }}</span>
                </div>
                <common-list
                  :data="filterInternalRole"
                  @click="clickRole"
                  :default-active="currentRole?.id"
                  @mouseenter="mouseenter"
                  @mouseleave="mouseId = ''"
                >
                  <template #default="{ row }">
                    <span class="ellipsis-1" :title="row.role_name">{{ i18n_name(row.role_name) }}</span>
                  </template>
                  <template #empty>
                    <span></span>
                  </template>
                </common-list>

                <div class="ml-8 border-t flex-between mb-8" style="padding-top: 12px">
                  <span class="color-secondary lighter">{{ $t('views.role.customRole') }}</span>
                  <el-tooltip
                    effect="dark"
                    :content="`${$t('common.create')}${$t('views.role.customRole')}`"
                    placement="top"
                  >
                    <el-button
                      type="primary"
                      text
                      @click="createOrUpdateRole()"
                      v-hasPermission="
                        new ComplexPermission(
                          [RoleConst.ADMIN],
                          [PermissionConst.ROLE_CREATE],
                          [],
                          'OR',
                        )
                      "
                    >
                      <AppIcon iconName="app-add-outlined"></AppIcon>
                    </el-button>
                  </el-tooltip>
                </div>
                <common-list
                  :data="filterCustomRole"
                  @click="clickRole"
                  :default-active="currentRole?.id"
                  @mouseenter="mouseenter"
                  @mouseleave="mouseId = ''"
                >
                  <template #default="{ row }">
                    <div class="flex-between">
                      <span class="flex align-center mr-8">
                        <div class="ellipsis" style="flex: 1">{{ row.role_name }}</div>
                        <span class="color-input-placeholder ml-4"
                          >({{ roleTypeMap[row.type as RoleTypeEnum] }})</span
                        >
                      </span>
                      <div
                        @click.stop
                        v-show="mouseId === row.id"
                        v-if="editPermission() || delPermission()"
                      >
                        <el-dropdown :teleported="false" trigger="click">
                          <el-button text>
                            <AppIcon iconName="app-more"></AppIcon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu style="min-width: 80px">
                              <el-dropdown-item
                                @click.stop="createOrUpdateRole(row)"
                                class="p-8"
                                v-if="editPermission()"
                              >
                                <AppIcon iconName="app-edit" class="color-secondary"></AppIcon>
                                {{ $t('common.rename') }}
                              </el-dropdown-item>
                              <el-dropdown-item
                                @click.stop="deleteRole(row)"
                                class="border-t p-8"
                                v-if="delPermission()"
                              >
                                <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
                                {{ $t('common.delete') }}
                              </el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                    </div>
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
        <div class="role-right p-24" v-loading="loading">
          <div class="flex-between mb-16">
            <div class="flex align-center">
              <h4>
                {{ i18n_name(currentRole?.role_name as string) }}
              </h4>
              <span
                v-if="currentRole?.type && !currentRole.internal"
                class="color-input-placeholder ml-4"
                >({{ roleTypeMap[currentRole?.type as RoleTypeEnum] }})
              </span>

              <el-divider direction="vertical" />
              <el-icon class="color-input-placeholder"><UserFilled /></el-icon>
              <span class="color-input-placeholder ml-4">
                {{ currentRole?.user_count }}
              </span>
            </div>
            <el-radio-group v-model="currentTab" class="app-radio-button-group">
              <el-radio-button
                v-for="item in tabList"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-radio-group>
          </div>
          <PermissionConfiguration v-if="currentTab === 'permission'" :currentRole="currentRole" />
          <Member v-else :currentRole="currentRole" />
        </div>
      </div>
    </el-card>

    <CreateOrUpdateRoleDialog ref="createOrUpdateRoleDialogRef" @refresh="refresh" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch } from 'vue'
import { t } from '@/locales'
import { i18n_name } from '@/utils/common'
import PermissionConfiguration from './component/PermissionConfiguration.vue'
import Member from './component/Member.vue'
import CreateOrUpdateRoleDialog from './component/CreateOrUpdateRoleDialog.vue'
import type { RoleItem } from '@/api/type/role'
import { RoleTypeEnum } from '@/enums/system'
import { roleTypeMap } from './index'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { loadPermissionApi } from '@/utils/dynamics-api/permission-api'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'
import { hasPermission } from '@/utils/permission/index'

const filterText = ref('')
const loading = ref(false)
const internalRoleList = ref<RoleItem[]>([])
const filterInternalRole = ref<RoleItem[]>([]) // 搜索过滤后列表
const customRoleList = ref<RoleItem[]>([])
const filterCustomRole = ref<RoleItem[]>([]) // 搜索过滤后列表
const currentRole = ref<RoleItem>()

async function getRole() {
  try {
    const res = await loadPermissionApi('role').getRoleList(loading)
    internalRoleList.value = res.data.internal_role
    customRoleList.value = res.data.custom_role
    filterInternalRole.value = filter(internalRoleList.value, filterText.value)
    filterCustomRole.value = filter(customRoleList.value, filterText.value)
  } catch (error) {
    console.error(error)
  }
}

const editPermission = () => {
  return hasPermission(
    new ComplexPermission([RoleConst.ADMIN], [PermissionConst.ROLE_EDIT], [], 'OR'),
    'OR',
  )
}

const delPermission = () => {
  return hasPermission(
    new ComplexPermission([RoleConst.ADMIN], [PermissionConst.ROLE_DELETE], [], 'OR'),
    'OR',
  )
}

onMounted(async () => {
  await getRole()
  currentRole.value = internalRoleList.value[0]
})

async function refresh(role?: RoleItem) {
  await getRole()
  // 创建角色后选中新建的角色
  if (role) {
    currentRole.value = role
  } else {
    currentRole.value = customRoleList.value.find((item) => item.id === currentRole.value?.id)
  }
}

function filter(list: RoleItem[], filterText: string) {
  if (!filterText.length) {
    return list
  }
  return list.filter((v: RoleItem) => v.role_name.toLowerCase().includes(filterText.toLowerCase()))
}

watch(filterText, (val: string) => {
  filterInternalRole.value = filter(internalRoleList.value, val)
  filterCustomRole.value = filter(customRoleList.value, val)
})

function clickRole(item: RoleItem) {
  currentRole.value = item
}

const createOrUpdateRoleDialogRef = ref<InstanceType<typeof CreateOrUpdateRoleDialog>>()

function createOrUpdateRole(item?: RoleItem) {
  createOrUpdateRoleDialogRef.value?.open(item)
}

function deleteRole(item: RoleItem) {
  MsgConfirm(
    `${t('views.role.delete.confirmTitle')}${item.role_name} ?`,
    t('views.role.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      loadPermissionApi('role')
        .deleteRole(item.id, loading)
        .then(async () => {
          MsgSuccess(t('common.deleteSuccess'))
          await getRole()
          currentRole.value =
            item.id === currentRole.value?.id ? internalRoleList.value[0] : currentRole.value
        })
    })
    .catch(() => {})
}

const currentTab = ref('permission')
const tabList = [
  {
    value: 'permission',
    label: t('views.role.permission.title'),
  },
  {
    value: 'member',
    label: t('views.role.member.title'),
  },
]
const mouseId = ref('')

function mouseenter(row: any) {
  mouseId.value = row.id
}
</script>

<style lang="scss" scoped>
.role-manage {
  .role-left {
    box-sizing: border-box;
    width: var(--setting-left-width);
    min-width: var(--setting-left-width);

    .list-height-left {
      height: calc(100vh - 200px);
    }
  }
  .role-right {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
}
</style>
