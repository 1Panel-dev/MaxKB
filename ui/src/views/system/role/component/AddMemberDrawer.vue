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
import type {CreateMemberParamsItem, FormItemModel, RoleItem} from '@/api/type/role'
import UserApi from '@/api/user/user'
import MemberFormContent from './MemberFormContent.vue'
import {t} from '@/locales'
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
const userOptions = ref<Array<{ label: string; value: string }>>([])

async function getUserFormItem() {
  try {
    const fetchUserOptions = async (query?: string) => {
      const res = await UserApi.getUserList(query ? {nick_name: query} : {}, memberFormContentLoading)
      return res.data?.map((item) => ({
        label: item.nick_name,
        value: item.id,
      })) || []
    }

    // 初始加载
    userOptions.value = await fetchUserOptions()

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
          options: userOptions.value,
          placeholder: `${t('common.selectPlaceholder')}${t('views.role.member.title')}`,
          remoteMethod: async (query: string, element: any) => {
            // 关键：直接更新 selectProps.options
            const newOptions = await fetchUserOptions(query)
            // 更新当前项的 options
            const currentItem = userFormItem.value.find(
              item => item.path === 'user_ids'
            )
            if (currentItem?.selectProps) {
              currentItem.selectProps.options = newOptions
            }
            return newOptions
          }
        },
      },
    ]
  } catch (e) {
    console.error(e)
  }
}

// 同样修改 workspace
async function getWorkspaceFormItem() {
  try {
    const fetchWorkspaceOptions = async (query?: string) => {
      const res = await loadPermissionApi('workspace').getWorkspaceList(
        query ? {name: query} : {},
        memberFormContentLoading
      )
      return res.data?.map((item: any) => ({
        label: item.name,
        value: item.id,
      })) || []
    }

    const initialOptions = await fetchWorkspaceOptions()

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
          options: initialOptions,
          placeholder: `${t('common.selectPlaceholder')}${t('views.role.member.workspace')}`,
          remoteMethod: async (query: string, element: any) => {
            const newOptions = await fetchWorkspaceOptions(query)
            const currentItem = workspaceFormItem.value.find(
              item => item.path === 'workspace_ids'
            )
            if (currentItem?.selectProps) {
              currentItem.selectProps.options = newOptions
            }
            return newOptions
          }
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
