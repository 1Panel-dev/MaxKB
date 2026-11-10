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
          remote
          :reserve-keyword="false"
          :placeholder="$t('common.selectPlaceholder')"
          :loading="optionLoading"
          :remote-method="filterUser"
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

async function fetchUserOptions(query?: string) {
  try {
    const res = await loadPermissionApi('chatUser').getChatUserList(
      query ? { nick_name: query } : {},
      optionLoading,
    )
    chatUserList.value = (res.data || []) as ChatUserItem[]
  } catch (e) {
    console.error(e)
  }
}

const filterUser = (query: string) => fetchUserOptions(query)

onBeforeMount(() => {
  fetchUserOptions()
})

const groupId = ref('')

function open(id: string) {
  form.value = { ...defaultForm }
  groupId.value = id
  dialogVisible.value = true
  fetchUserOptions()
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
