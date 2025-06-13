<template>
  <div class="role">
    <h2 class="mb-16">{{ $t('views.role.title') }}</h2>
    <el-card style="--el-card-padding: 0" body-class="role-card">
      <div class="flex h-full">
        <div class="role-left border-r p-16">
          <div class="p-8 pb-0">
            <el-input v-model="filterText" :placeholder="$t('common.search')" prefix-icon="Search" clearable />
          </div>
          <div class="list-height-left mt-8">
            <el-scrollbar v-loading="loading">
              <div class="role-left_title color-secondary lighter">
                <span>{{ $t('views.role.internalRole') }}</span>
              </div>
              <common-list :data="filterInternalRole" @click="clickRole" :default-active="currentRole?.id">
                <template #default="{ row }">
                  <div class="flex-between">
                    <span class="mr-8">{{ row.role_name }}</span>
                    <el-dropdown :teleported="false">
                      <el-button text>
                        <el-icon class="color-secondary">
                          <MoreFilled />
                        </el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu style="min-width: 80px">
                          <el-dropdown-item @click.stop="createOrUpdateRole(row)" class="p-8">
                            <AppIcon iconName="app-copy"></AppIcon>
                            {{ $t('common.rename') }}
                          </el-dropdown-item>
                          <el-dropdown-item @click.stop="deleteRole(row)" class="border-t p-8">
                            <AppIcon iconName="app-copy"></AppIcon>
                            {{ $t('common.delete') }}
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
              <div class="role-left_divider">
                <el-divider />
              </div>
              <div class="role-left_title">
                <span class="color-secondary lighter">{{ $t('views.role.customRole') }}</span>
                <el-tooltip effect="dark" :content="`${$t('common.create')}${$t('views.role.customRole')}`"
                  placement="top">
                  <el-button type="primary" text @click="createOrUpdateRole()">
                    <AppIcon iconName="app-copy"></AppIcon>
                  </el-button>
                </el-tooltip>
              </div>
              <common-list :data="filterCustomRole" @click="clickRole" :default-active="currentRole?.id">
                <template #default="{ row }">
                  <div class="flex-between">
                    <span>
                      {{ row.role_name }}
                      <span class="color-input-placeholder ml-4">({{ roleTypeMap[row.type as RoleTypeEnum] }})</span>
                    </span>
                    <el-dropdown :teleported="false">
                      <el-button text>
                        <el-icon class="color-secondary">
                          <MoreFilled />
                        </el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu style="min-width: 80px">
                          <el-dropdown-item @click.stop="createOrUpdateRole(row)" class="p-8">
                            <AppIcon iconName="app-copy"></AppIcon>
                            {{ $t('common.rename') }}
                          </el-dropdown-item>
                          <el-dropdown-item @click.stop="deleteRole(row)" class="border-t p-8">
                            <AppIcon iconName="app-copy"></AppIcon>
                            {{ $t('common.delete') }}
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
        <div class="role-right" v-loading="loading">
          <div class="flex-between mb-16 p-24 pb-0">
            <div class="flex align-center">
              <span>
                {{ currentRole?.role_name }}
                <span v-if="currentRole?.type && !currentRole.internal" class="color-input-placeholder ml-4">({{
                  roleTypeMap[currentRole?.type as
                  RoleTypeEnum] }})
                </span>
              </span>
              <el-divider direction="vertical" class="mr-8 ml-8" />
              <AppIcon iconName="app-wordspace" style="font-size: 16px" class="color-input-placeholder"></AppIcon>
              <span class="color-input-placeholder ml-4">
                数字
              </span>
            </div>
            <el-radio-group v-model="currentTab">
              <el-radio-button v-for="item in tabList" :key="item.value" :label="item.label" :value="item.value" />
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
import RoleApi from '@/api/system/role'
import { t } from '@/locales'
import PermissionConfiguration from './component/PermissionConfiguration.vue'
import Member from './component/Member.vue'
import CreateOrUpdateRoleDialog from './component/CreateOrUpdateRoleDialog.vue'
import type { RoleItem } from '@/api/type/role'
import { RoleTypeEnum } from '@/enums/system'
import { roleTypeMap } from './index'
import { MsgSuccess, MsgConfirm } from '@/utils/message'

const filterText = ref('')
const loading = ref(false)
const internalRoleList = ref<RoleItem[]>([])
const filterInternalRole = ref<RoleItem[]>([]) // 搜索过滤后列表
const customRoleList = ref<RoleItem[]>([])
const filterCustomRole = ref<RoleItem[]>([]) // 搜索过滤后列表
const currentRole = ref<RoleItem>()

async function getRole() {
  try {
    const res = await RoleApi.getRoleList(loading)
    internalRoleList.value = res.data.internal_role
    customRoleList.value = res.data.custom_role
    filterInternalRole.value = filter(internalRoleList.value, filterText.value)
    filterCustomRole.value = filter(customRoleList.value, filterText.value)
  } catch (error) {
    console.error(error)
  }
}

onMounted(async () => {
  await getRole()
  currentRole.value = internalRoleList.value[0]
})

async function refresh(role?: RoleItem) {
  await getRole();
  // 创建角色后选中新建的角色
  currentRole.value = role ? role : currentRole.value
}

function filter(list: RoleItem[], filterText: string) {
  if (!filterText.length) {
    return list
  }
  return list.filter((v: RoleItem) =>
    v.role_name.toLowerCase().includes(filterText.toLowerCase()),
  )
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
  createOrUpdateRoleDialogRef.value?.open(item);
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
      RoleApi.deleteRole(item.id, loading).then(async () => {
        MsgSuccess(t('common.deleteSuccess'))
        await getRole()
        currentRole.value = item.id === currentRole.value?.id ? internalRoleList.value[0] : currentRole.value
      })
    })
    .catch(() => { })
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

</script>

<style lang="scss" scoped>
.role {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  box-sizing: border-box;
  padding: 16px 24px;

  :deep(.role-card) {
    height: 100%;
    overflow: hidden;
  }

  .role-left {
    box-sizing: border-box;
    width: var(--setting-left-width);
    min-width: var(--setting-left-width);

    .role-left_title {
      padding: 8px;
      display: flex;
      justify-content: space-between;
    }

    .list-height-left {
      height: calc(100vh - 213px);

      :deep(.common-list li) {
        padding-right: 4px;
        padding-left: 8px;
      }
    }

    .role-left_divider {
      padding: 0 8px;

      :deep(.el-divider) {
        margin: 4px 0;
      }
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
