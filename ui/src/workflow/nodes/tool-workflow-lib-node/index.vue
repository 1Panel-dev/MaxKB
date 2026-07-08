<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-form
      @submit.prevent
      ref="ToolNodeFormRef"
      :model="chat_data"
      label-position="top"
      require-asterisk-position="right"
      hide-required-asterisk
    >
      <h5 class="title-decoration-1 mb-8">{{ chat_data.input_title }}</h5>

      <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
        <div v-if="chat_data.input_field_list?.length">
          <template v-for="(item, index) in chat_data.input_field_list" :key="item.field">
            <el-form-item
              :label="item.label"
              :prop="'input_field_list.' + index + '.value'"
              :rules="{
                required: item.is_required,
                message:
                  item.source === 'reference'
                    ? $t('views.tool.form.param.selectPlaceholder')
                    : $t('views.tool.form.param.inputPlaceholder'),
                trigger: 'blur',
              }"
            >
              <template #label>
                <div class="flex-between">
                  <div class="flex align-center">
                    <div class="mr-4">
                      <auto-tooltip :content="item.label" style="max-width: 130px">
                        {{ item.label }}
                      </auto-tooltip>
                    </div>
                    <span class="color-danger" v-if="item.is_required">*</span>
                  </div>
                  <el-select
                    :teleported="false"
                    v-model="item.source"
                    @change="onSourceChange(item)"
                    size="small"
                    style="width: 85px"
                  >
                    <el-option :label="$t('workflow.variable.Referencing')" value="reference" />
                    <el-option :label="$t('common.custom')" value="custom" />
                  </el-select>
                </div>
              </template>
              <NodeCascader
                v-if="item.source === 'reference'"
                ref="nodeCascaderRef"
                :nodeModel="nodeModel"
                class="w-full"
                :placeholder="$t('views.tool.form.param.selectPlaceholder')"
                v-model="item.value"
              />
              <template v-else>
                <el-input
                  v-if="['string'].includes(item.type)"
                  v-model="item.value"
                  :placeholder="$t('views.tool.form.param.inputPlaceholder')"
                />
                <JsonInput v-if="['array', 'dict'].includes(item.type)" v-model="item.value" />
                <el-input-number v-if="['int', 'float'].includes(item.type)" v-model="item.value" />
                <el-switch
                  v-if="['boolean'].includes(item.type)"
                  v-model="item.value"
                  :active-value="true"
                  :inactive-value="false"
                />
              </template>
            </el-form-item>
          </template>
        </div>

        <el-text type="info" v-else> {{ $t('common.noData') }} </el-text>
      </el-card>
    </el-form>
  </NodeContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'
import { useRoute } from 'vue-router'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import JsonInput from '@/components/dynamics-form/items/JsonInput.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted, inject } from 'vue'
import { isLastNode } from '@/workflow/common/data'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const props = defineProps<{ nodeModel: any }>()

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

const onSourceChange = (item: any) => {
  if (item.type === 'boolean') {
    item.value = false
  } else if (['array', 'dict'].includes(item.type)) {
    item.value = []
  } else {
    item.value = ''
  }
}

const form = {
  input_field_list: [],
  is_result: false,
  source: 'custom',
}

const chat_data = computed({
  get: () => {
    if (props.nodeModel.properties.node_data) {
      return props.nodeModel.properties.node_data
    } else {
      set(props.nodeModel.properties, 'node_data', form)
    }
    return props.nodeModel.properties.node_data
  },
  set: (value) => {
    set(props.nodeModel.properties, 'node_data', value)
  },
})

const ToolNodeFormRef = ref<FormInstance>()

const validate = () => {
  return ToolNodeFormRef.value?.validate().catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

const update_field = () => {
  if (!props.nodeModel.properties.node_data.tool_lib_id) {
    set(props.nodeModel.properties, 'status', 500)
    return
  }
  loadSharedApi({ type: 'tool', systemType: apiType.value })
    .getToolById(props.nodeModel.properties.node_data.tool_lib_id)
    .then((ok: any) => {
      const workflowNodes = ok.data?.work_flow?.nodes || []
      const baseNode = workflowNodes.find((n: any) => n.type === 'tool-base-node')

      if (baseNode) {
        const new_input_list = baseNode.properties.user_input_field_list || []
        const new_output_list = baseNode.properties.user_output_field_list || []

        const old_config_fields = props.nodeModel.properties.config?.fields || []
        const config_field_list = new_output_list.map((item: any) => {
          const old = old_config_fields.find((o: any) => o.value === item.field)
          return old ? JSON.parse(JSON.stringify(old)) : { label: item.label, value: item.field }
        })

        const input_title = baseNode.properties.user_input_config?.title
        const output_title = baseNode.properties.user_output_config?.title
        const old_input_list = props.nodeModel.properties.node_data.input_field_list || []
        const merged_input_list = new_input_list.map((item: any) => {
          const find_field = old_input_list.find((old_item: any) => old_item.field === item.field)

          if (find_field) {
            return {
              ...item,
              source: find_field.source,
              value: JSON.parse(JSON.stringify(find_field.value)),
            }
          }
          return { ...item, source: 'custom', value: '' }
        })

        set(props.nodeModel.properties.node_data, 'input_field_list', merged_input_list)
        set(props.nodeModel.properties, 'config', {
          fields: config_field_list,
          output_title: output_title,
        })
        set(props.nodeModel.properties.node_data, 'input_title', input_title)
      }
      set(props.nodeModel.properties, 'status', ok.data.is_active ? 200 : 500)
      props.nodeModel.clear_next_node_field(true)
    })
    .catch(() => {
      set(props.nodeModel.properties, 'status', 500)
    })
}

onMounted(() => {
  if (props.nodeModel.properties.config?.fields?.length) {
    set(props.nodeModel.properties.config, 'fields', props.nodeModel.properties.config.fields)
  }
  if (typeof props.nodeModel.properties.node_data?.is_result === 'undefined') {
    if (isLastNode(props.nodeModel)) {
      set(props.nodeModel.properties.node_data, 'is_result', true)
    }
  }
  update_field()
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
