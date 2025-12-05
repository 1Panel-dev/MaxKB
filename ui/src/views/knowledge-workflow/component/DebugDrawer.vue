<template>
  <el-drawer
    v-model="drawerVisible"
    :title="$t('common.debug')"
    size="800px"
    direction="rtl"
    destroy-on-close
    :before-close="close"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div style="height: calc(100% - 57px)" v-loading="loading">
      <keep-alive :key="key" :include="['DataSource', 'KnowledgeBase']">
        <component
          ref="ActionRef"
          :is="ak[active]"
          v-model:loading="loading"
          :workflow="_workflow"
          :knowledge_id="id"
          :id="action_id"
        ></component>
      </keep-alive>
    </div>
    <template #footer>
      <el-button v-if="active == 'result'" @click="continueImporting">
        {{ $t('views.document.buttons.continueImporting') }}
      </el-button>
      <el-button
        v-if="base_form_list.length > 0 && active == 'knowledge_base'"
        :loading="loading"
        @click="up"
      >
        {{ $t('common.steps.prev') }}</el-button
      >
      <el-button
        v-if="base_form_list.length > 0 && active == 'data_source'"
        :loading="loading"
        @click="next"
      >
        {{ $t('common.steps.next') }}
      </el-button>
      <el-button
        v-if="base_form_list.length > 0 ? active == 'knowledge_base' : active == 'data_source'"
        @click="upload"
        type="primary"
        :loading="loading"
      >
        {{ $t('views.document.buttons.import') }}
      </el-button>
      <el-button v-if="active == 'result'" type="primary" @click="goDocument">{{
        $t('views.knowledge.ResultSuccess.buttons.toDocument')
      }}</el-button>
    </template>
  </el-drawer>
</template>
<script setup lang="ts">
import { computed, ref, provide, type Ref, nextTick } from 'vue'
import DataSource from '@/views/knowledge-workflow/component/action/DataSource.vue'
import Result from '@/views/knowledge-workflow/component/action/Result.vue'
import applicationApi from '@/api/application/application'
import KnowledgeBase from '@/views/knowledge-workflow/component/action/KnowledgeBase.vue'
import { WorkflowType } from '@/enums/application'

import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import permissionMap from '@/permission'
import { MsgError } from '@/utils/message'
import { t } from '@/locales'
import { useRoute, useRouter } from 'vue-router'
provide('upload', (file: any, loading?: Ref<boolean>) => {
  return applicationApi.postUploadFile(file, id, 'KNOWLEDGE', loading)
})
const key = ref<number>(0)
const router = useRouter()
const route = useRoute()
const {
  params: { id, folderId },
  /*
  id 为 knowledge_id
  */
} = route as any
const ak = {
  data_source: DataSource,
  knowledge_base: KnowledgeBase,
  result: Result,
}
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const loading = ref<boolean>(false)
const action_id = ref<string>()
const ActionRef = ref()
const form_data = ref<any>({})
const active = ref<'data_source' | 'knowledge_base' | 'result'>('data_source')
const drawerVisible = ref<boolean>(false)
const _workflow = ref<any>(null)
const close = () => {
  drawerVisible.value = false
  _workflow.value = null
  active.value = 'data_source'
}
const open = (workflow: any) => {
  drawerVisible.value = true
  _workflow.value = workflow
}

const base_form_list = computed(() => {
  const kBase = _workflow.value?.nodes?.find((n: any) => n.type === WorkflowType.KnowledgeBase)
  if (kBase) {
    return kBase.properties.user_input_field_list
  }
  return []
})
const next = () => {
  ActionRef.value.validate().then(() => {
    form_data.value[active.value] = ActionRef.value.get_data()
    active.value = 'knowledge_base'
  })
}
const up = () => {
  ActionRef.value.validate().then(() => {
    active.value = 'data_source'
  })
}

const permissionPrecise = computed(() => {
  return permissionMap['knowledge'][apiType.value]
})

const upload = () => {
  if (permissionPrecise.value.doc_create(id)) {
    ActionRef.value.validate().then(() => {
      form_data.value[active.value] = ActionRef.value.get_data()
      loadSharedApi({ type: 'knowledge', systemType: apiType.value })
        .workflowAction(id, form_data.value, loading)
        .then((ok: any) => {
          action_id.value = ok.data.id
          active.value = 'result'
        })
    })
  } else {
    MsgError(t('views.application.tip.noDocPermission'))
  }
}
const continueImporting = () => {
  active.value = 'data_source'
  key.value++
  action_id.value = undefined
  const c_workflow = _workflow.value
  _workflow.value = null
  form_data.value = {}
  nextTick(() => {
    _workflow.value = c_workflow
  })
}
const goDocument = () => {
  const newUrl = router.resolve({
    path: `/knowledge/${id}/${folderId}/4/document`,
  }).href
  window.open(newUrl)
}
defineExpose({ close, open })
</script>
<style lang="scss" scoped></style>
