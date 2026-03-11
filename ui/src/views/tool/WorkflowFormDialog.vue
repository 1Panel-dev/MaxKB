<template>
  <el-dialog
    :title="title"
    v-model="dialogVisible"
    width="720"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form
      ref="FolderFormRef"
      :rules="rules"
      :model="workflowForm"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="$t('common.name')" prop="name">
        <el-input
          v-model="workflowForm.name"
          :placeholder="$t('components.folder.folderNamePlaceholder')"
          maxlength="64"
          show-word-limit
          @blur="workflowForm.name = workflowForm.name.trim()"
        />
      </el-form-item>
      <el-form-item :label="$t('common.desc')" prop="desc">
        <el-input
          v-model="workflowForm.desc"
          type="textarea"
          :placeholder="$t('common.descPlaceholder')"
          maxlength="128"
          show-word-limit
          :autosize="{ minRows: 3 }"
          @blur="workflowForm.desc = workflowForm.desc.trim()"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false" :loading="loading">
          {{ $t('common.cancel') }}
        </el-button>
        <el-button type="primary" @click="submitHandle" :disabled="loading" :loading="loading">
          {{ isEdit ? $t('common.confirm') : $t('common.add') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import folderApi from '@/api/workspace/folder'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import useStore from '@/stores'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
const { user, tool, knowledge, folder } = useStore()
const emit = defineEmits(['refresh'])

const props = defineProps({
  title: {
    type: String,
    default: t('components.folder.addFolder'),
  },
})

const FolderFormRef = ref()
const route = useRoute()
const loading = ref(false)
const dialogVisible = ref<boolean>(false)
const sourceType = ref<any>('')
const isEdit = ref<boolean>(false)
const editId = ref<string>('')
const default_workflow = {}
const workflowForm = ref<any>({
  name: '',
  desc: '',
  tool_type: 'WORKFLOW',
  work_flow: {},
})

const rules = reactive({
  name: [
    {
      required: true,
      message: t('views.tool.form.toolName.requiredMessage'),
      trigger: 'blur',
    },
  ],
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    sourceType.value = ''
    workflowForm.value = {
      name: '',
      desc: '',
      tool_type: 'WORKFLOW',
      work_flow: {},
    }
    isEdit.value = false
    FolderFormRef.value.resetFields()
  }
})

const open = (source: string, data?: any) => {
  sourceType.value = source
  if (data) {
    //  编辑当前id
    editId.value = data.id
    workflowForm.value.name = data.name
    workflowForm.value.desc = data.desc
    isEdit.value = true
  }
  dialogVisible.value = true
}
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const submitHandle = async () => {
  await FolderFormRef.value.validate((valid: any) => {
    if (valid) {
      if (isEdit.value) {
        loadSharedApi({ type: 'tool', systemType: apiType.value })
          .putTool(workflowForm.value?.id as string, workflowForm.value)
          .then((res: any) => {
            MsgSuccess(t('common.editSuccess'))
            emit('refresh', res.data)
            return user.profile()
          })
          .then(() => {
            dialogVisible.value = false
          })
          .finally(() => {
            loading.value = false
          })
      } else {
        loadSharedApi({ type: 'tool', systemType: apiType.value })
          .postTool({ ...workflowForm.value, folder_id: folder.currentFolder?.id, code: 'None' })
          .then((res: any) => {
            MsgSuccess(t('common.createSuccess'))
            emit('refresh', res.data)
            return user.profile()
          })
          .then(() => {
            dialogVisible.value = false
          })
          .finally(() => {
            loading.value = false
          })
      }
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
