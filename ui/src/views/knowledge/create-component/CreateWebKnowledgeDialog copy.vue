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
      ref="DatasetFormRef"
      :rules="rules"
      :model="datasetForm"
      label-position="top"
      require-asterisk-position="right"
    >

      <el-form-item
        :label="$t('views.knowledge.form.source_url.label')"
        prop="source_url"
        v-if="datasetForm.type === '1'"
      >
        <el-input
          v-model="datasetForm.source_url"
          :placeholder="$t('views.knowledge.form.source_url.placeholder')"
          @blur="datasetForm.source_url = datasetForm.source_url.trim()"
        />
      </el-form-item>
      <el-form-item
        :label="$t('views.knowledge.form.selector.label')"
        v-if="datasetForm.type === '1'"
      >
        <el-input
          v-model="datasetForm.selector"
          :placeholder="$t('views.knowledge.form.selector.placeholder')"
          @blur="datasetForm.selector = datasetForm.selector.trim()"
        />
      </el-form-item>
      <el-form-item label="App ID" prop="app_id" v-if="datasetForm.type === '2'">
        <el-input
          v-model="datasetForm.app_id"
          :placeholder="$t('views.application.applicationAccess.larkSetting.appIdPlaceholder')"
        />
      </el-form-item>
      <el-form-item label="App Secret" prop="app_secret" v-if="datasetForm.type === '2'">
        <el-input
          v-model="datasetForm.app_secret"
          type="password"
          show-password
          :placeholder="$t('views.application.applicationAccess.larkSetting.appSecretPlaceholder')"
        />
      </el-form-item>
      <el-form-item label="Folder Token" prop="folder_token" v-if="datasetForm.type === '2'">
        <el-input
          v-model="datasetForm.folder_token"
          :placeholder="
            $t('views.application.applicationAccess.larkSetting.folderTokenPlaceholder')
          "
        />
      </el-form-item>
      <el-form-item label="User ID" prop="user_id" v-if="datasetForm.type === '3'">
        <el-input
          v-model="datasetForm.user_id"
          :placeholder="
            $t('views.application.applicationAccess.larkSetting.folderTokenPlaceholder')
          "
        />
      </el-form-item>
      <el-form-item label="Token" prop="token" v-if="datasetForm.type === '3'">
        <el-input
          v-model="datasetForm.token"
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
import { ref, watch, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BaseForm from '@/views/knowledge/component/BaseForm.vue'
import KnowledgeApi from '@/api/knowledge/knowledge'
import { MsgSuccess, MsgAlert } from '@/utils/message'
import { t } from '@/locales'
import { ComplexPermission } from '@/utils/permission/type'
const emit = defineEmits(['refresh'])

const router = useRouter()
const BaseFormRef = ref()
const DatasetFormRef = ref()

const loading = ref(false)
const dialogVisible = ref<boolean>(false)

const datasetForm = ref<any>({
  type: '0',
  source_url: '',
  selector: '',
  app_id: '',
  app_secret: '',
  folder_token: ''
})

const rules = reactive({
  source_url: [
    {
      required: true,
      message: t('views.knowledge.form.source_url.requiredMessage'),
      trigger: 'blur'
    }
  ],
  app_id: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.appIdPlaceholder'),
      trigger: 'blur'
    }
  ],
  app_secret: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.appSecretPlaceholder'),
      trigger: 'blur'
    }
  ],
  folder_token: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.folderTokenPlaceholder'),
      trigger: 'blur'
    }
  ],
  user_id: [
    {
      required: true,
      message: t('views.knowledge.form.user_id.requiredMessage'),
      trigger: 'blur'
    }
  ],
  token: [
    {
      required: true,
      message: t('views.knowledge.form.token.requiredMessage'),
      trigger: 'blur'
    }
  ]
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    datasetForm.value = {
      type: '0',
      source_url: '',
      selector: ''
    }
    DatasetFormRef.value?.clearValidate()
  }
})

const open = () => {
  dialogVisible.value = true
}

const submitHandle = async () => {
  if (await BaseFormRef.value?.validate()) {
    await DatasetFormRef.value.validate((valid: any) => {
      if (valid) {
        if (datasetForm.value.type === '0') {
          const obj = {
            ...BaseFormRef.value.form,
            type: datasetForm.value.type
          }
          knowledgeApi.postDataset(obj, loading).then((res) => {
            MsgSuccess(t('common.createSuccess'))
            router.push({ path: `/knowledge/${res.data.id}/document` })
            emit('refresh')
          })
        } else if (datasetForm.value.type === '1') {
          const obj = { ...BaseFormRef.value.form, ...datasetForm.value }
          knowledgeApi.postWebDataset(obj, loading).then((res) => {
            MsgSuccess(t('common.createSuccess'))
            router.push({ path: `/knowledge/${res.data.id}/document` })
            emit('refresh')
          })
        } else if (datasetForm.value.type === '2') {
          const obj = { ...BaseFormRef.value.form, ...datasetForm.value }
          knowledgeApi.postLarkDataset(obj, loading).then((res) => {
            MsgSuccess(t('common.createSuccess'))
            router.push({ path: `/knowledge/${res.data.id}/document` })
            emit('refresh')
          })
        }
      } else {
        return false
      }
    })
  } else {
    return false
  }
}
function radioChange() {
  datasetForm.value.source_url = ''
  datasetForm.value.selector = ''
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
