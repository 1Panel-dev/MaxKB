<script setup lang="ts">
import type { FormItemRule } from 'element-plus'
import type { CreateWorkspaceMemberParamsItem, SelectOption, SystemUserOption } from '@/api/types'

defineOptions({ name: 'MemberRoleSetting' })

defineProps<{
  remoteUserMethod: (keyword: string) => Promise<void>
  roleLoading?: boolean
  roleOptions: SelectOption[]
  userLoading?: boolean
  userOptions: SystemUserOption[]
}>()

const memberSettings = defineModel<CreateWorkspaceMemberParamsItem[]>({ required: true })

const memberRequiredRule: FormItemRule = {
  required: true,
  type: 'array',
  min: 1,
  message: '请选择成员',
  trigger: 'change',
}
const roleRequiredRule: FormItemRule = {
  required: true,
  type: 'array',
  min: 1,
  message: '请选择角色',
  trigger: 'change',
}

function addMemberSetting() {
  memberSettings.value = [...memberSettings.value, { role_ids: [], user_ids: [] }]
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
      class="flex-1"
      :label="index === 0 ? '角色' : ''"
      :prop="`members.${index}.role_ids`"
      :rules="roleRequiredRule"
    >
      <el-select
        v-model="memberSetting.role_ids"
        :loading="roleLoading"
        collapse-tags
        collapse-tags-tooltip
        filterable
        fit-input-width
        multiple
        placeholder="请选择角色"
        :reserve-keyword="false"
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
