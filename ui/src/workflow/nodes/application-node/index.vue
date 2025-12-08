<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.applicationWorkflow.nodeSetting') }}</h5>
    <el-card shadow="never" class="card-never">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="applicationNodeFormRef"
      >
        <el-form-item
          :label="$t('views.applicationWorkflow.nodes.startNode.question')"
          prop="question_reference_address"
          :rules="{
            message: $t(
              'views.applicationWorkflow.nodes.searchKnowledgeNode.searchQuestion.requiredMessage',
            ),
            trigger: 'blur',
            required: true,
          }"
        >
          <NodeCascader
            ref="applicationNodeFormRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="
              $t('views.applicationWorkflow.nodes.searchKnowledgeNode.searchQuestion.placeholder')
            "
            v-model="form_data.question_reference_address"
          />
        </el-form-item>

        <el-form-item
          v-if="form_data.hasOwnProperty('document_list') || 'document_list' in form_data"
          :label="$t('views.problem.relateParagraph.selectDocument')"
          prop="document_list"
          :rules="{
            message: $t('views.chatLog.documentPlaceholder'),
            trigger: 'blur',
            required: false,
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="$t('views.chatLog.documentPlaceholder')"
            v-model="form_data.document_list"
          />
        </el-form-item>

        <el-form-item
          v-if="form_data.hasOwnProperty('image_list') || 'image_list' in form_data"
          :label="$t('views.applicationWorkflow.nodes.imageUnderstandNode.image.label')"
          prop="image_list"
          :rules="{
            message: $t(
              'views.applicationWorkflow.nodes.imageUnderstandNode.image.requiredMessage',
            ),
            trigger: 'blur',
            required: false,
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="
              $t('views.applicationWorkflow.nodes.imageUnderstandNode.image.requiredMessage')
            "
            v-model="form_data.image_list"
          />
        </el-form-item>

        <el-form-item
          v-if="form_data.hasOwnProperty('audio_list') || 'audio_list' in form_data"
          :label="$t('views.applicationWorkflow.nodes.speechToTextNode.audio.label')"
          prop="audio_list"
          :rules="{
            message: $t('views.applicationWorkflow.nodes.speechToTextNode.audio.placeholder'),
            trigger: 'blur',
            required: false,
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="$t('views.applicationWorkflow.nodes.speechToTextNode.audio.placeholder')"
            v-model="form_data.audio_list"
          />
        </el-form-item>
        <el-form-item
          v-if="form_data.hasOwnProperty('video_list') || 'video_list' in form_data"
          :label="$t('views.applicationWorkflow.nodes.videoUnderstandNode.video.label')"
          prop="video_list"
          :rules="{
            message: $t(
              'views.applicationWorkflow.nodes.videoUnderstandNode.video.requiredMessage',
            ),
            trigger: 'blur',
            required: false,
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="
              $t('views.applicationWorkflow.nodes.videoUnderstandNode.video.requiredMessage')
            "
            v-model="form_data.video_list"
          />
        </el-form-item>
        <div v-for="(field, index) in form_data.api_input_field_list" :key="'api-input-' + index">
          <el-form-item
            :label="field.variable"
            :prop="'api_input_field_list.' + index + '.value'"
            :rules="[
              {
                required: field.is_required,
                message: `${$t('common.inputPlaceholder')}${field.variable}`,
                trigger: 'blur',
              },
            ]"
          >
            <NodeCascader
              ref="nodeCascaderRef"
              :nodeModel="nodeModel"
              class="w-full"
              :placeholder="
                $t('views.applicationWorkflow.nodes.searchKnowledgeNode.searchQuestion.placeholder')
              "
              v-model="form_data.api_input_field_list[index].value"
            />
          </el-form-item>
        </div>

        <div v-for="(field, index) in form_data.user_input_field_list" :key="'user-input-' + index">
          <el-form-item
            :label="field.label"
            :prop="'user_input_field_list.' + index + '.value'"
            :rules="[
              {
                required: field.required,
                message: `${$t('common.inputPlaceholder')}${field.label}`,
                trigger: 'blur',
              },
            ]"
          >
            <NodeCascader
              ref="nodeCascaderRef"
              :nodeModel="nodeModel"
              class="w-full"
              :placeholder="
                $t('views.applicationWorkflow.nodes.searchKnowledgeNode.searchQuestion.placeholder')
              "
              v-model="form_data.user_input_field_list[index].value"
            />
          </el-form-item>
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
          <el-switch size="small" v-model="form_data.is_result" />
        </el-form-item>
      </el-form>
    </el-card>
  </NodeContainer>
