<template>
  <el-dialog modal-class="authorized-workspace" v-model="centerDialogVisible" width="840">
    <template #header="{ titleId, titleClass }">
      <h4 class="mb-8">{{ $t('views.shared.authorized_workspace') }}</h4>
      <el-text class="color-secondary lighter">被授权的工作空间，可使用当前资源</el-text>
    </template>

    <p class="mb-8 lighter">类型</p>
    <el-radio-group v-model="listType">
      <el-radio value="WHITE_LIST">白名单</el-radio>
      <el-radio value="BLACK_LIST">黑名单</el-radio>
    </el-radio-group>
    <p class="mb-8 lighter mt-16">选择工作空间</p>
    <div class="flex border" v-loading="loading">
      <div class="p-16 border-r">
        <el-input
          v-model="search"
          :validate-event="false"
          :placeholder="$t('common.search')"
          style="width: 364px"
          clearable
        >
          <template #prefix>
            <el-icon>
              <Search></Search>
            </el-icon>
          </template>
        </el-input>
        <div class="mt-8">
          <el-checkbox
            class="mb-8"
            v-model="checkAll"
            :indeterminate="isIndeterminate"
            @change="handleCheckAllChange"
            v-if="!search"
          >
            全选
          </el-checkbox>
          <el-checkbox-group
            class="checkbox-group-block"
            v-model="checkedWorkspace"
            @change="handleCheckedWorkspaceChange"
          >
            <el-checkbox
              v-for="space in workspaceWithKeywords"
              :key="space.id"
              :label="space.name"
              :value="space"
            >
              <div class="flex">
                <AppIcon iconName="app-workspace"></AppIcon>
                <span class="ml-4 ellipsis" :title="space.name"> {{ space.name }}</span>
              </div>
            </el-checkbox>
          </el-checkbox-group>
        </div>
      </div>
      <div class="p-16 w-full">
        <div class="flex-between mb-16">
          <span class="lighter">
            {{ $t('common.selected') }}: {{ checkedWorkspace.length }} 个
          </span>

          <el-button @click="clearWorkspaceAll" link type="primary">
            {{ $t('common.clear') }}
          </el-button>
        </div>
        <template v-for="ele in checkedWorkspace">
          <div class="flex-between">
            <div class="flex align-center">
              <AppIcon iconName="app-workspace"></AppIcon>
              <span class="ml-4 lighter ellipsis" :title="ele.name">{{ ele.name }}</span>
            </div>
            <el-button link>
              <el-icon @click="clearWorkspace(ele)" :size="18">
                <Close />
              </el-icon>
            </el-button>
          </div>
        </template>
      </div>
    </div>

    <template #footer>
      <el-button @click="centerDialogVisible = false"> {{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="handleConfirm"> {{ $t('common.save') }}</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'
import type { CheckboxValueType } from 'element-plus'
import authorizationApi from '@/api/system-shared/authorization'
import workspaceApi from '@/api/workspace/workspace'
import { loadPermissionApi } from '@/utils/dynamics-api/permission-api.ts'

const checkAll = ref(false)
const isIndeterminate = ref(true)
const checkedWorkspace = ref<any[]>([])
const workspace = ref<any[]>([])
const listType = ref('WHITE_LIST')
const search = ref('')
let knowledge_id = ''
let currentType = 'Knowledge'
const loading = ref(false)
const centerDialogVisible = ref(false)

const workspaceWithKeywords = computed(() => {
  return workspace.value.filter((ele: any) => (ele.name as string).includes(search.value))
})
const handleCheckAllChange = (val: CheckboxValueType) => {
  checkedWorkspace.value = val ? workspace.value : []
  isIndeterminate.value = false
  if (!val) {
    clearWorkspaceAll()
  }
}
const handleCheckedWorkspaceChange = (value: CheckboxValueType[]) => {
  const checkedCount = value.length
  checkAll.value = checkedCount === workspace.value.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < workspace.value.length
}

const open = async ({ id }: any, type = 'Knowledge') => {
  knowledge_id = id
  loading.value = true
  currentType = type
  const [authList, systemWorkspaceList] = await Promise.all([
    authorizationApi[`getSharedAuthorization${type}`](id),
    loadPermissionApi('workspace').getSystemWorkspaceList(),
  ])
  workspace.value = systemWorkspaceList.data as any
  listType.value = (authList.data || {}).authentication_type || 'WHITE_LIST'
  let workspace_id_list = (authList.data || {}).workspace_id_list || []
  checkedWorkspace.value = workspace.value.filter((ele) => workspace_id_list.includes(ele.id))
  handleCheckedWorkspaceChange(checkedWorkspace.value)
  loading.value = false
  centerDialogVisible.value = true
}

const handleConfirm = () => {
  authorizationApi[`postSharedAuthorization${currentType}`](knowledge_id, {
    workspace_id_list: checkedWorkspace.value.map((ele: any) => ele.id),
    authentication_type: listType.value,
  }).then(() => {
    centerDialogVisible.value = false
  })
}

const clearWorkspace = (val: any) => {
  checkedWorkspace.value = checkedWorkspace.value.filter((ele: any) => ele.id !== val.id)
}

const clearWorkspaceAll = () => {
  checkedWorkspace.value = []
  handleCheckedWorkspaceChange([])
}

defineExpose({
  open,
})
</script>
<style lang="scss"></style>
