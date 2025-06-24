<template>
  <el-drawer v-model="visible" size="60%">
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
          maxlength="20"
          show-word-limit
          :disabled="isEdit"
        >
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('views.userManage.userForm.nick_name.label')" prop="nick_name" >
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
        <el-input v-model="userForm.phone"
                  :placeholder="$t('views.userManage.userForm.phone.placeholder')">
        </el-input>
      </el-form-item>
      <el-form-item label="默认密码" v-if="!isEdit">
        <span>{{ userForm.password }}</span>
      </el-form-item>
    </el-form>
    <h4 class="title-decoration-1 mb-16 mt-8" v-if="user.isEE()">
      {{ $t('views.userManage.roleSetting') }}</h4>
    <MemberFormContent ref="memberFormContentRef" :models="formItemModel" v-model:form="list"
                       v-loading="memberFormContentLoading"
                       :addText="$t('views.userManage.addRole')" v-if="user.isEE()"/>
    <template #footer>
      <el-button @click.prevent="visible = false"> {{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="submit(userFormRef)" :loading="loading">
        {{ $t('common.save') }}
      </el-button>
    </template>
  </el-drawer>
</template>
<script setup lang="ts">
import {ref, reactive, watch, onBeforeMount} from 'vue'
import type {FormInstance} from 'element-plus'
import userManageApi from '@/api/system/user-manage'
import {MsgSuccess} from '@/utils/message'
import {t} from '@/locales'
import type {FormItemModel} from '@/api/type/role'
import WorkspaceApi from '@/api/workspace/workspace'
import MemberFormContent from '@/views/system/role/component/MemberFormContent.vue'
import {RoleTypeEnum} from '@/enums/system'
import useStore from "@/stores";

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

const list = ref<any[]>([]);
const memberFormContentLoading = ref(false);
const formItemModel = ref<FormItemModel[]>([]);
const roleFormItem = ref<FormItemModel[]>([]);
const adminRoleList = ref<any[]>([])
const workspaceFormItem = ref<FormItemModel[]>([])

async function getRoleFormItem() {
  try {
    const res = await WorkspaceApi.getWorkspaceRoleList(memberFormContentLoading);
    roleFormItem.value = [{
      path: 'role_id',
      label: t('views.role.member.role'),
      rules: [
        {
          required: true,
          message: `${t('common.selectPlaceholder')}${t('views.role.member.role')}`,
        },
      ],
      selectProps: {
        options: res.data?.map(item => ({
          label: item.name,
          value: item.id
        })) || [],
        placeholder: `${t('common.selectPlaceholder')}${t('views.role.member.role')}`,
        multiple: false
      }
    }]
    adminRoleList.value = res.data.filter(item => item.type === RoleTypeEnum.ADMIN)
  } catch (e) {
    console.error(e);
  }
}

async function getWorkspaceFormItem() {
  try {
    const res = await WorkspaceApi.getWorkspaceList(memberFormContentLoading)
    workspaceFormItem.value = [
      {
        path: 'workspace_ids',
        label: t('views.role.member.workspace'),
        hidden: (e) => adminRoleList.value.find(item => item.id === e.role_id),
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
  if (user.isEE()) {
    await getRoleFormItem();
    await getWorkspaceFormItem();
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
      max: 20,
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
      max: 20,
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
    list.value = data.role_setting
    isEdit.value = true
  } else {
    //需要查询默认密码是啥zxl
    userManageApi.getSystemDefaultPassword().then((res: any) => {
      userForm.value.password = res.data.password
    })
  }

  visible.value = true
}

const memberFormContentRef = ref<InstanceType<typeof MemberFormContent>>()
const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      memberFormContentRef.value?.validate().then(async (valid: any) => {
        if (valid) {
          const params = {
            ...userForm.value,
            role_setting: list.value
          }
          if (isEdit.value) {
            userManageApi.putUserManage(userForm.value.id, params, loading).then((res) => {
              emit('refresh')
              MsgSuccess(t('common.editSuccess'))
              visible.value = false
            })
          } else {
            userManageApi.postUserManage(params, loading).then((res) => {
              emit('refresh')
              MsgSuccess(t('common.createSuccess'))
              visible.value = false
            })
          }
        }
      })
    }
  })
}

defineExpose({open})
</script>
<style lang="scss" scoped></style>