</template>

<script setup lang="ts">
import { set, groupBy, create, cloneDeep } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { ref, computed, onMounted, onActivated } from 'vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import { isWorkFlow } from '@/utils/application'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const route = useRoute()

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const form = {
  question_reference_address: ['start-node', 'question'],
  api_input_field_list: [],
  user_input_field_list: [],
  document_list: ['start-node', 'document'],
  image_list: ['start-node', 'image'],
  audio_list: ['start-node', 'audio'],
  video_list: ['start-node', 'video'],
}

const applicationNodeFormRef = ref<FormInstance>()

const form_data = computed({
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

function handleFileUpload(type: string, isEnabled: boolean) {
  const listKey = `${type}_list`
  if (isEnabled) {
    if (!props.nodeModel.properties.node_data[listKey]) {
      set(props.nodeModel.properties.node_data, listKey, [])
    }
  } else {
    // eslint-disable-next-line vue/no-mutating-props
    delete props.nodeModel.properties.node_data[listKey]
  }
}

const update_field = () => {
  if (!props.nodeModel.properties.node_data.application_id) {
    set(props.nodeModel.properties, 'status', 500)
    return
  }
  loadSharedApi({ type: 'application', systemType: apiType.value })
    .getApplicationDetail(props.nodeModel.properties.node_data.application_id)
    .then((ok: any) => {
      const old_api_input_field_list = cloneDeep(
        props.nodeModel.properties.node_data.api_input_field_list,
      )
      const old_user_input_field_list = cloneDeep(
        props.nodeModel.properties.node_data.user_input_field_list,
      )
      if (isWorkFlow(ok.data.type)) {
        const nodeData = ok.data.work_flow.nodes[0].properties.node_data
        const new_api_input_field_list = cloneDeep(
          ok.data.work_flow.nodes[0].properties.api_input_field_list,
        )
        const new_user_input_field_list = cloneDeep(
          ok.data.work_flow.nodes[0].properties.user_input_field_list,
        )

        const merge_api_input_field_list = (new_api_input_field_list || []).map((item: any) => {
          const find_field = old_api_input_field_list?.find(
            (old_item: any) => old_item.variable == item.variable,
          )
          if (find_field) {
            return {
              ...item,
              value: find_field.value,
              label:
                typeof item.label === 'object' && item.label != null
                  ? item.label.label
                  : item.label,
            }
          } else {
            return item
          }
        })
        set(
          props.nodeModel.properties.node_data,
          'api_input_field_list',
          merge_api_input_field_list,
        )
        const merge_user_input_field_list = (new_user_input_field_list || []).map((item: any) => {
          const find_field = old_user_input_field_list?.find(
            (old_item: any) => old_item.field == item.field,
          )
          if (find_field) {
            return {
              ...item,
              value: find_field.value,
              label:
                typeof item.label === 'object' && item.label != null
                  ? item.label.label
                  : item.label,
            }
          } else {
            return item
          }
        })
        set(
          props.nodeModel.properties.node_data,
          'user_input_field_list',
          merge_user_input_field_list,
        )
        const fileEnable = nodeData.file_upload_enable
        const fileUploadSetting = nodeData.file_upload_setting
        if (fileEnable) {
          handleFileUpload('document', fileUploadSetting.document)
          handleFileUpload('image', fileUploadSetting.image)
          handleFileUpload('audio', fileUploadSetting.audio)
          handleFileUpload('video', fileUploadSetting.video)
        } else {
          ;['document_list', 'image_list', 'audio_list', 'video_list'].forEach((list) => {
            // eslint-disable-next-line vue/no-mutating-props
            delete props.nodeModel.properties.node_data[list]
          })
        }
        set(props.nodeModel.properties, 'status', ok.data.id ? 200 : 500)
      }
    })
    .catch((err: any) => {
      console.log(err)
      set(props.nodeModel.properties, 'status', 500)
    })
}

const props = defineProps<{ nodeModel: any }>()

const validate = () => {
  return applicationNodeFormRef.value?.validate().catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

onMounted(() => {
  update_field()
  set(props.nodeModel, 'validate', validate)
})
</script>

<style lang="scss" scoped></style>
