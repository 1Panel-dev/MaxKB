<template>
  <el-dialog
    :title="$t('views.knowledge.knowledgeType.createGeneralKnowledge')"
    v-model="dialogVisible"
    width="720"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <!-- 基本信息 -->
    <BaseForm ref="BaseFormRef" v-if="dialogVisible" />

    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false" :loading="loading">
          {{ $t('common.cancel') }}
        </el-button>
        <el-button type="primary" @click="submitHandle" :loading="loading">
          {{ $t('common.create') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BaseForm from '@/views/knowledge/component/BaseForm.vue'
import KnowledgeApi from '@/api/knowledge/knowledge'
import { MsgSuccess, MsgAlert } from '@/utils/message'
import { t } from '@/locales'
const emit = defineEmits(['refresh'])

const router = useRouter()
const BaseFormRef = ref()

const loading = ref(false)
const dialogVisible = ref<boolean>(false)
const currentFolder = ref<any>(null)

watch(dialogVisible, (bool) => {
  if (!bool) {
    currentFolder.value = null
  }
})

const open = (folder: string) => {
  currentFolder.value = folder
  dialogVisible.value = true
}

const submitHandle = async () => {
  if (await BaseFormRef.value?.validate()) {
    const obj = {
      folder_id: currentFolder.value?.id,
      ...BaseFormRef.value.form,
    }
    KnowledgeApi.postDataset('default', obj, loading).then((res) => {
      MsgSuccess(t('common.createSuccess'))
      // router.push({ path: `/knowledge/${res.data.id}/document` })
      emit('refresh')
    })
  } else {
    return false
  }
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
