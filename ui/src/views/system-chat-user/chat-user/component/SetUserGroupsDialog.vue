<template>
  <el-dialog width="600" :title="$t('views.chatUser.setUserGroups')" v-model="dialogVisible"
    :close-on-click-modal="false" :close-on-press-escape="false" :destroy-on-close="true">
    <el-form label-position="top" ref="formRef" :rules="rules" :model="form" require-asterisk-position="right">
      <el-form-item :label="$t('views.chatUser.settingMethod')" prop="is_append">
        <el-radio-group v-model="form.is_append">
          <el-radio :value="true">{{ $t('views.chatUser.append') }}</el-radio>
          <el-radio :value="false">{{ $t('views.applicationOverview.SettingDisplayDialog.replace') }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item :label="$t('views.chatUser.group.title')" prop="user_group_ids">
        <el-select v-model="form.user_group_ids" multiple filterable :placeholder="$t('common.selectPlaceholder')"
          :loading="props.optionLoading">
          <el-option v-for="item in props.chatGroupList" :key="item.id" :label="item.name" :value="item.id">
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
import { ref, reactive } from 'vue'
import type { FormInstance } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import userManageApi from '@/api/system/chat-user'
import type { ListItem } from '@/api/type/common'
import {loadPermissionApi} from "@/utils/dynamics-api/permission-api.ts";

const props = defineProps<{
  optionLoading: boolean,
  chatGroupList: ListItem[],
}>()

const emit = defineEmits<{
  (e: 'refresh'): void;
}>();

const dialogVisible = ref<boolean>(false)
const defaultForm = {
  user_group_ids: [],
  is_append: true,
  ids: []
}
const form = ref<{
  ids: string[], user_group_ids: string[], is_append: boolean
}>({
  ...defaultForm,
})

function open(ids: string[]) {
  form.value = { ...defaultForm, ids }
  dialogVisible.value = true
}

const formRef = ref<FormInstance>();

const rules = reactive({
  user_group_ids: [{ required: true, message: t('common.selectPlaceholder'), trigger: 'blur' }],
  is_append: [{ required: true, message: t('common.selectPlaceholder'), trigger: 'blur' }],
})

const loading = ref<boolean>(false)
const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      loadPermissionApi('chatUser').batchAddGroup(form.value, loading).then(() => {
        MsgSuccess(t('common.settingSuccess'))
        emit('refresh')
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
