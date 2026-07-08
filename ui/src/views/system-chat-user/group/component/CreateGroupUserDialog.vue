<template>
  <el-dialog
    :title="$t('views.role.member.add')"
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
      <el-form-item :label="$t('views.chatUser.group.usernameOrName')" prop="user">
        <el-select
          v-model="form.user"
          multiple
          filterable
          :reserve-keyword="false"
          :placeholder="$t('common.selectPlaceholder')"
          :loading="optionLoading"
          :filter-method="filterUser"
        >
          <el-option
            v-for="item in chatUserList"
            :key="item.id"
            :label="item.nick_name"
            :value="item.id"
          >
          </el-option>
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(formRef)" :loading="loading">
          {{ $t('common.add') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onBeforeMount } from 'vue'
import type { FormInstance } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import SystemGroupApi from '@/api/system/user-group'
import userManageApi from '@/api/system/chat-user'
import type { ChatUserItem } from '@/api/type/systemChatUser'
import { loadPermissionApi } from '@/utils/dynamics-api/permission-api.ts'

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const dialogVisible = ref<boolean>(false)
const defaultForm = {
  user: [],
}
const form = ref<{ user: string[] }>({
  ...defaultForm,
})

const optionLoading = ref(false)
const chatUserList = ref<ChatUserItem[]>([])
const originalChatUserList = ref<ChatUserItem[]>([])
async function getChatUserList() {
  try {
    const res = await loadPermissionApi('chatUser').getChatUserList(optionLoading)
    originalChatUserList.value = res.data
    chatUserList.value = [...res.data]
  } catch (e) {
    console.error(e)
  }
}

const filterUser = (query: string) => {
  if (!query) {
    chatUserList.value = originalChatUserList.value
    return
  }

  const q = query.toLowerCase()
  chatUserList.value = originalChatUserList.value.filter(
    (item) => item.nick_name?.toLowerCase().includes(q) || item.username?.toLowerCase().includes(q),
  )
}

onBeforeMount(() => {
  getChatUserList()
})

const groupId = ref('')

function open(id: string) {
  form.value = { ...defaultForm }
  groupId.value = id
  dialogVisible.value = true
}

const formRef = ref<FormInstance>()

const rules = reactive({
  user: [{ required: true, message: t('common.selectPlaceholder'), trigger: 'blur' }],
})

const loading = ref<boolean>(false)
const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      loadPermissionApi('userGroup')
        .postAddMember(groupId.value, { user_ids: form.value.user }, loading)
        .then(() => {
          MsgSuccess(t('common.addSuccess'))
          emit('refresh')
          dialogVisible.value = false
        })
    }
  })
}

defineExpose({ open })
</script>
