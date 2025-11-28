<template>
  <el-drawer
    v-model="drawerVisible"
    :title="$t('common.debug')"
    size="800px"
    direction="rtl"
    destroy-on-close
    :before-close="close"
  >
    <div style="height: calc(100% - 57px)" v-loading="loading">
      <keep-alive>
        <component
          ref="ActionRef"
          :is="ak[active]"
          v-model:loading="loading"
          :workflow="_workflow"
          :knowledge_id="_knowledge_id"
          :id="action_id"
        ></component>
      </keep-alive>
    </div>
    <template #footer>
      <el-button :loading="loading" @click="close">{{ $t('common.cancel') }}</el-button>
      <el-button
        v-if="base_form_list.length > 0 && active == 'knowledge_base'"
        :loading="loading"
        @click="up"
      >
        {{ $t('views.document.buttons.prev') }}</el-button
      >
      <el-button
        v-if="base_form_list.length > 0 && active == 'data_source'"
        :loading="loading"
        @click="next"
      >
        {{ $t('views.document.buttons.next') }}
      </el-button>
      <el-button
        v-if="base_form_list.length > 0 ? active == 'knowledge_base' : true"
        @click="upload"
        type="primary"
        :loading="loading"
      >
        {{ $t('views.document.buttons.import') }}
      </el-button>
    </template>
  </el-drawer>
</template>
<script setup lang="ts">
import { computed, ref, provide, type Ref } from 'vue'
import DataSource from '@/views/knowledge-workflow/component/action/DataSource.vue'
import Result from '@/views/knowledge-workflow/component/action/Result.vue'
import applicationApi from '@/api/application/application'
import KnowledgeBase from '@/views/knowledge-workflow/component/action/KnowledgeBase.vue'
import { WorkflowType } from '@/enums/application'
import KnowledgeApi from '@/api/knowledge/knowledge'
provide('upload', (file: any, loading?: Ref<boolean>) => {
  return applicationApi.postUploadFile(file, _knowledge_id.value, 'KNOWLEDGE', loading)
})
const ak = {
  data_source: DataSource,
  knowledge_base: KnowledgeBase,
  result: Result,
}
const loading = ref<boolean>(false)
const action_id = ref<string>()
const ActionRef = ref()
const form_data = ref<any>({})
const active = ref<'data_source' | 'knowledge_base' | 'result'>('data_source')
const drawerVisible = ref<boolean>(false)
const _workflow = ref<any>(null)
const _knowledge_id = ref<string>('')
const close = () => {
  drawerVisible.value = false
  _workflow.value = null
  _knowledge_id.value = ''
  active.value = 'data_source'
}
const open = (workflow: any, knowledge_id: string) => {
  drawerVisible.value = true
  _workflow.value = workflow
  _knowledge_id.value = knowledge_id
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
const upload = () => {
  ActionRef.value.validate().then(() => {
    form_data.value[active.value] = ActionRef.value.get_data()
    KnowledgeApi.workflowAction(_knowledge_id.value, form_data.value, loading).then((ok) => {
      action_id.value = ok.data.id
      active.value = 'result'
    })
  })
}
defineExpose({ close, open })
</script>
<style lang="scss" scoped></style>
