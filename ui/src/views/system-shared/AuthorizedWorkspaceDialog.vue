<template>
  <el-dialog modal-class="authorized-workspace" v-model="centerDialogVisible" width="840">
    <template #header="{ titleId, titleClass }">
      <h4 class="mb-8">{{ $t('views.shared.authorized_workspace') }}</h4>
      <el-text class="color-secondary lighter">被授权的工作空间，可使用当前资源</el-text>
    </template>

    <p class="mb-8 lighter">类型</p>
    <el-radio-group v-model="listType" @change="handleListTypeChange">
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
                <AppIcon iconName="app-wordspace"></AppIcon>
                <span class="ml-4"> {{ space.name }}</span>
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
              <AppIcon iconName="app-wordspace"></AppIcon>
              <span class="ml-4 lighter">{{ ele.name }}</span>
            </div>
            <el-button @click="clearWorkspaceAll" link>
              <el-icon @click="clearWorkspace(ele)" :size="18"><Close /></el-icon>
            </el-button>
          </div>
        </template>
      </div>
    </div>

    <template #footer>
      <el-button @click="centerDialogVisible = false"> {{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="handleConfirm"> {{ $t('common.add') }} </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'
import type { CheckboxValueType } from 'element-plus'
import authorizationApi from '@/api/system-shared/authorization'

const checkAll = ref(false)
const isIndeterminate = ref(true)
const checkedWorkspace = ref([])
const workspace = ref([])
const listType = ref('WHITE_LIST')
const search = ref('')
let knowledge_id = ''
let currentType = 'Knowledge'
const loading = ref(false)
const centerDialogVisible = ref(false)
let auth_list: any[] = []
let un_auth_list = []

const workspaceWithKeywords = computed(() => {
  return workspace.value.filter((ele: any) => (ele.name as string).includes(search.value))
})
const handleCheckAllChange = (val: CheckboxValueType) => {
  checkedWorkspace.value = val ? workspace.value : []
  isIndeterminate.value = false
  if (val) {
    clearWorkspaceAll()
  } else {
    auth_list = [
      ...workspace.value.map((ele) => ({ authentication_type: listType.value, workspace_id: ele })),
      ...auth_list.filter((ele) => ele.authentication_type !== listType.value),
    ]
  }
}
const handleCheckedWorkspaceChange = (value: CheckboxValueType[]) => {
  const checkedCount = value.length
  checkAll.value = checkedCount === workspace.value.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < workspace.value.length
  auth_list = [
    ...value.map((ele: any) => ({
      authentication_type: listType.value,
      workspace_id: ele.id,
      name: ele.name,
    })),
    ...auth_list.filter((ele) => ele.authentication_type !== listType.value),
  ]
}

const open = ({ id }: any, type = 'Knowledge') => {
  knowledge_id = id
  auth_list = []
  un_auth_list = []
  listType.value = 'WHITE_LIST'
  loading.value = true
  currentType = type
  authorizationApi[`getSharedAuthorization${type}`](id)
    .then((res: any) => {
      auth_list = (res.data || {}).auth_list || []
      un_auth_list = (res.data || {}).un_auth_list || []
      workspace.value = [
        ...un_auth_list,
        ...auth_list.map((ele) => ({ id: ele.workspace_id, name: ele.name })),
      ] as any
      handleListTypeChange(listType.value)
    })
    .finally(() => {
      loading.value = false
    })
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
  auth_list = auth_list.filter((ele) => ele.workspace_id !== val.id)
}

const clearWorkspaceAll = () => {
  checkedWorkspace.value = []
  auth_list = auth_list.filter((ele) => ele.authentication_type !== listType.value)
  handleCheckedWorkspaceChange([])
}

const handleListTypeChange = (val: any) => {
  checkedWorkspace.value = auth_list
    .filter((ele) => ele.authentication_type === val)
    .map((ele) => ({ id: ele.workspace_id, name: ele.name })) as any
  handleCheckedWorkspaceChange(checkedWorkspace.value)
}
defineExpose({
  open,
})
</script>
<style lang="scss">
.authorized-workspace {
}
</style>
