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
    <el-form
      ref="KnowledgeFormRef"
      :rules="rules"
      :model="knowledgeForm"
      label-position="top"
      require-asterisk-position="right"
    >
      <el-form-item :label="$t('views.knowledge.form.source_url.label')" prop="source_url">
        <el-input
          v-model="knowledgeForm.source_url"
          :placeholder="$t('views.knowledge.form.source_url.placeholder')"
          @blur="knowledgeForm.source_url = knowledgeForm.source_url.trim()"
        />
      </el-form-item>
      <el-form-item :label="$t('views.knowledge.form.selector.label')">
        <el-input
          v-model="knowledgeForm.selector"
          :placeholder="$t('views.knowledge.form.selector.placeholder')"
          @blur="knowledgeForm.selector = knowledgeForm.selector.trim()"
        />
      </el-form-item>
    </el-form>
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
import BaseForm from '@/views/shared/knowledge-shared/component/BaseForm.vue'
import KnowledgeApi from '@/api/system-shared/knowledge'
import { MsgSuccess, MsgAlert } from '@/utils/message'
import { t } from '@/locales'
const emit = defineEmits(['refresh'])

const router = useRouter()
const BaseFormRef = ref()
const KnowledgeFormRef = ref()

const loading = ref(false)
const dialogVisible = ref<boolean>(false)

const knowledgeForm = ref<any>({
  source_url: '',
  selector: '',
})

const rules = reactive({
  source_url: [
    {
      required: true,
      message: t('views.knowledge.form.source_url.requiredMessage'),
      trigger: 'blur',
    },
  ],
})

const currentFolder = ref<any>(null)

watch(dialogVisible, (bool) => {
  if (!bool) {
    currentFolder.value = null
    knowledgeForm.value = {
      source_url: '',
      selector: '',
    }
    KnowledgeFormRef.value?.clearValidate()
  }
})

const open = (folder: string) => {
  currentFolder.value = folder
  dialogVisible.value = true
}

const submitHandle = async () => {
  if (await BaseFormRef.value?.validate()) {
    await KnowledgeFormRef.value.validate((valid: any) => {
      if (valid) {
        const obj = {
          folder_id: currentFolder.value?.id,
          ...BaseFormRef.value.form,
          ...knowledgeForm.value,
        }
        KnowledgeApi.postWebKnowledge(obj, loading).then((res) => {
          MsgSuccess(t('common.createSuccess'))
          router.push({
            path: `/knowledge/system/${res.data.id}/documentShared`,
          })
          emit('refresh')
        })
      } else {
        return false
      }
    })
  } else {
    return false
  }
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
