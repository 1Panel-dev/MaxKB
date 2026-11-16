<script setup lang="ts">
import { computed, ref } from 'vue'
import { RESOURCE_TYPE } from '@/api/enums'
import type { SharedResourceType, SharedWorkspaceAuthorization, WorkspaceItem } from '@/api/types'
import AuthorizationApi from '@/api/admin/system/shared-resources/authorization'
import WorkspaceApi from '@/api/admin/system/workspace'
import { MsgSuccess } from '@/utils/message'

const WHITE_LIST = 'WHITE_LIST'
const BLACK_LIST = 'BLACK_LIST'

/* 查询当前资源的工作空间授权。 */
const visible = ref(false)
const loading = ref(false)
const resourceId = ref('')
const resourceType = ref<SharedResourceType>(RESOURCE_TYPE.KNOWLEDGE)
const authenticationType = ref<SharedWorkspaceAuthorization['authentication_type']>(WHITE_LIST)
const search = ref('')
const workspaces = ref<(WorkspaceItem & { id: string })[]>([])
const checkedWorkspaceIds = ref<string[]>([])
const filteredWorkspaces = computed(() => workspaces.value.filter(({ name }) => name.includes(search.value)))
const selectedWorkspaces = computed(() => workspaces.value.filter(({ id }) => checkedWorkspaceIds.value.includes(id)))
const checkAll = computed({
  get: () => workspaces.value.length > 0 && checkedWorkspaceIds.value.length === workspaces.value.length,
  set: (checked: boolean) => {
    checkedWorkspaceIds.value = checked ? workspaces.value.map(({ id }) => id) : []
  },
})
const isIndeterminate = computed(() => checkedWorkspaceIds.value.length > 0 && checkedWorkspaceIds.value.length < workspaces.value.length)

function open(resource: { id: string }, type: SharedResourceType) {
  if (loading.value) return
  resourceId.value = resource.id
  resourceType.value = type
  loading.value = true
  return Promise.all([AuthorizationApi.getSharedAuthorization(resourceType.value, resourceId.value), WorkspaceApi.getSystemWorkspaceList()])
    .then(([authorization, workspaceOptions]) => {
      workspaces.value = workspaceOptions.filter((workspace): workspace is WorkspaceItem & { id: string } => !!workspace.id)
      authenticationType.value = authorization?.authentication_type ?? WHITE_LIST
      checkedWorkspaceIds.value = (authorization?.workspace_id_list ?? []).filter((id) => workspaces.value.some((workspace) => workspace.id === id))
      visible.value = true
    })
    .finally(() => {
      loading.value = false
    })
}

/* 保存成功才关闭，失败保留授权草稿。 */
function handleConfirm() {
  if (loading.value) return
  loading.value = true
  return AuthorizationApi.postSharedAuthorization(resourceType.value, resourceId.value, {
    authentication_type: authenticationType.value,
    workspace_id_list: [...checkedWorkspaceIds.value],
  })
    .then(() => {
      MsgSuccess('操作成功')
      visible.value = false
    })
    .finally(() => {
      loading.value = false
    })
}

function handleRemoveWorkspace(workspaceId: string) {
  checkedWorkspaceIds.value = checkedWorkspaceIds.value.filter((id) => id !== workspaceId)
}

/* 关闭动画结束后清空本次授权数据。 */
function handleClosed() {
  resourceId.value = ''
  resourceType.value = RESOURCE_TYPE.KNOWLEDGE
  authenticationType.value = WHITE_LIST
  search.value = ''
  workspaces.value = []
  checkedWorkspaceIds.value = []
  loading.value = false
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="授权工作空间" width="840" content-class="h-120" @closed="handleClosed">
    <template #subtitle>被授权的工作空间，可使用当前资源</template>
    <div v-loading="loading" class="flex-column h-full">
      <p class="shrink-0">类型</p>
      <el-radio-group v-model="authenticationType" class="shrink-0">
        <el-radio :value="WHITE_LIST">白名单</el-radio>
        <el-radio :value="BLACK_LIST">黑名单</el-radio>
      </el-radio-group>
      <p class="mt-2 mb-2 shrink-0">选择工作空间</p>
      <div class="grid min-h-0 flex-1 grid-cols-2 overflow-hidden rounded-md border">
        <!-- 左边 -->
        <section class="flex-column min-h-0 border-r">
          <div class="shrink-0 p-4 pb-0">
            <MkSearchInput v-model="search" />
          </div>

          <div class="flex-column min-h-0 flex-1">
            <!-- 全选工作空间 -->
            <div class="p-2 pb-0">
              <el-checkbox v-if="!search" v-model="checkAll" :indeterminate="isIndeterminate" class="w-full shrink-0 rounded-md p-2 hover:bg-N900/10">
                全选
              </el-checkbox>
            </div>
            <el-scrollbar class="min-h-0 flex-1 p-2 pt-0">
              <el-checkbox-group v-model="checkedWorkspaceIds" class="mk-checkbox-group-vertical">
                <el-checkbox
                  v-for="workspace in filteredWorkspaces"
                  :key="workspace.id"
                  :value="workspace.id"
                  class="rounded-md px-2 py-2 hover:bg-N900/10"
                >
                  <div class="flex-align-center min-w-0 gap-2">
                    <MkIcon name="icon_moments-categories_outlined" class="shrink-0" />
                    <span class="block min-w-0 truncate" :title="workspace.name">{{ workspace.name }}</span>
                  </div>
                </el-checkbox>
              </el-checkbox-group>
              <MkEmpty v-if="!filteredWorkspaces.length" :type="search ? 'search' : 'default'" />
            </el-scrollbar>
          </div>
        </section>
        <!-- 右边 -->
        <section class="flex-column min-h-0">
          <div class="flex-between shrink-0 p-4 pb-3 mt-1">
            <span>已选：{{ checkedWorkspaceIds.length }} 个</span>
            <!-- 清空已选工作空间 -->
            <el-button link type="primary" @click="checkedWorkspaceIds = []">清空</el-button>
          </div>
          <el-scrollbar class="min-h-0 flex-1" wrap-class="p-2 pt-0">
            <template v-for="workspace in selectedWorkspaces" :key="workspace.id">
              <div class="flex-between gap-2 rounded-md p-2 hover:bg-N900/10">
                <span class="truncate" :title="workspace.name">{{ workspace.name }}</span>
                <!-- 移除已选工作空间 -->
                <el-button text class="-mr-1" @click="handleRemoveWorkspace(workspace.id)"><MkIcon name="icon_close_outlined" /></el-button>
              </div>
            </template>
          </el-scrollbar>
        </section>
      </div>
    </div>
    <template #footer>
      <!-- 取消工作空间授权 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 保存工作空间授权 -->
      <el-button type="primary" :loading="loading" @click="handleConfirm">保存</el-button>
    </template>
  </MkDialog>
</template>
