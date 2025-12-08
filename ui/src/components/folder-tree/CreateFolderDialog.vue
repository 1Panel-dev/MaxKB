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
      :model="folderForm"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="$t('common.name')" prop="name">
        <el-input
          v-model="folderForm.name"
          :placeholder="$t('components.folder.folderNamePlaceholder')"
          maxlength="64"
          show-word-limit
          @blur="folderForm.name = folderForm.name.trim()"
        />
      </el-form-item>
      <el-form-item :label="$t('common.desc')" prop="desc">
        <el-input
          v-model="folderForm.desc"
          type="textarea"
          :placeholder="$t('common.descPlaceholder')"
          maxlength="128"
          show-word-limit
          :autosize="{ minRows: 3 }"
          @blur="folderForm.desc = folderForm.desc.trim()"
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
import { ref, watch, reactive } from 'vue'
import folderApi from '@/api/folder'
import { MsgSuccess, MsgAlert } from '@/utils/message'
import { t } from '@/locales'
import useStore from '@/stores'
const { user, tool, knowledge, folder } = useStore()
const emit = defineEmits(['refresh'])

const props = defineProps({
  title: {
    type: String,
    default: t('components.folder.addFolder'),
  },
})

const FolderFormRef = ref()

const loading = ref(false)
const dialogVisible = ref<boolean>(false)
const sourceType = ref<any>('')
const isEdit = ref<boolean>(false)
const editId = ref<string>('')

const folderForm = ref<any>({
  name: '',
  desc: '',
  parent_id: '',
})

const rules = reactive({
  name: [
    {
      required: true,
      message: t('components.folder.folderNamePlaceholder'),
      trigger: 'blur',
    },
  ],
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    sourceType.value = ''
    folderForm.value = {
      name: '',
      desc: '',
      parent_id: '',
    }
    isEdit.value = false
    FolderFormRef.value.resetFields()
  }
})

const open = (source: string, id: string, data?: any) => {
  sourceType.value = source
  if (data) {
    //  编辑当前id
    editId.value = data.id
    folderForm.value.name = data.name
    folderForm.value.desc = data.desc
    folderForm.value.parent_id = data.parent_id
    isEdit.value = true
  } else {
    //  给当前id添加子id
    folderForm.value.parent_id = id
  }
  dialogVisible.value = true
}

const submitHandle = async () => {
  await FolderFormRef.value.validate((valid: any) => {
    if (valid) {
      if (isEdit.value) {
        folderApi
          .putFolder(editId.value, sourceType.value, folderForm.value, loading)
          .then((res) => {
            MsgSuccess(t('common.editSuccess'))
            emit('refresh')
            dialogVisible.value = false
          })
      } else {
        folderApi.postFolder(sourceType.value, folderForm.value, loading)
          .then((res) => {
            return user.profile().then(() => {
              return res
            })
          })
          .then((res) => {
          MsgSuccess(t('common.createSuccess'))
          folder.setCurrentFolder(res.data)
          folder.asyncGetFolder(sourceType.value, {}, loading)
          clearData()
          emit('refresh')
          dialogVisible.value = false
        })
      }
    }
  })
}

function clearData() {
  tool.setToolList([])
  knowledge.setKnowledgeList([])
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
