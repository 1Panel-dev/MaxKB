<template>
  <el-dialog
    :title="$t('views.knowledge.knowledgeType.createWorkflowKnowledge')"
    v-model="dialogVisible"
    width="720"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <!-- 基本信息 -->
    <BaseForm ref="BaseFormRef" v-if="dialogVisible" :apiType="apiType" />

    <div class="w-full" v-if="dialogVisible">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-card
            class="template-radio-card cursor text-center flex-center"
            shadow="never"
            @click="selectedType('blank')"
            :class="appTemplate === 'blank' ? 'active' : ''"
          >
            <div class="flex-center p-24">
              <AppIcon iconName="app-add-outlined" class="mr-12"></AppIcon>
              {{ $t('views.knowledge.form.appTemplate.blank.title') }}
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <CardBox
            :title="$t('views.knowledge.form.appTemplate.basic.title')"
            :description="$t('views.knowledge.form.appTemplate.basic.description')"
            shadow="never"
            class="template-radio-card cursor"
            :class="appTemplate === 'basic' ? 'active' : ''"
            @click="selectedType('basic')"
          >
            <template #icon>
              <img src="@/assets/knowledge/icon_basic_template.svg" alt="" />
            </template>
          </CardBox>
        </el-col>
      </el-row>
    </div>

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
import { ref, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BaseForm from '@/views/knowledge/component/BaseForm.vue'
import { MsgSuccess, MsgAlert } from '@/utils/message'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { t } from '@/locales'
import useStore from '@/stores'
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
    loadSharedApi({ type: 'knowledge', systemType: apiType.value })
      .createWorkflowKnowledge(obj, loading)
      .then(async (res: any) => {
        await user.profile()
        return res
      })
      .then((res: any) => {
        MsgSuccess(t('common.createSuccess'))
        router.push({
          path: `/knowledge/${res.data.id}/${currentFolder.value.id || 'shared'}/4/document`,
        })
        emit('refresh')
      })
  } else {
    return false
  }
}

const appTemplate = ref('blank')
const workflowDefault = ref<any>({
  // edges: [],
  // nodes: baseNodes,
})
function selectedType(type: string) {
  appTemplate.value = type
  // workflowDefault.value = applicationTemplate[type]
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
