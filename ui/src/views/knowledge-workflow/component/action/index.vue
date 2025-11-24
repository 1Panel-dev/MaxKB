<template>
  <div style="height: 100%; width: 100%" v-loading="loading">
    <div style="height: calc(100% - 57px); overflow-y: auto; width: 100%">
      <keep-alive>
        <component
          ref="ActionRef"
          :is="ak[active]"
          v-model:loading="loading"
          :workflow="workflow"
          :knowledge_id="knowledge_id"
          :id="action_id"
        ></component>
      </keep-alive>
    </div>
    <div class="el-drawer__footer">
      <el-button
        v-if="base_form_list.length > 0 && active == 'knowledge_base'"
        :loading="loading"
        @click="up"
        >上一步</el-button
      >
      <el-button
        v-if="base_form_list.length > 0 && active == 'data_source'"
        :loading="loading"
        @click="next"
        >下一步</el-button
      >
      <el-button
        v-if="base_form_list.length > 0 ? active == 'knowledge_base' : true"
        @click="upload"
        type="primary"
        :loading="loading"
        >Upload
      </el-button>
    </div>
  </div>
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
  return applicationApi.postUploadFile(file, props.knowledge_id, 'KNOWLEDGE', loading)
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
const props = defineProps<{
  workflow: any
  knowledge_id: string
}>()
const base_form_list = computed(() => {
  const kBase = props.workflow?.nodes?.find((n: any) => n.type === WorkflowType.KnowledgeBase)
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
    KnowledgeApi.workflowAction(props.knowledge_id, form_data.value, loading).then((ok) => {
      action_id.value = ok.data.id
      active.value = 'result'
    })
  })
}
</script>
<style lang="scss" scoped></style>
