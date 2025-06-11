<template>
  <el-drawer v-model="visible" size="600" :destroy-on-close="true" :before-close="handleCancel">
    <template #header>
      <h4>{{ $t('views.role.member.add') }}</h4>
    </template>
    <template #default>
      <MemberFormContent ref="memberFormContentRef" :models="formItemModel" v-model:form="list" />
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
import { onBeforeMount, ref } from 'vue'
import type { CreateMemberParamsItem, FormItemModel } from '@/api/type/role'
import RoleApi from '@/api/system/role'
import UserApi from '@/api/user/user'
import MemberFormContent from './MemberFormContent.vue'
import { t } from '@/locales'
import { MsgSuccess } from '@/utils/message'

const props = defineProps<{
  roleId: string
}>()

const emit = defineEmits<{
  (e: 'refresh'): void;
}>();

const loading = ref(false)
const visible = ref(false)
const list = ref<CreateMemberParamsItem[]>([]);

const formItemModel = ref<FormItemModel[]>([
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
      options: [],
      placeholder: `${t('common.selectPlaceholder')}${t('views.role.member.title')}`
    }
  },
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
      options: [], // TODO
      placeholder: `${t('common.selectPlaceholder')}${t('views.role.member.workspace')}`
    }
  },
]);
onBeforeMount(async () => {
  const res = await UserApi.getUserList();
  formItemModel.value[0].selectProps.options = res.data?.map(item => ({ label: item.nick_name, value: item.id }))
})

function open() {
  visible.value = true
}

function handleCancel() {
  visible.value = false
  list.value = []
}

const memberFormContentRef = ref<InstanceType<typeof MemberFormContent>>()
function handleAdd() {
  memberFormContentRef.value?.validate().then(async (valid) => {
    if (valid) {
      await RoleApi.CreateMember(props.roleId, { members: list.value }, loading)
      MsgSuccess(t('common.addSuccess'))
      handleCancel();
      emit('refresh')
    }
  })
}

defineExpose({ open })
</script>