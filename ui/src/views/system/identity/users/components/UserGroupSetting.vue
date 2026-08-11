<script setup lang="ts">
import { ref, watch } from 'vue'
import UserGroupsApi from '@/api/admin/system/user-groups'
import type { ListItem } from '@/api/types'
import type { CascaderNode, CascaderOption, CascaderProps } from 'element-plus'

defineOptions({ name: 'UserGroupSetting' })

const props = defineProps<{
  workspaceIds: string[]
  workspaceOptions: ListItem[]
}>()

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
  return UserGroupsApi.getSystemUserGroups(workspaceId).then((userGroups) =>
    userGroups.map((userGroup) => ({ ...userGroup, leaf: true })),
  )
}

// 展开级联第一列时，按工作空间异步加载第二列用户组。
function loadWorkspaceUserGroups(
  node: CascaderNode,
  resolve: (options: CascaderOption[]) => void,
  reject: () => void,
) {
  if (node.level !== 1) {
    resolve([])
    return
  }

  getWorkspaceUserGroups(String(node.value)).then(resolve).catch(reject)
}

// 工作空间变化时重建级联选项；编辑态先预加载用户组以完成名称回显。
function refreshUserGroupOptions() {
  if (!props.workspaceIds.length) {
    userGroupIds.value = []
    userGroupOptions.value = []
    return
  }

  const preloadRequest = userGroupIds.value?.length
    ? Promise.all(props.workspaceIds.map(getWorkspaceUserGroups))
    : Promise.resolve([])

  preloadRequest.then((workspaceUserGroups) => {
    userGroupOptions.value = props.workspaceOptions
      .filter(({ id }) => props.workspaceIds.includes(id))
      .map((workspace) => ({
        ...workspace,
        children: workspaceUserGroups[props.workspaceIds.indexOf(workspace.id)],
        leaf: false,
      }))

    const availableUserGroupIds = workspaceUserGroups.flat().map(({ id }) => String(id))
    userGroupIds.value = (userGroupIds.value ?? []).filter((id) =>
      availableUserGroupIds.includes(id),
    )
  })
}

watch([() => props.workspaceIds, () => props.workspaceOptions], refreshUserGroupOptions, {
  deep: true,
  immediate: true,
})
</script>

<template>
  <el-form-item>
    <el-cascader
      v-model="userGroupIds"
      class="w-full"
      :options="userGroupOptions"
      :props="cascaderProps"
      :show-all-levels="false"
      clearable
      placeholder="请选择用户组"
    />
  </el-form-item>
</template>
