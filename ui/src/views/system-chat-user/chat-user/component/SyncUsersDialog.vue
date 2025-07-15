<template>
  <el-dialog v-model="dialogVisible" :close-on-click-modal="false" :close-on-press-escape="false"
             :destroy-on-close="true" width="600">
    <template #header>
      <h4 class="mb-8 medium">{{ t('views.chatUser.syncUsers') }}</h4>
      <div class="color-secondary lighter">{{ t('views.chatUser.syncUsersTip') }}</div>
    </template>
    <el-form label-position="top" ref="formRef" :rules="rules" :model="form"
             require-asterisk-position="right">
      <el-form-item :label="$t('views.userManage.source.label')" prop="sync_type">
        <el-select v-model="form.sync_type" :placeholder="$t('common.selectPlaceholder')">
          <el-option :label="t('views.userManage.source.local')" value="LOCAL">
          </el-option>
        </el-select>
      </el-form-item>
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
import {ref, reactive} from 'vue'
import type {FormInstance} from 'element-plus'
import {MsgError, MsgSuccess} from '@/utils/message'
import {t} from '@/locales'
import userManageApi from '@/api/system/chat-user'

const emit = defineEmits<{
  (e: 'refresh'): void;
}>();

const dialogVisible = ref<boolean>(false)
const defaultForm = {
  sync_type: 'LOCAL',
}
const form = ref<{
  sync_type: string
}>({
  ...defaultForm,
})

function open() {
  form.value = {...defaultForm}
  dialogVisible.value = true
}

const formRef = ref<FormInstance>();

const rules = reactive({
  sync_type: [{required: true, message: t('common.selectPlaceholder'), trigger: 'blur'}],
})

const loading = ref<boolean>(false)
const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      userManageApi.batchSync(form.value.sync_type, loading).then((res) => {
        if (res.data) {
          const count = res.data.success_count
          if (res.data.conflict_users && res.data.conflict_users.length > 0) {
            // 遍历res.data.conflict_users， 他是一个数组里面是对象
            let ErrorMsg = ''
            res.data.conflict_users.forEach((item: any) => {
              if (item.type === 'username') {
                ErrorMsg += '\n\n' + t('views.chatUser.syncMessage.usernameExist') + " [ " + item.users.join(',') + '\n' + ' ]'
              }
              if (item.type === 'nick_name') {
                ErrorMsg += '\n\n' + t('views.chatUser.syncMessage.nicknameExist') + " [ " + item.users.join(',') + '\n' + ' ]'
              }
            })
            MsgSuccess(t('views.chatUser.syncMessage.title', {count: count}) + ErrorMsg)
            emit('refresh')
            dialogVisible.value = false
          }
        }

      })
    }
  })
}

defineExpose({open})
</script>
