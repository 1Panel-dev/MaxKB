<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ListItem } from '@/api/types'
import type { CascaderNode, CascaderOption, CascaderProps } from 'element-plus'
import UserGroupsApi from '@/api/admin/system/user-groups'
import { useStore } from '@/stores/admin'

defineOptions({ name: 'UserGroupSetting' })

const { t } = useI18n({ useScope: 'global' })
const { auth } = useStore()

const props = defineProps<{ workspaceIds: string[]; workspaceOptions: ListItem[] }>()

const userGroupIds = defineModel<string[] | undefined>({ required: true })

const userGroupOptions = ref<CascaderOption[]>([])

const cascaderProps: CascaderProps = {
  showPrefix: false,
  multiple: true,
  children: 'children',
  emitPath: false,
  label: 'name',
  lazy: true,
  lazyLoad: loadWorkspaceUserGroups,
  leaf: 'leaf',
  value: 'id',
}

function getWorkspaceUserGroups(workspaceId: string) {
  return UserGroupsApi.getSystemUserGroups(workspaceId).then((userGroups) => userGroups.map((userGroup) => ({ ...userGroup, leaf: true })))
}

// 展开级联第一列时，按工作空间异步加载第二列用户组。
function loadWorkspaceUserGroups(node: CascaderNode, resolve: (options: CascaderOption[]) => void, reject: () => void) {
  if (node.level !== 1) {
    resolve([])
    return
  }

  getWorkspaceUserGroups(String(node.value)).then(resolve).catch(reject)
}

// 社区版直接加载默认空间用户组；商业版编辑态预加载以完成名称回显。
function refreshUserGroupOptions() {
  if (!props.workspaceIds.length) {
    userGroupIds.value = []
    userGroupOptions.value = []
    return
  }

  const preloadRequest = auth.isCE || userGroupIds.value?.length ? Promise.all(props.workspaceIds.map(getWorkspaceUserGroups)) : Promise.resolve([])

  preloadRequest.then((workspaceUserGroups) => {
    userGroupOptions.value = auth.isCE
      ? workspaceUserGroups.flat()
      : props.workspaceOptions
          .filter(({ id }) => props.workspaceIds.includes(id))
          .map((workspace) => ({ ...workspace, children: workspaceUserGroups[props.workspaceIds.indexOf(workspace.id)], leaf: false }))

    const availableUserGroupIds = workspaceUserGroups.flat().map(({ id }) => String(id))
    userGroupIds.value = (userGroupIds.value ?? []).filter((id) => availableUserGroupIds.includes(id))
  })
}

watch([() => props.workspaceIds, () => props.workspaceOptions, () => auth.isCE], refreshUserGroupOptions, { deep: true, immediate: true })
</script>

<template>
  <el-form-item>
    <!-- 社区版直接多选用户组 -->
    <el-select v-if="auth.isCE" v-model="userGroupIds" class="w-full" multiple clearable filterable :placeholder="t('userGroup.placeholder')">
      <el-option v-for="userGroup in userGroupOptions" :key="userGroup.id" :label="userGroup.name" :value="userGroup.id" />
    </el-select>
    <!-- 非社区版按工作空间选择用户组 -->
    <el-cascader
      v-else
      v-model="userGroupIds"
      class="w-full"
      :options="userGroupOptions"
      :props="cascaderProps"
      :show-all-levels="false"
      clearable
      filterable
      :placeholder="t('userGroup.placeholder')"
      fit-input-width
    />
  </el-form-item>
</template>
