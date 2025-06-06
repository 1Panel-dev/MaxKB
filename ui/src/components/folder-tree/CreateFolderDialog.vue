<template>
  <el-dialog
    :title="$t('components.folder.addFolder')"
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
      <el-form-item :label="$t('components.folder.description')" prop="desc">
        <el-input
          v-model="folderForm.desc"
          type="textarea"
          :placeholder="$t('components.folder.descriptionPlaceholder')"
          maxlength="256"
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
        <el-button type="primary" @click="submitHandle" :loading="loading">
          {{ $t('common.add') }}
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
const emit = defineEmits(['refresh'])

const FolderFormRef = ref()

const loading = ref(false)
const dialogVisible = ref<boolean>(false)
const sourceType = ref<any>('')

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
  }
})

const open = (source: string, id: string) => {
  sourceType.value = source
  folderForm.value.parent_id = id
  dialogVisible.value = true
}

const submitHandle = async () => {
  await FolderFormRef.value.validate((valid: any) => {
    if (valid) {
      folderApi.postFolder( sourceType.value, folderForm.value, loading).then((res) => {
        MsgSuccess(t('common.createSuccess'))
        emit('refresh')
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
