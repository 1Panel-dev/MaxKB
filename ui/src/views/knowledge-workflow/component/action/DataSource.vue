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
      <h4 class="title-decoration-1 mb-16 mt-4">
        {{ $t('views.tool.dataSource.selectDataSource') }}
      </h4>
      <el-form-item
        :label="$t('views.tool.dataSource.title')"
        prop="node_id"
        :rules="base_form_data_rule.node_id"
      >
        <el-row class="w-full" :gutter="8">
          <el-col :span="8" v-for="node in source_node_list" :key="node.id">
            <el-card
              shadow="never"
              class="card-checkbox cursor w-full mb-8"
              :class="base_form_data.node_id === node.id ? 'active' : ''"
              style="--el-card-padding: 4px 12px"
              @click="sourceChange(node.id)"
            >
              <div class="flex align-center">
                <component
                  :is="iconComponent(`${node.type}-icon`)"
                  class="mr-8"
                  :size="20"
                  :item="node?.properties.node_data"
                />
                {{ node.properties.stepName }}
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-form-item>
    </template>
  </DynamicsForm>
</template>
<script setup lang="ts">
import { computed, ref, watch, provide } from 'vue'
import { WorkflowKind, WorkflowType } from '@/enums/application'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import type { FormField } from '@/components/dynamics-form/type'
import { iconComponent } from '@/workflow/icons/utils'
import type { Dict } from '@/api/type/common'
import type { FormRules } from 'element-plus'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { useRoute } from 'vue-router'
import { t } from '@/locales'
import useStore from '@/stores'
const { user } = useStore()
const route = useRoute()

const props = defineProps<{
  workflow: any
  knowledge_id: string
  loading: boolean
}>()

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const model_form_field = ref<Array<FormField>>([])

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
const extra = ref<any>({
  current_tool_id: undefined,
})
const get_extra = () => {
  return extra.value
}
provide('get_extra', get_extra)

const sourceChange = (node_id: string) => {
  base_form_data.value.node_id = node_id
  const n = source_node_list.value.find((n: any) => n.id == node_id)
  if (n.properties.node_data && n.properties.node_data.tool_lib_id) {
    extra.value.current_tool_id = n.properties.node_data.tool_lib_id
  }
  node_id = n
    ? [WorkflowType.DataSourceLocalNode, WorkflowType.DataSourceWebNode].includes(n.type)
      ? n.type
      : n.properties.node_data.tool_lib_id
    : node_id
  loadSharedApi({ type: 'knowledge', systemType: apiType.value })
    .getKnowledgeWorkflowFormList(
      props.knowledge_id,
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
    message: t('views.tool.dataSource.requiredMessage'),
  },
})
const validate = () => {
  return dynamicsFormRef.value?.validate()
}
const get_data = () => {
  return form_data.value
}
watch(
  source_node_list,
  () => {
    if (!base_form_data.value.node_id) {
      if (source_node_list.value && source_node_list.value.length > 0) {
        sourceChange(source_node_list.value[0].id)
      }
    }
  },
  { immediate: true },
)

defineExpose({ validate, get_data })
</script>
<style lang="scss" scoped></style>
