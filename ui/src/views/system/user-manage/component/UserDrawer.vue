<template>
  <el-drawer v-model="visible" size="600">
    <template #header>
      <h4>{{ title }}</h4>
    </template>
    <h4 class="title-decoration-1 mb-16 mt-8">{{ $t('common.info') }}</h4>
    <el-form
      ref="userFormRef"
      :model="userForm"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <el-form-item
        :prop="isEdit ? '' : 'username'"
        :label="$t('views.login.loginForm.username.label')"
      >
        <el-input
          v-model="userForm.username"
          :placeholder="$t('views.login.loginForm.username.placeholder')"
          maxlength="64"
          show-word-limit
          :disabled="isEdit"
        >
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('views.userManage.userForm.nick_name.label')" prop="nick_name">
        <el-input
          v-model="userForm.nick_name"
          :placeholder="$t('views.userManage.userForm.nick_name.placeholder')"
          maxlength="64"
          show-word-limit
        >
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('views.login.loginForm.email.label')" prop="email">
        <el-input
          type="email"
          v-model="userForm.email"
          :placeholder="$t('views.login.loginForm.email.placeholder')"
        >
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('views.userManage.userForm.phone.label')" prop="phone">
        <el-input
          v-model="userForm.phone"
          :placeholder="$t('views.userManage.userForm.phone.placeholder')"
        >
        </el-input>
      </el-form-item>
      <el-form-item label="默认密码" v-if="!isEdit">
        <span>{{ userForm.password }}</span>
      </el-form-item>
    </el-form>
    <h4 class="title-decoration-1 mb-16 mt-8" v-if="user.isEE() || user.isPE()">
      {{ $t('views.userManage.roleSetting') }}
    </h4>
    <MemberFormContent
      ref="memberFormContentRef"
      :models="formItemModel"
      v-model:form="list"
      v-loading="memberFormContentLoading"
      keepOneLine
      :addText="$t('views.userManage.addRole')"
      v-if="user.isEE() || user.isPE()"
      :deleteButtonDisabled="deleteButtonDisabled"
    />
    <template #footer>
      <div style="display: flex; width: 100%;">
        <el-button @click="openDialog" v-if="!isEdit && showPermission">
          {{ $t('views.system.resourceAuthorization.setting.defaultPermission') }}
        </el-button>
        <div style="margin-left: auto;">
          <el-button @click.prevent="visible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="submit(userFormRef)" :loading="loading">
            {{ $t('common.save') }}
          </el-button>
        </div>
      </div>

    </template>
  </el-drawer>
  <el-dialog
    v-model="dialogVisible"
    :title="$t('views.system.resourceAuthorization.setting.defaultPermission')"
    destroy-on-close
    @close="closeDialog"
  >
    <template #header="{ titleId, titleClass }" v-if="user.isEE()">
      <div class="dialog-header">
        <h4 :id="titleId" :class="titleClass" style="margin: 0;">
          {{ $t('views.system.resourceAuthorization.setting.defaultPermission') }}
          <span class="dialog-subtitle">
          {{ $t('views.system.resourceAuthorization.setting.defaultPermissionTip') }}
        </span>
        </h4>
      </div>
    </template>
    <el-radio-group v-model="radioPermission" class="radio-block">
      <template v-for="(item, index) in permissionOptions" :key="index">
        <el-radio :value="item.value" class="mr-16">
          <p class="color-text-primary lighter">{{ item.label }}</p>
          <el-text class="color-secondary lighter">{{ item.desc }}</el-text>
        </el-radio>
      </template>
    </el-radio-group>
    <template #footer>
      <div class="dialog-footer mt-24">
        <el-button @click="closeDialog"> {{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submitDialog"> {{ $t('common.confirm') }}</el-button>
      </div>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import {ref, reactive, watch, onBeforeMount, computed} from 'vue'
import type {FormInstance} from 'element-plus'
import userManageApi from '@/api/system/user-manage'
import {MsgSuccess} from '@/utils/message'
import {t} from '@/locales'
import type {FormItemModel} from '@/api/type/role'
import WorkspaceApi from '@/api/workspace/workspace'
import MemberFormContent from '@/views/system/role/component/MemberFormContent.vue'
import {AuthorizationEnum, RoleTypeEnum} from '@/enums/system'
import useStore from '@/stores'
import {hasPermission} from "@/utils/permission";
import {EditionConst} from "@/utils/permission/data.ts";

const {user} = useStore()
const props = defineProps({
  title: String,
})

const emit = defineEmits(['refresh'])

const userFormRef = ref()
const userForm = ref<any>({
  username: '',
  email: '',
  password: '',
  phone: '',
  nick_name: '',
})

const list = ref<any[]>([])
const memberFormContentLoading = ref(false)
const formItemModel = ref<FormItemModel[]>([])
const roleFormItem = ref<FormItemModel[]>([])
const adminRoleList = ref<any[]>([])
const userRoleList = ref<any[]>([])
const workspaceFormItem = ref<FormItemModel[]>([])

const isAdmin = computed(() => userForm.value['id'] === 'f0dd8f71-e4ee-11ee-8c84-a8a1595801ab')
const dialogVisible = ref(false)
const radioPermission = ref('NOT_AUTH')
const defaultPermission = ref('NOT_AUTH')
const permissionOptions = computed(() => {
  const baseOptions = [
    {
      label: t('views.system.resourceAuthorization.setting.check'),
      value: AuthorizationEnum.VIEW,
      desc: t('views.system.resourceAuthorization.setting.checkDesc'),
    },
    {
      label: t('views.system.resourceAuthorization.setting.management'),
      value: AuthorizationEnum.MANAGE,
      desc: t('views.system.resourceAuthorization.setting.managementDesc'),
    },
    {
      label: t('views.system.resourceAuthorization.setting.notAuthorized'),
      value: AuthorizationEnum.NOT_AUTH,
      desc: '',
    }
  ];

  if (hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR')) {
    baseOptions.splice(2, 0, {
      label: t('views.system.resourceAuthorization.setting.role'),
      value: AuthorizationEnum.ROLE,
      desc: t('views.system.resourceAuthorization.setting.roleDesc'),
    });
  }

  return baseOptions;
});

const showPermission = computed(() => {
  //社区版本的可以显示 别的版本 过期了 也可以显示
  if (user.isCE() || user.isExpire()) {
    return true
  }
  const hasUserRole = list.value.some((item) => userRoleList.value.includes(item.role_id));
  return (user.isEE() || user.isPE()) && hasUserRole
})


function deleteButtonDisabled(element: any) {
  return isAdmin.value && ['ADMIN', 'WORKSPACE_MANAGE', 'USER'].includes(element.role_id);

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
          multiple: false,
        },
      },
    ]
    adminRoleList.value = res.data.filter((item) => item.type === RoleTypeEnum.ADMIN)
    userRoleList.value = res.data
      .filter((item) => item.type === RoleTypeEnum.USER)
      .map((item) => item.id)

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
              disabledFunction: (e: any) =>
                isAdmin.value &&
                ['WORKSPACE_MANAGE', 'USER'].includes(e.role_id) &&
                item.id === 'default',
            })) || [],
          placeholder: `${t('common.selectPlaceholder')}${t('views.role.member.workspace')}`,
          clearableFunction: (e) => {
            return !(isAdmin.value && ['WORKSPACE_MANAGE', 'USER'].includes(e.role_id))
          },
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
  list.value = [{role_id: '', workspace_ids: []}]
})

