<template>
  <el-drawer v-model="visible" size="600" :destroy-on-close="true" :before-close="handleCancel">
    <template #header>
      <h4>{{ $t('views.role.member.add') }}</h4>
    </template>
    <template #default>
      <MemberFormContent
        ref="memberFormContentRef"
        :models="formItemModel"
        v-model:form="list"
        v-loading="memberFormContentLoading"
        keepOneLine
      />
    </template>
    <template #footer>
      <el-button @click="handleCancel">{{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="handleAdd()" :loading="loading">
        {{ $t('common.add') }}
      </el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import {onBeforeMount, ref} from 'vue'
import type {CreateMemberParamsItem, FormItemModel} from '@/api/type/role'
import UserApi from '@/api/user/user'
import WorkspaceApi from '@/api/workspace/workspace'
import MemberFormContent from './MemberFormContent.vue'
import {t} from '@/locales'
import type {RoleItem} from '@/api/type/role'
import {MsgSuccess} from '@/utils/message'
import {RoleTypeEnum} from '@/enums/system'
import {loadPermissionApi} from '@/utils/dynamics-api/permission-api'
import useStore from "@/stores";

const {user} = useStore()
const props = defineProps<{
  currentRole?: RoleItem
}>()

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const loading = ref(false)
const visible = ref(false)
const list = ref<CreateMemberParamsItem[]>([])

const memberFormContentLoading = ref(false)
const formItemModel = ref<FormItemModel[]>([])
const userFormItem = ref<FormItemModel[]>([])
const workspaceFormItem = ref<FormItemModel[]>([])

async function getUserFormItem() {
  try {
    const res = await UserApi.getUserList(memberFormContentLoading)
    userFormItem.value = [
      {
        path: 'user_ids',
        label: t('views.role.member.title'),
        rules: [
          {
            required: true,
            message: `${t('common.selectPlaceholder')}${t('views.role.member.title')}`,
          },
        ],
        selectProps: {
          options:
            res.data?.map((item) => ({
              label: item.nick_name,
              value: item.id,
            })) || [],
          placeholder: `${t('common.selectPlaceholder')}${t('views.role.member.title')}`,
        },
      },
    ]
  } catch (e) {
    console.error(e)
  }
}

async function getWorkspaceFormItem() {
  try {
    const res = await loadPermissionApi('workspace').getWorkspaceList(memberFormContentLoading)
    workspaceFormItem.value = [
      {
        path: 'workspace_ids',
        label: t('views.role.member.workspace'),
        rules: [
          {
            required: true,
            message: `${t('common.selectPlaceholder')}${t('views.role.member.workspace')}`,
          },
        ],
        selectProps: {
          options:
            res.data?.map((item: any) => ({
              label: item.name,
              value: item.id,
            })) || [],
          placeholder: `${t('common.selectPlaceholder')}${t('views.role.member.workspace')}`,
        },
      },
    ]
  } catch (e) {
    console.error(e)
  }
}

function init() {
  if (props.currentRole?.type !== RoleTypeEnum.ADMIN) {
    formItemModel.value = [...userFormItem.value, ...workspaceFormItem.value]
    list.value = [{user_ids: [], workspace_ids: []}]
  } else {
    formItemModel.value = [...userFormItem.value]
    list.value = [{user_ids: []}]
  }
}

onBeforeMount(async () => {
  await getUserFormItem()
  if (user.isEE()) {
    await getWorkspaceFormItem()
  }
  init()
})

function open() {
  init()
  visible.value = true
}

function handleCancel() {
  visible.value = false
}

const memberFormContentRef = ref<InstanceType<typeof MemberFormContent>>()

function handleAdd() {
  memberFormContentRef.value?.validate().then(async (valid: any) => {
    if (valid) {
      let params
      if (props.currentRole?.type === RoleTypeEnum.ADMIN) {
        params = list.value.map((item) => ({user_ids: item.user_ids, workspace_ids: ['None']}))
      } else if (user.isPE()) {
        params = list.value.map((item) => ({user_ids: item.user_ids, workspace_ids: ['default']}))
      }
      await loadPermissionApi('role').CreateMember(
        props.currentRole?.id as string,
        {members: params ?? list.value},
        loading,
      )
      MsgSuccess(t('common.addSuccess'))
      handleCancel()
      emit('refresh')
    }
  })
}

defineExpose({open})
</script>
