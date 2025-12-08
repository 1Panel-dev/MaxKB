<template>
  <div class="workspace-manage p-16-24">
    <h2 class="mb-16">{{ $t('views.workspace.title') }}</h2>
    <el-card style="--el-card-padding: 0">
      <div class="flex main-calc-height">
        <div class="workspace-left border-r">
          <div class="p-24 pb-0">
            <div class="flex-between mb-12">
              <h4 class="medium">{{ $t('views.workspace.list') }}</h4>
              <el-tooltip
                effect="dark"
                :content="`${$t('common.create')}${$t('views.workspace.title')}`"
                placement="top"
              >
                <el-button
                  type="primary"
                  text
                  @click="createOrUpdateWorkspace()"
                  v-hasPermission="[RoleConst.ADMIN, PermissionConst.WORKSPACE_CREATE]"
                >
                  <AppIcon iconName="app-add-outlined"></AppIcon>
                </el-button>
              </el-tooltip>
            </div>
            <el-input
              v-model="filterText"
              :placeholder="$t('common.search')"
              prefix-icon="Search"
              clearable
            />
          </div>
          <div class="list-height-left">
            <el-scrollbar v-loading="loading">
              <div class="p-8-16">
                <common-list
                  :data="filterList"
                  @click="clickWorkspace"
                  :default-active="currentWorkspace?.id"
                  @mouseenter="mouseenter"
                  @mouseleave="mouseId = ''"
                >
                  <template #default="{ row }">
                    <div class="flex-between">
                      <span class="ellipsis" :title="row.name">{{ i18n_name(row.name) }}</span>
                      <div @click.stop v-show="mouseId === row.id">
                        <el-dropdown
                          :teleported="false"
                          trigger="click"
                          v-if="editPermission() || dlePermission()"
                        >
                          <el-button text>
                            <AppIcon iconName="app-more"></AppIcon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu style="min-width: 80px">
                              <el-dropdown-item
                                @click.stop="createOrUpdateWorkspace(row)"
                                class="p-8"
                                v-if="editPermission()"
                              >
                                <AppIcon iconName="app-edit" class="color-secondary"></AppIcon>
                                {{ $t('common.rename') }}
                              </el-dropdown-item>
                              <el-dropdown-item
                                @click.stop="deleteWorkspace(row)"
                                class="border-t p-8"
                                v-if="dlePermission()"
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
        <div class="workspace-right p-24" v-loading="loading">
          <div class="flex align-center mb-16">
            <h4 class="medium">{{ i18n_name(currentWorkspace?.name as string) }}</h4>
            <el-divider direction="vertical" class="mr-8 ml-8" />
            <el-icon class="color-input-placeholder"><UserFilled /></el-icon>
            <span class="color-input-placeholder ml-4">
              {{ currentWorkspace?.user_count }}
            </span>
          </div>
          <Member :currentWorkspace="currentWorkspace" />
        </div>
      </div>
    </el-card>

    <CreateOrUpdateWorkspaceDialog ref="createOrUpdateWorkspaceDialogRef" @refresh="refresh" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch } from 'vue'
import { t } from '@/locales'
import { i18n_name } from '@/utils/common'
import Member from './component/Member.vue'
import CreateOrUpdateWorkspaceDialog from './component/CreateOrUpdateWorkspaceDialog.vue'
import type { WorkspaceItem } from '@/api/type/workspace'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import { loadPermissionApi } from '@/utils/dynamics-api/permission-api.ts'

const filterText = ref('')
const loading = ref(false)
const list = ref<WorkspaceItem[]>([])
const filterList = ref<WorkspaceItem[]>([]) // 搜索过滤后列表
const currentWorkspace = ref<WorkspaceItem>()

async function getWorkspace() {
  try {
    const res = await loadPermissionApi('workspace').getSystemWorkspaceList(loading)
    list.value = res.data
    filterList.value = filter(list.value, filterText.value)
  } catch (error) {
    console.error(error)
  }
}

onMounted(async () => {
  await getWorkspace()
  currentWorkspace.value = list.value[0]
})

const editPermission = () => {
  return hasPermission([RoleConst.ADMIN, PermissionConst.WORKSPACE_EDIT], 'OR')
}

const dlePermission = () => {
  return hasPermission([RoleConst.ADMIN, PermissionConst.WORKSPACE_DELETE], 'OR')
}

async function refresh(workspace?: WorkspaceItem) {
  await getWorkspace()
  // 创建后选中新建的
  if (workspace) {
    currentWorkspace.value = workspace
  } else {
    currentWorkspace.value = list.value.find((item) => item.id === currentWorkspace.value?.id)
  }
}

function filter(list: WorkspaceItem[], filterText: string) {
  if (!filterText.length) {
    return list
  }
  return list.filter((v: WorkspaceItem) => v.name.toLowerCase().includes(filterText.toLowerCase()))
}

watch(filterText, (val: string) => {
  filterList.value = filter(list.value, val)
})

function clickWorkspace(item: WorkspaceItem) {
  currentWorkspace.value = item
}

const createOrUpdateWorkspaceDialogRef = ref<InstanceType<typeof CreateOrUpdateWorkspaceDialog>>()

function createOrUpdateWorkspace(item?: WorkspaceItem) {
  createOrUpdateWorkspaceDialogRef.value?.open(item)
}

async function check(id: string) {
  try {
    return await loadPermissionApi('workspace').deleteWorkspaceCheck(id)
  } catch (error) {
    console.log(error)
  }
}

async function deleteWorkspace(item: WorkspaceItem) {
  // 判断是否能删除
  const res = await check(item.id as string)
  const canDelete = res ? res.data.can_delete : true
  if (canDelete) {
    MsgConfirm(
      `${t('views.workspace.delete.confirmTitle')}${item.name} ?`,
      t('views.workspace.delete.confirmContent'),
      {
        confirmButtonText: t('common.confirm'),
        confirmButtonClass: 'danger',
      },
    ).then(() => {
      loadPermissionApi('workspace')
        .deleteWorkspace(item.id as string, loading)
        .then(async () => {
          MsgSuccess(t('common.deleteSuccess'))
          await getWorkspace()
          currentWorkspace.value =
            item.id === currentWorkspace.value?.id ? list.value[0] : currentWorkspace.value
        })
    })
  } else {
    MsgConfirm(
      `${t('views.workspace.delete.confirmTitle')}${item.name} ?`,
      res ? res.data.message : t('views.workspace.delete.confirmContent'),
      {
        showConfirmButton: false,
        cancelButtonText: t('common.close'),
      },
    )
  }
}
const mouseId = ref('')

function mouseenter(row: any) {
  mouseId.value = row.id
}
</script>

<style lang="scss" scoped>
.workspace-manage {
  .workspace-left {
    box-sizing: border-box;
    width: var(--setting-left-width);
    min-width: var(--setting-left-width);

    .list-height-left {
      height: calc(100vh - 255px);
    }
  }

  .workspace-right {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
}
</style>
