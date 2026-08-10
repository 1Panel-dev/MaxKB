<script setup lang="ts">
import type { FormItemRule } from 'element-plus'
import type { ListItem, SystemUserRoleAssignment } from '@/api/types'

defineOptions({ name: 'UserRoleSettingSection' })

withDefaults(
  defineProps<{
    loading?: boolean
    roleOptions: ListItem[]
    showWorkspace?: boolean
    workspaceOptions: ListItem[]
  }>(),
  { showWorkspace: true },
)

const roleAssignments = defineModel<SystemUserRoleAssignment[]>({ required: true })

const roleRequiredRule: FormItemRule = {
  required: true,
  message: '请选择角色',
  trigger: 'change',
}
const workspaceRequiredRule: FormItemRule = {
  required: true,
  type: 'array',
  min: 1,
  message: '请选择工作空间',
  trigger: 'change',
}

function addRole() {
  roleAssignments.value = [...roleAssignments.value, { role_id: '', workspace_ids: [] }]
}

function removeRole(index: number) {
  if (roleAssignments.value.length === 1) return
  roleAssignments.value = roleAssignments.value.filter((_, roleIndex) => roleIndex !== index)
}
</script>

<template>
  <div v-for="(roleAssignment, index) in roleAssignments" :key="index" class="flex w-full gap-2">
    <el-form-item
      class="flex-1"
      :label="index === 0 ? '角色' : ''"
      :prop="`role_setting.${index}.role_id`"
      :rules="roleRequiredRule"
    >
      <el-select
        v-model="roleAssignment.role_id"
        placeholder="请选择角色"
        :loading="loading"
        clearable
        filterable
        fit-input-width
      >
        <el-option
          v-for="roleOption in roleOptions"
          :key="roleOption.id"
          :label="roleOption.name"
          :title="roleOption.name"
          :value="roleOption.id"
        />
      </el-select>
    </el-form-item>

    <el-form-item
      v-if="showWorkspace"
      class="flex-1"
      :label="index === 0 ? '工作空间' : ''"
      :prop="`role_setting.${index}.workspace_ids`"
      :rules="workspaceRequiredRule"
    >
      <el-select
        v-model="roleAssignment.workspace_ids"
        placeholder="请选择工作空间"
        :loading="loading"
        clearable
        filterable
        fit-input-width
        multiple
        collapse-tags
        collapse-tags-tooltip
        :reserve-keyword="false"
      >
        <el-option
          v-for="workspaceOption in workspaceOptions"
          :key="workspaceOption.id"
          :label="workspaceOption.name"
          :title="workspaceOption.name"
          :value="workspaceOption.id"
        />
      </el-select>
    </el-form-item>

    <el-form-item class="shrink-0" :class="index === 0 ? 'mt-8' : 'mt-0.5'">
      <el-button :disabled="roleAssignments.length === 1" text @click="removeRole(index)">
        <mk-icon name="icon_delete-trash_outlined" class="text-N600"></mk-icon>
      </el-button>
    </el-form-item>
  </div>

  <el-button link type="primary" @click="addRole" class="-mt-3">
    <mk-icon name="icon_add_outlined"></mk-icon>
    <span>添加角色</span>
  </el-button>
</template>
