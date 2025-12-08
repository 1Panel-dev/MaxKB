<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-16">{{ $t('views.applicationWorkflow.nodeSetting') }}</h5>
    <h5 class="lighter mb-8">{{ $t('common.param.inputParam') }}</h5>
    <el-form
      @submit.prevent
      ref="ToolNodeFormRef"
      :model="chat_data"
      label-position="top"
      require-asterisk-position="right"
      hide-required-asterisk
    >
      <el-card shadow="never" class="card-never mb-16" style="--el-card-padding: 12px">
        <div v-if="chat_data.input_field_list?.length > 0">
          <template v-for="(item, index) in chat_data.input_field_list" :key="item.name">
            <el-form-item
              :label="item.name"
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
                      <auto-tooltip :content="item.name" style="max-width: 130px">
                        {{ item.name }}
                      </auto-tooltip>
                    </div>
                    <el-tooltip
                      v-if="item.desc"
                      effect="dark"
                      placement="right"
                      popper-class="max-w-200"
                    >
                      <template #content>
                        {{ item.desc }}
                      </template>
                      <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                    </el-tooltip>

                    <span class="color-danger" v-if="item.is_required">*</span>

                    <el-tag type="info" class="info-tag ml-4">{{ item.type }}</el-tag>
                  </div>
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
              <el-input
                v-else
                v-model="item.value"
                :placeholder="$t('views.tool.form.param.inputPlaceholder')"
              />
            </el-form-item>
          </template>
        </div>

        <el-text type="info" v-else> {{ $t('common.noData') }} </el-text>
      </el-card>
      <el-form-item
        :label="$t('views.applicationWorkflow.nodes.aiChatNode.returnContent.label')"
        @click.prevent
      >
        <template #label>
          <div class="flex align-center">
            <div class="mr-4">
              <span>{{
                $t('views.applicationWorkflow.nodes.aiChatNode.returnContent.label')
              }}</span>
            </div>
            <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
              <template #content>
                {{ $t('views.applicationWorkflow.nodes.aiChatNode.returnContent.tooltip') }}
              </template>
              <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
            </el-tooltip>
          </div>
        </template>
        <el-switch size="small" v-model="chat_data.is_result" />
      </el-form-item>
    </el-form>
  </NodeContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'
import { useRoute } from 'vue-router'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import { isLastNode } from '@/workflow/common/data'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const props = defineProps<{ nodeModel: any }>()

const route = useRoute()

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const nodeCascaderRef = ref()

const form = {
  input_field_list: [],
  is_result: false,
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
      const old_input_field_list = props.nodeModel.properties.node_data.input_field_list
      const merge_input_field_list = ok.data.input_field_list.map((item: any) => {
        const find_field = old_input_field_list.find((old_item: any) => old_item.name == item.name)
        if (find_field && find_field.source == item.source) {
          return { ...item, value: JSON.parse(JSON.stringify(find_field.value)) }
        }
        return { ...item, value: item.source == 'reference' ? [] : '' }
      })
      set(props.nodeModel.properties.node_data, 'input_field_list', merge_input_field_list)
      set(props.nodeModel.properties, 'status', ok.data.is_active ? 200 : 500)
    })
    .catch(() => {
      set(props.nodeModel.properties, 'status', 500)
    })
}

onMounted(() => {
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
