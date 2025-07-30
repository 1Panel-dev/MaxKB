<template>
  <el-dialog
    :title="$t('views.knowledge.knowledgeType.createWebKnowledge')"
    v-model="dialogVisible"
    width="720"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <!-- 基本信息 -->
    <BaseForm ref="BaseFormRef" v-if="dialogVisible" :apiType="apiType" />
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
import { ref, watch, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BaseForm from '@/views/knowledge/component/BaseForm.vue'
import { MsgSuccess, MsgAlert } from '@/utils/message'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { t } from '@/locales'
import useStore from "@/stores";
const emit = defineEmits(['refresh'])

const { user } = useStore()
const router = useRouter()
const route = useRoute()
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
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
        loadSharedApi({ type: 'knowledge', systemType: apiType.value })
          .postWebKnowledge(obj, loading)
          .then(async (res: any) => {
            await user.profile();
            return res
          })
          .then((res: any) => {
            MsgSuccess(t('common.createSuccess'))
            router.push({
              path: `/knowledge/${res.data.id}/${currentFolder.value.id || 'shared'}/document`,
              query: {
                from: apiType.value,
              },
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