const rules = reactive({
  username: [
    {
      required: true,
      message: t('views.login.loginForm.username.requiredMessage'),
      trigger: 'blur',
    },
    {
      min: 4,
      max: 64,
      message: t('views.login.loginForm.username.lengthMessage'),
      trigger: 'blur',
    },
  ],
  nick_name: [
    {
      required: true,
      message: t('views.userManage.userForm.nick_name.placeholder'),
      trigger: 'blur',
    },
    {
      min: 1,
      max: 64,
      message: t('views.userManage.userForm.nick_name.lengthMessage'),
      trigger: 'blur',
    },
  ],
  email: [
    {
      required: true,
      message: t('views.login.loginForm.email.requiredMessage'),
      trigger: 'blur',
    },
  ],
  password: [
    {
      required: true,
      message: t('views.login.loginForm.password.requiredMessage'),
      trigger: 'blur',
    },
    {
      min: 6,
      max: 20,
      message: t('views.login.loginForm.password.lengthMessage'),
      trigger: 'blur',
    },
  ],
  phone: [
    {
      pattern: /^1[3-9]\d{9}$/,
      message: t('views.userManage.userForm.phone.invalidMessage'),
      trigger: 'blur',
    },
  ],
})
const visible = ref<boolean>(false)
const loading = ref(false)
const isEdit = ref(false)

