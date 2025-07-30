<template>
  <el-dialog
    :title="$t('views.knowledge.knowledgeType.createLarkKnowledge')"
    v-model="dialogVisible"
    width="720"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <!-- 基本信息 -->
    <BaseForm ref="BaseFormRef" v-if="dialogVisible" :apiType="apiType" />
    <el-form
      ref="knowledgeFormRef"
      :rules="rules"
      :model="knowledgeForm"
      label-position="top"
      require-asterisk-position="right"
    >
      <el-form-item label="App ID" prop="app_id">
        <el-input
          v-model="knowledgeForm.app_id"
          :placeholder="$t('views.application.applicationAccess.larkSetting.appIdPlaceholder')"
        />
      </el-form-item>
      <el-form-item label="App Secret" prop="app_secret">
        <el-input
          v-model="knowledgeForm.app_secret"
          type="password"
          show-password
          :placeholder="$t('views.application.applicationAccess.larkSetting.appSecretPlaceholder')"
        />
      </el-form-item>
      <el-form-item label="Folder Token" prop="folder_token">
        <el-input
          v-model="knowledgeForm.folder_token"
          :placeholder="
            $t('views.application.applicationAccess.larkSetting.folderTokenPlaceholder')
          "
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
import { t } from '@/locales'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
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
const knowledgeFormRef = ref()

const loading = ref(false)
const dialogVisible = ref<boolean>(false)
const currentFolder = ref<any>(null)

const knowledgeForm = ref<any>({
  type: '0',
  source_url: '',
  selector: '',
  app_id: '',
  app_secret: '',
  folder_token: '',
})

const rules = reactive({
  source_url: [
    {
      required: true,
      message: t('views.knowledge.form.source_url.requiredMessage'),
      trigger: 'blur',
    },
  ],
  app_id: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.appIdPlaceholder'),
      trigger: 'blur',
    },
  ],
  app_secret: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.appSecretPlaceholder'),
      trigger: 'blur',
    },
  ],
  folder_token: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.folderTokenPlaceholder'),
      trigger: 'blur',
    },
  ],
  user_id: [
    {
      required: true,
      message: t('views.knowledge.form.user_id.requiredMessage'),
      trigger: 'blur',
    },
  ],
  token: [
    {
      required: true,
      message: t('views.knowledge.form.token.requiredMessage'),
      trigger: 'blur',
    },
  ],
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    knowledgeForm.value = {
      type: '0',
      source_url: '',
      selector: '',
    }
    knowledgeFormRef.value?.clearValidate()
  }
})

const open = (folder: string) => {
  currentFolder.value = folder
  dialogVisible.value = true
}

const submitHandle = async () => {
  if (await BaseFormRef.value?.validate()) {
    await knowledgeFormRef.value.validate((valid: any) => {
      if (valid) {
        const obj = {
          folder_id: currentFolder.value?.id,
          ...BaseFormRef.value.form,
          ...knowledgeForm.value,
        }
        loadSharedApi({ type: 'knowledge', systemType: apiType.value })
          .postLarkKnowledge(obj, loading)
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
