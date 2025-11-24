<template>
  <DynamicsForm
    v-model="form_data"
    :render_data="model_form_field"
    :model="form_data"
    ref="dynamicsFormRef"
    label-position="top"
    require-asterisk-position="right"
    :other-params="{ current_workspace_id: workspace_id, current_knowledge_id: knowledge_id }"
  >
    <template #default>
      <el-form-item prop="node_id" :rules="base_form_data_rule.node_id">
        <el-radio-group @change="sourceChange" v-model="base_form_data.node_id">
          <el-radio :value="node.id" border size="large" v-for="node in source_node_list">
            <div style="display: flex; align-items: center">
              <component
                :is="iconComponent(`${node.type}-icon`)"
                class="mr-8"
                :size="24"
                :item="node?.properties.node_data"
              />
              {{ node.properties.stepName }}
            </div>
          </el-radio>
        </el-radio-group>
      </el-form-item>
    </template>
  </DynamicsForm>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { WorkflowKind, WorkflowType } from '@/enums/application'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import type { FormField } from '@/components/dynamics-form/type'
import { iconComponent } from '@/workflow/icons/utils'
import type { Dict } from '@/api/type/common'
import type { FormRules } from 'element-plus'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { useRoute } from 'vue-router'
import useStore from '@/stores'
const { user } = useStore()
const route = useRoute()

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const model_form_field = ref<Array<FormField>>([])
const props = defineProps<{
  workflow: any
  knowledge_id: string
  loading: boolean
}>()
const workspace_id = computed(() => {
  return user.getWorkspaceId()
})
const emit = defineEmits(['update:loading'])
const _loading = computed({
  get: () => {
    return props.loading
  },
  set: (v: boolean) => {
    emit('update:loading', v)
  },
})
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const base_form_data = ref<{ node_id: string }>({ node_id: '' })
const dynamics_form_data = ref<Dict<any>>({})
const form_data = computed({
  get: () => {
    return { ...dynamics_form_data.value, ...base_form_data.value }
  },
  set: (event: any) => {
    dynamics_form_data.value = event
  },
})
const source_node_list = computed(() => {
  return props.workflow?.nodes?.filter((n: any) => n.properties.kind === WorkflowKind.DataSource)
})
const {
  params: { id, from },
} = route as any
const sourceChange = (node_id: string) => {
  const n = source_node_list.value.find((n: any) => n.id == node_id)
  node_id = n
    ? [WorkflowType.DataSourceLocalNode, WorkflowType.DataSourceWebNode].includes(n.type)
      ? n.type
      : n.properties.node_data.tool_lib_id
    : node_id
  loadSharedApi({ type: 'knowledge', systemType: apiType.value })
    .getKnowledgeWorkflowFormList(
      id,
      [WorkflowType.DataSourceLocalNode, WorkflowType.DataSourceWebNode].includes(n.type)
        ? 'local'
        : 'tool',
      node_id,
      n,
      _loading,
    )
    .then((ok: any) => {
      dynamicsFormRef.value?.render(ok.data)
    })
}
const base_form_data_rule = ref<FormRules>({
  node_id: {
    required: true,
    trigger: 'blur',
    message: '数据源必选',
  },
})
const validate = () => {
  return dynamicsFormRef.value?.validate()
}
const get_data = () => {
  return form_data.value
}
defineExpose({ validate, get_data })
</script>
<style lang="scss" scoped></style>