watch(visible, (bool) => {
  if (!bool) {
    userForm.value = {
      username: '',
      email: '',
      password: '',
      phone: '',
      nick_name: '',
    }
    isEdit.value = false
    list.value = [{role_id: '', workspace_ids: []}]
    userFormRef.value?.clearValidate()
  }
})

const open = (data: any) => {
  if (data) {
    userForm.value['id'] = data.id
    userForm.value.username = data.username
    userForm.value.email = data.email
    userForm.value.password = data.password
    userForm.value.phone = data.phone
    userForm.value.nick_name = data.nick_name
    list.value = data.role_setting?.map((item: any) => ({
      ...item,
      workspace_ids: item.workspace_ids.includes('None') ? [] : item.workspace_ids,
    }))
    isEdit.value = true
  } else {
    userManageApi.getSystemDefaultPassword().then((res: any) => {
      userForm.value.password = res.data.password
    })
  }
  if (memberFormContentRef.value) {
    memberFormContentRef.value.resetValidation()
  }

  visible.value = true
}

const memberFormContentRef = ref<InstanceType<typeof MemberFormContent>>()
const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate(async (valid, fields) => {
    if (valid) {
      if (memberFormContentRef.value) {
        await memberFormContentRef.value?.validate()
      }
      if (user.isPE() || user.isEE()) {
        list.value = list.value.map((item) => {
          const isAdminRole = adminRoleList.value.find((item1) => item1.id === item.role_id)

          // 如果是管理员角色，则设置为 ['None']
          if (isAdminRole) {
            return {...item, workspace_ids: ['None']}
          }

          // 如果是普通用户且是 PE 类型，则设置为 ['default']
          if (user.isPE()) {
            return {...item, workspace_ids: ['default']}
          }

          // 其他情况保持原样
          return item
        })
      }
      const params = {
        ...userForm.value,
        role_setting: list.value,
      }
      if (isEdit.value) {
        userManageApi
          .putUserManage(userForm.value.id, params, loading)
          .then((res) => {
            return user.profile(loading).then(() => {
              return res
            })
          })
          .then((res) => {
            emit('refresh')
            MsgSuccess(t('common.editSuccess'))
            visible.value = false
          })
      } else {
        params.defaultPermission = defaultPermission.value
        userManageApi
          .postUserManage(params, loading)
          .then((res) => {
            return user.profile(loading).then(() => {
              return res
            })
          })
          .then((res) => {
            emit('refresh')
            MsgSuccess(t('common.createSuccess'))
            visible.value = false
          })
      }
    }
  })
}

const openDialog = () => {
  dialogVisible.value = true
}

const closeDialog = () => {
  dialogVisible.value = false
}

const submitDialog = () => {
  defaultPermission.value = radioPermission.value
  closeDialog()
}


defineExpose({open})
</script>
<style lang="scss" scoped>
.dialog-header {
  h4 {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin: 0;
  }

  .dialog-subtitle {
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }
}

</style>
