<template>
  <el-dialog
    :title="title"
    v-model="dialogVisible"
    width="550"
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
      <el-form-item :label="$t('views.tool.form.workflowName.label')" prop="name">
        <div class="flex w-full">
          <div
            v-if="isEdit"
            class="edit-avatar mr-12"
            @mouseenter="showEditIcon = true"
            @mouseleave="showEditIcon = false"
          >
            <el-Avatar
              v-if="isAppIcon(workflowForm.icon)"
              :id="editId"
              shape="square"
              :size="32"
              style="background: none"
            >
              <img :src="String(workflowForm.icon)" alt=""/>
            </el-Avatar>
            <el-avatar v-else class="avatar-green" shape="square" :size="32">
              <img src="@/assets/workflow/logo_workflow.svg" style="width: 58%" alt=""/>
            </el-avatar>
            <el-Avatar
              v-if="showEditIcon"
              :id="editId"
              shape="square"
              class="edit-mask"
              :size="32"
              @click="openEditAvatar"
            >
              <AppIcon iconName="app-edit"></AppIcon>
            </el-Avatar>
          </div>
          <el-avatar v-else class="avatar-green mr-12" shape="square" :size="32">
            <img src="@/assets/workflow/logo_workflow.svg" style="width: 58%" alt=""/>
          </el-avatar>
          <el-input
            v-model="workflowForm.name"
            :placeholder="$t('views.tool.form.workflowName.placeholder')"
            maxlength="64"
            show-word-limit
            @blur="workflowForm.name = workflowForm.name.trim()"
          />
        </div>
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
    <EditAvatarDialog ref="EditAvatarDialogRef" @refresh="refreshTool" iconType="WORKFLOW"/>
  </el-dialog>
</template>
<script setup lang="ts">
import {ref, watch, reactive, computed} from 'vue'
import {useRouter, useRoute} from 'vue-router'
import EditAvatarDialog from '@/views/tool/component/EditAvatarDialog.vue'
import {isAppIcon} from '@/utils/common'
import {MsgSuccess} from '@/utils/message'
import {t} from '@/locales'
import useStore from '@/stores'
import {loadSharedApi} from '@/utils/dynamics-api/shared-api'

const router = useRouter()
const {user, folder} = useStore()
const emit = defineEmits(['refresh'])

const props = defineProps({
  title: {
    type: String,
    default: t('common.edit'),
  },
})

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const FolderFormRef = ref()
const route = useRoute()
const loading = ref(false)
const dialogVisible = ref<boolean>(false)
const isEdit = ref<boolean>(false)
const editId = ref<string>('')
const default_workflow = {}
const showEditIcon = ref(false)
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
      message: t('views.tool.form.workflowName.requiredMessage'),
      trigger: 'blur',
    },
  ],
})

watch(dialogVisible, (bool) => {
  if (!bool) {
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
const details = ref<any>()
const open = (data?: any) => {
  if (data) {
    //  编辑当前id
    editId.value = data.id
    details.value = data
    workflowForm.value.name = data.name
    workflowForm.value.desc = data.desc
    workflowForm.value.icon = data.icon
    isEdit.value = true
  }
  dialogVisible.value = true
}

const EditAvatarDialogRef = ref()

function openEditAvatar() {
  EditAvatarDialogRef.value.open(details.value)
}

function refreshTool(data: any) {
  workflowForm.value.icon = data
}

const submitHandle = async () => {
  await FolderFormRef.value.validate((valid: any) => {
    if (valid) {
      if (isEdit.value) {
        loadSharedApi({type: 'tool', systemType: apiType.value})
          .putTool(editId.value as string, workflowForm.value)
          .then((res: any) => {
            MsgSuccess(t('common.editSuccess'))
            emit('refresh', res.data)
            return user.profile().then(() => {
              dialogVisible.value = false
            })
          })
          .finally(() => {
            loading.value = false
          })
      } else {
        loadSharedApi({type: 'tool', systemType: apiType.value})
          .postTool({...workflowForm.value, folder_id: folder.currentFolder?.id, code: 'None'})
          .then((res: any) => {
            MsgSuccess(t('common.createSuccess'))
            emit('refresh', res.data)
            return user.profile().then(() => {
              const folderId = res.data.scope === 'SHARED' ? 'shared' : res.data.folder_id
              router.push({
                name: 'ToolWorkflow',
                params: {id: res.data.id, folderId: folderId},
              })
              dialogVisible.value = false
            })
          })
          .finally(() => {
            loading.value = false
          })
      }
    }
  })
}

defineExpose({open})
</script>
<style lang="scss" scoped></style>
