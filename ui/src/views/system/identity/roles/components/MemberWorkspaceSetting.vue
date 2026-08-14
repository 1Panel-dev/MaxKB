<script setup lang="ts">
import type { FormItemRule } from 'element-plus'
import type { CreateRoleMemberItem, SystemUserOption, WorkspaceItem } from '@/api/types'

defineOptions({ name: 'MemberWorkspaceSetting' })

defineProps<{
  remoteUserMethod: (keyword: string) => Promise<void>
  showWorkspace?: boolean
  userLoading?: boolean
  userOptions: SystemUserOption[]
  workspaceLoading?: boolean
  workspaceOptions: WorkspaceItem[]
}>()

const memberSettings = defineModel<CreateRoleMemberItem[]>({ required: true })

const memberRequiredRule: FormItemRule = {
  required: true,
  type: 'array',
  min: 1,
  message: '请选择成员',
  trigger: 'change',
}
const workspaceRequiredRule: FormItemRule = {
  required: true,
  type: 'array',
  min: 1,
  message: '请选择工作空间',
  trigger: 'change',
}

function addMemberSetting() {
  memberSettings.value = [...memberSettings.value, { user_ids: [], workspace_ids: [] }]
}

function removeMemberSetting(index: number) {
  if (memberSettings.value.length === 1) return
  memberSettings.value = memberSettings.value.filter((_, settingIndex) => settingIndex !== index)
}
</script>

<template>
  <div v-for="(memberSetting, index) in memberSettings" :key="index" class="flex w-full gap-2">
    <el-form-item
      class="flex-1"
      :label="index === 0 ? '成员' : ''"
      :prop="`members.${index}.user_ids`"
      :rules="memberRequiredRule"
    >
      <el-select
        v-model="memberSetting.user_ids"
        :loading="userLoading"
        :remote-method="remoteUserMethod"
        collapse-tags
        collapse-tags-tooltip
        filterable
        fit-input-width
        multiple
        placeholder="请选择成员"
        remote
        :reserve-keyword="false"
      >
        <el-option
          v-for="userOption in userOptions"
          :key="userOption.id"
          :label="userOption.nick_name || userOption.username"
          :title="userOption.nick_name || userOption.username"
          :value="userOption.id"
        />
      </el-select>
    </el-form-item>

    <el-form-item
      v-if="showWorkspace"
      class="flex-1"
      :label="index === 0 ? '工作空间' : ''"
      :prop="`members.${index}.workspace_ids`"
      :rules="workspaceRequiredRule"
    >
      <el-select
        v-model="memberSetting.workspace_ids"
        :loading="workspaceLoading"
        collapse-tags
        collapse-tags-tooltip
        filterable
        fit-input-width
        multiple
        placeholder="请选择工作空间"
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
      <el-button :disabled="memberSettings.length === 1" text @click="removeMemberSetting(index)">
        <MkIcon name="icon_delete-trash_outlined" class="text-N600" />
      </el-button>
    </el-form-item>
  </div>

  <el-button class="-mt-1 mb-6" link type="primary" @click="addMemberSetting">
    <MkIcon name="icon_add_outlined" />
    <span>添加成员</span>
  </el-button>
</template>
