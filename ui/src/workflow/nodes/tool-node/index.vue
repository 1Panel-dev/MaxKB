<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-16">{{ $t('views.applicationWorkflow.nodeSetting') }}</h5>
    <div class="flex-between">
      <h5 class="lighter mb-8">{{ $t('common.param.inputParam') }}</h5>
      <el-button link type="primary" @click="openAddDialog()">
        <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon> {{ $t('common.add') }}
      </el-button>
    </div>
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
          <template v-for="(item, index) in chat_data.input_field_list" :key="index">
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
                    <el-tooltip v-if="item.desc" effect="dark" placement="right" popper-class="max-w-200">
                      <template #content>
                        {{ item.desc }}
                      </template>
                      <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                    </el-tooltip>

                    <span class="color-danger" v-if="item.is_required">*</span>

                    <el-tag type="info" class="info-tag ml-4">{{ item.type }}</el-tag>
                  </div>
                  <div>
                    <el-button text @click.stop="openAddDialog(item, index)">
                      <AppIcon iconName="app-edit"></AppIcon>
                    </el-button>
                    <el-button text @click="deleteField(index)" style="margin-left: 4px !important">
                      <AppIcon iconName="app-delete"></AppIcon>
                    </el-button>
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
                :width="100"
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

      <h5 class="lighter mb-8">
        {{ $t('views.tool.form.param.code') }}
      </h5>
      <div class="mb-8" v-if="showEditor">
        <CodemirrorEditor
          :title="$t('views.tool.form.param.code')"
          v-model="chat_data.code"
          @wheel="wheel"
          style="height: 130px !important"
          @submitDialog="submitCodemirrorEditor"
        />
      </div>

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
    <FieldFormDialog ref="FieldFormDialogRef" @refresh="refreshFieldList" />
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import FieldFormDialog from '@/views/tool/component/FieldFormDialog.vue'
import { isLastNode } from '@/workflow/common/data'

const props = defineProps<{ nodeModel: any }>()

const wheel = (e: any) => {
  if (e.ctrlKey === true) {
    e.preventDefault()
    return true
  } else {
    e.stopPropagation()
    return true
  }
}
const FieldFormDialogRef = ref()
const nodeCascaderRef = ref()

const form = {
  code: '',
  input_field_list: [],
  is_result: false,
}

const currentIndex = ref<any>(null)
const showEditor = ref(false)

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

function submitCodemirrorEditor(val: string) {
  set(props.nodeModel.properties.node_data, 'code', val)
}

function openAddDialog(data?: any, index?: any) {
  if (typeof index !== 'undefined') {
    currentIndex.value = index
  }

  FieldFormDialogRef.value.open(data)
}

function deleteField(index: any) {
  const list: any = cloneDeep(props.nodeModel.properties.node_data.input_field_list)
  list.splice(index, 1)
  set(props.nodeModel.properties.node_data, 'input_field_list', list)
}

function refreshFieldList(data: any) {
  const list = cloneDeep(props.nodeModel.properties.node_data.input_field_list)
  const obj = {
    ...data,
    value: data.source === 'reference' ? [] : '',
  }
  if (currentIndex.value !== null) {
    list.splice(currentIndex.value, 1, obj)
  } else {
    list.push(obj)
  }
  set(props.nodeModel.properties.node_data, 'input_field_list', list)
  currentIndex.value = null
}

onMounted(() => {
  if (typeof props.nodeModel.properties.node_data?.is_result === 'undefined') {
    if (isLastNode(props.nodeModel)) {
      set(props.nodeModel.properties.node_data, 'is_result', true)
    }
  }
  set(props.nodeModel, 'validate', validate)
  setTimeout(() => {
    showEditor.value = true
  }, 100)
})
</script>
<style lang="scss"></style>
