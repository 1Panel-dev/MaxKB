<template>
  <el-dialog
    width="600"
    :title="$t('views.userManage.settingRole')"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
  >
    <el-form
      label-position="top"
      ref="formRef"
      :rules="rules"
      :model="form"
      require-asterisk-position="right"
    >
      <el-form-item :label="$t('views.chatUser.settingMethod')">
        <el-radio-group v-model="form.is_append">
          <el-radio :value="true">{{ $t('views.chatUser.append') }}</el-radio>
          <el-radio :value="false"
            >{{ $t('views.applicationOverview.SettingDisplayDialog.replace') }}
          </el-radio>
        </el-radio-group>
      </el-form-item>

      <MemberFormContent
        ref="memberFormContentRef"
        :models="formItemModel"
        v-model:form="list"
        v-loading="memberFormContentLoading"
        keepOneLine
        :need-add-button="!user.isPE()"
        :addText="$t('views.userManage.addRole')"
        v-if="user.isEE() || user.isPE()"
      />
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(formRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onBeforeMount } from 'vue'
import type { FormInstance } from 'element-plus'
import { t } from '@/locales'

const memberFormContentLoading = ref(false)
import userManageApi from '@/api/system/user-manage'
import MemberFormContent from '@/views/system/role/component/MemberFormContent.vue'
import type { FormItemModel } from '@/api/type/role.ts'
import WorkspaceApi from '@/api/workspace/workspace.ts'
import useStore from '@/stores'
import { RoleTypeEnum } from '@/enums/system.ts'
import { loadPermissionApi } from '@/utils/dynamics-api/permission-api.ts'
import { MsgSuccess } from '@/utils/message.ts'

const list = ref<any[]>([])
const formItemModel = ref<FormItemModel[]>([])
const { user, common } = useStore()
const workspaceFormItem = ref<FormItemModel[]>([])
const roleFormItem = ref<FormItemModel[]>([])

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const dialogVisible = ref<boolean>(false)
const defaultForm = {
  role_ids: [],
  is_append: true,
  ids: [],
}
const form = ref<{
  ids: string[]
  role_ids: string[]
  is_append: boolean
}>({
  ...defaultForm,
})

function open(ids: string[]) {
  form.value = { ...defaultForm, ids }
  list.value = [{ role_id: '', workspace_ids: [] }]
   if (memberFormContentRef.value) {
    memberFormContentRef.value.resetValidation()
  }
  dialogVisible.value = true
}

const formRef = ref<FormInstance>()
const adminRoleList = ref<any[]>([])
const rules = reactive({
  is_append: [{ required: true, message: t('common.selectPlaceholder'), trigger: 'blur' }],
})

const memberFormContentRef = ref<InstanceType<typeof MemberFormContent>>()
const loading = ref<boolean>(false)
const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate(async (valid) => {
    if (valid) {
      if (memberFormContentRef.value) {
        await memberFormContentRef.value?.validate()
      }
      if (user.isPE()) {
        const data = {
          is_append: form.value.is_append,
          ids: form.value.ids,
          role_ids: list.value[0].role_id,
        }
        userManageApi.batchSetRolePE(data, loading).then(() => {
          MsgSuccess(t('common.settingSuccess'))
          emit('refresh')
          dialogVisible.value = false
        })
      }
      if (user.isEE()) {
        list.value = list.value.map((item) => {
          const isAdminRole = adminRoleList.value.find((item1) => item1.id === item.role_id)

          // 如果是管理员角色，则设置为 ['None']
          if (isAdminRole) {
            return {...item, workspace_ids: ['None']}
          }
          return item
        })
        const data = {
          is_append: form.value.is_append,
          ids: form.value.ids,
          role_setting: list.value,
        }
        userManageApi.batchSetRoleEE(data, loading).then(() => {
          MsgSuccess(t('common.settingSuccess'))
          emit('refresh')
          dialogVisible.value = false
        })
      }
    }
  })
}

async function getRoleFormItem() {
  try {
    const res = await WorkspaceApi.getWorkspaceRoleList(memberFormContentLoading)
    roleFormItem.value = [
      {
        path: 'role_id',
        label: t('views.role.member.role'),
        rules: [
          {
            required: true,
            message: `${t('common.selectPlaceholder')}${t('views.role.member.role')}`,
          },
        ],
        selectProps: {
          options:
            res.data?.map((item) => ({
              label: item.name,
              value: item.id,
            })) || [],
          placeholder: `${t('common.selectPlaceholder')}${t('views.role.member.role')}`,
          multiple: !!user.isPE(),
        },
      },
    ]
    adminRoleList.value = res.data.filter((item) => item.type === RoleTypeEnum.ADMIN)
  } catch (e) {
    console.error(e)
  }
}

async function getWorkspaceFormItem() {
  try {
    const res = await WorkspaceApi.getWorkspaceList(memberFormContentLoading)
    workspaceFormItem.value = [
      {
        path: 'workspace_ids',
        label: t('views.role.member.workspace'),
        hidden: (e) => adminRoleList.value.find((item) => item.id === e.role_id),
        rules: [
          {
            validator: (rule, value, callback) => {
              const match = rule.field?.match(/\[(\d+)\]/)
              const isAdmin = adminRoleList.value.some(
                (role) => role.id === list.value[parseInt(match?.[1] ?? '', 10)].role_id,
              )
              if (!isAdmin && (!value || value.length === 0)) {
                callback(
                  new Error(`${t('common.selectPlaceholder')}${t('views.role.member.workspace')}`),
                )
              } else {
                callback()
              }
            },
            trigger: 'blur',
          },
        ],
        selectProps: {
          options:
            res.data?.map((item) => ({
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

onBeforeMount(async () => {
  if (user.isEE() || user.isPE()) {
    await getRoleFormItem()
    if (user.isEE()) {
      await getWorkspaceFormItem()
    }
    formItemModel.value = [...roleFormItem.value, ...workspaceFormItem.value]
  }
  list.value = [{ role_id: '', workspace_ids: [] }]
})

defineExpose({ open })
</script>
