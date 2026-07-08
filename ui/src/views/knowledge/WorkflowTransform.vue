<template>
  <div class="p-16-24">
    <el-card style="height: calc(var(--app-main-height) + 50px)">
      <div class="flex-center h-full">
        <div style="margin-left: 20px">
          <h1 class="mb-12">{{ $t('views.knowledge.transform.title') }}</h1>
          <div class="color-secondary lighter line-height-22">
            {{ $t('views.knowledge.transform.message1') }}<br />{{
              $t('views.knowledge.transform.message2')
            }}
          </div>
          <p class="mt-24 mb-8 color-organe">{{ $t('views.knowledge.transform.tip') }}</p>
          <el-button type="primary" @click="transformHandle">{{
            $t('views.knowledge.transform.button')
          }}</el-button>
        </div>
        <img class="ml-24" src="@/assets/workflow-demo.png" width="708" alt="" />
      </div>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import { t } from '@/locales'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
import { useRoute, useRouter } from 'vue-router'
import { knowledgeTemplate } from '@/workflow/common/template.ts'
const route = useRoute()
const {
  params: { id, folderId },
} = route as any

const router = useRouter()
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const workflowDefault = ref(knowledgeTemplate.default)

const loading = ref(false)
function transformHandle() {
  MsgConfirm(t('common.tip'), t('views.knowledge.transform.comfirm'), {
    cancelButtonText: t('common.close'),
    type: 'warning',
  })
    .then(() => {
      loadSharedApi({ type: 'knowledge', systemType: apiType.value })
        .postTransformWorkflow(id as string, { work_flow: workflowDefault.value }, loading)
        .then(() => {
          MsgSuccess(t('common.submitSuccess'))
          router.push({ path: `/knowledge/${id}/${folderId}/workflow` })
        })
        .catch(() => {
          loading.value = false
        })
    })
    .catch(() => {})
}

onMounted(() => {})
</script>
<style lang="scss" scoped></style>
