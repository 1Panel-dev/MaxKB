<template>
  <el-dialog
    :title="$t('views.chatLog.editMark')"
    v-model="dialogVisible"
    width="600"
    class="edit-mark-dialog"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <template #header="{ titleId, titleClass }">
      <div class="flex-between">
        <h4 :id="titleId" :class="titleClass">{{ $t('views.chatLog.editMark') }}</h4>
        <div class="text-right">
          <el-button text @click="isEdit = true" v-if="!isEdit">
            <AppIcon iconName="app-edit"></AppIcon>
          </el-button>
          <el-button text style="margin-left: 4px" @click="deleteMark">
            <AppIcon iconName="app-delete"></AppIcon>
          </el-button>
          <el-divider direction="vertical" />
        </div>
      </div>
    </template>

    <el-scrollbar>
      <div style="min-height: 250px; max-height: 350px" v-loading="loading">
        <el-form
          v-if="isEdit"
          ref="formRef"
          :model="form"
          label-position="top"
          require-asterisk-position="right"
          :rules="rules"
          @submit.prevent
        >
          <el-form-item prop="content">
            <el-input
              v-model="form.content"
              :placeholder="$t('views.chatLog.form.content.placeholder')"
              :maxlength="100000"
              show-word-limit
              :rows="15"
              type="textarea"
            >
            </el-input>
          </el-form-item>
        </el-form>
        <span v-else class="pre-wrap">{{ form?.content }}</span>
      </div>
    </el-scrollbar>

    <template #footer>
      <span class="dialog-footer" v-if="isEdit">
        <el-button @click.prevent="isEdit = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(formRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { t } from '@/locales'
import { MsgSuccess, MsgConfirm } from '@/utils/message'

import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
const route = useRoute()
const {
  params: { id },
} = route as any
const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const emit = defineEmits(['refresh'])

const formRef = ref()

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const form = ref<any>({})
const isEdit = ref(false)
const detail = ref<any>({})

const rules = reactive<FormRules>({
  content: [
    { required: true, message: t('views.chatLog.form.content.placeholder'), trigger: 'blur' },
  ],
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {}
    isEdit.value = false
  }
})

function deleteMark() {
  loadSharedApi({ type: 'chatLog', systemType: apiType.value })
    .delMarkChatRecord(
      id as string,
      detail.value.chat_id,
      detail.value.id,
      form.value.knowledge,
      form.value.document,
      form.value.id,
      loading,
    )
    .then(() => {
      emit('refresh')
      MsgSuccess(t('common.deleteSuccess'))
      dialogVisible.value = false
    })
}

function getMark(data: any) {
  loadSharedApi({ type: 'chatLog', systemType: apiType.value })
    .getMarkChatRecord(id as string, data.chat_id, data.id, loading)
    .then((res: any) => {
      if (res.data.length > 0) {
        form.value = res.data[0]
      }
    })
}

const open = (data: any) => {
  detail.value = data
  getMark(data)
  dialogVisible.value = true
}
const submit = async (formEl: FormInstance) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      loadSharedApi({ type: 'paragraph', systemType: apiType.value })
        .putParagraph(
          form.value.knowledge,
          form.value.document,
          form.value.id,
          {
            content: form.value.content,
          },
          loading,
        )
        .then(() => {
          dialogVisible.value = false
        })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped>
.edit-mark-dialog {
  .el-dialog__header.show-close {
    padding-right: 15px;
  }

  .el-dialog__headerbtn {
    top: 13px;
  }
}
</style>
