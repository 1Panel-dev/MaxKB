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
      <div style="flex: auto">
        <el-button @click="handleCancel">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleAdd()" :loading="loading">
          {{ $t('common.add') }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import {onBeforeMount, ref} from 'vue'
import UserApi from '@/api/user/user'
import WorkspaceApi from '@/api/workspace/workspace'
import MemberFormContent from '@/views/system/role/component/MemberFormContent.vue'
import {t} from '@/locales'
import {MsgSuccess} from '@/utils/message'
import type {CreateWorkspaceMemberParamsItem, WorkspaceItem} from '@/api/type/workspace'
import type {FormItemModel} from '@/api/type/role'
import {RoleTypeEnum} from '@/enums/system'
import {loadPermissionApi} from '@/utils/dynamics-api/permission-api.ts'
import {i18n_name} from '@/utils/common'

const props = defineProps<{
  currentWorkspace?: WorkspaceItem
}>()

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const loading = ref(false)
const visible = ref(false)
const list = ref<CreateWorkspaceMemberParamsItem[]>([])

const memberFormContentLoading = ref(false)
const formItemModel = ref<FormItemModel[]>([])
const userFormItem = ref<FormItemModel[]>([])
const roleFormItem = ref<FormItemModel[]>([])
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

async function getRoleFormItem() {
  try {
    const res = await loadPermissionApi('workspace').getWorkspaceRoleList(memberFormContentLoading)
    roleFormItem.value = [
      {
        path: 'role_ids',
        label: t('views.role.member.role'),
        rules: [
          {
            required: true,
            message: `${t('common.selectPlaceholder')}${t('views.role.member.role')}`,
          },
        ],
        selectProps: {
          options:
            res.data
              .filter((item: any) => item.type !== RoleTypeEnum.ADMIN)
              ?.map((item: any) => ({
                label: i18n_name(item.name),
                value: item.id,
              })) || [],
          placeholder: `${t('common.selectPlaceholder')}${t('views.role.member.role')}`,
        },
      },
    ]
  } catch (e) {
    console.error(e)
  }
}

function init() {
  formItemModel.value = [...userFormItem.value, ...roleFormItem.value]
  list.value = [{user_ids: [], role_ids: []}]
}

onBeforeMount(async () => {
  await getUserFormItem()
  await getRoleFormItem()
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
      await loadPermissionApi('workspace').CreateWorkspaceMember(
        props.currentWorkspace?.id as string,
        list.value,
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
