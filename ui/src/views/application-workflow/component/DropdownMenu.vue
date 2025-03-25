<template>
  <div v-show="show" class="workflow-dropdown-menu border border-r-4">
    <el-tabs v-model="activeName" class="workflow-dropdown-tabs">
      <div style="display: flex; width: 100%; justify-content: center" class="mb-4">
        <el-input
          v-model="search_text"
          style="width: 240px"
          :placeholder="$t('views.applicationWorkflow.searchBar.placeholder')"
        >
          <template #suffix>
            <el-icon class="el-input__icon"><search /></el-icon>
          </template>
        </el-input>
      </div>

      <el-tab-pane :label="$t('views.applicationWorkflow.baseComponent')" name="base">
        <el-scrollbar height="400">
          <div v-if="filter_menu_nodes.length > 0">
            <template v-for="(item, index) in filter_menu_nodes" :key="index">
              <div
                class="workflow-dropdown-item cursor flex p-8-12"
                @click.stop="clickNodes(item)"
                @mousedown.stop="onmousedown(item)"
              >
                <component :is="iconComponent(`${item.type}-icon`)" class="mr-8 mt-4" :size="32" />
                <div class="pre-wrap">
                  <div class="lighter">{{ item.label }}</div>
                  <el-text type="info" size="small">{{ item.text }}</el-text>
                </div>
              </div>
            </template>
          </div>
          <div v-else class="ml-16 mt-8">
            <el-text type="info">{{ $t('views.applicationWorkflow.tip.noData') }}</el-text>
          </div>
        </el-scrollbar>
      </el-tab-pane>
      <el-tab-pane :label="$t('views.functionLib.title')" name="function">
        <el-scrollbar height="400">
          <div
            class="workflow-dropdown-item cursor flex p-8-12"
            @click.stop="clickNodes(functionNode)"
            @mousedown.stop="onmousedown(functionNode)"
          >
            <component :is="iconComponent(`function-lib-node-icon`)" class="mr-8 mt-4" :size="32" />
            <div class="pre-wrap">
              <div class="lighter">{{ functionNode.label }}</div>
              <el-text type="info" size="small">{{ functionNode.text }}</el-text>
            </div>
          </div>

          <template v-for="(item, index) in filter_function_lib_list" :key="index">
            <div
              class="workflow-dropdown-item cursor flex p-8-12 align-center"
              @click.stop="clickNodes(functionLibNode, item, 'function')"
              @mousedown.stop="onmousedown(functionLibNode, item, 'function')"
            >
              <component
                :is="iconComponent(`function-lib-node-icon`)"
                class="mr-8"
                :size="32"
                :item="item"
              />

              <div class="pre-wrap">
                <div class="lighter ellipsis-1" :title="item.name">{{ item.name }}</div>
                <p>
                  <el-text
                    class="ellipsis-1"
                    type="info"
                    size="small"
                    :title="item.desc"
                    v-if="item.desc"
                    >{{ item.desc }}</el-text
                  >
                </p>
              </div>
            </div>
          </template>
        </el-scrollbar>
      </el-tab-pane>
      <el-tab-pane :label="$t('views.application.title')" name="application">
        <el-scrollbar height="400">
          <div v-if="filter_application_list.length > 0">
            <template v-for="(item, index) in filter_application_list" :key="index">
              <div
                class="workflow-dropdown-item cursor flex align-center p-8-12"
                @click.stop="clickNodes(applicationNode, item, 'application')"
                @mousedown.stop="onmousedown(applicationNode, item, 'application')"
              >
                <component
                  :is="iconComponent(`application-node-icon`)"
                  class="mr-8"
                  :size="32"
                  :item="item"
                />
                <div class="pre-wrap" style="width: 60%">
                  <div class="lighter ellipsis" :title="item.name">
                    {{ item.name }}
                  </div>
                  <p>
                    <el-text
                      class="ellipsis"
                      type="info"
                      size="small"
                      :title="item.desc"
                      v-if="item.desc"
                      >{{ item.desc }}</el-text
                    >
                  </p>
                </div>
                <div class="status-tag" style="margin-left: auto">
                  <el-tag type="warning" v-if="isWorkFlow(item.type)" style="height: 22px">
                    {{ $t('views.application.workflow') }}</el-tag
                  >
                  <el-tag class="blue-tag" v-else style="height: 22px">{{
                    $t('views.application.simple')
                  }}</el-tag>
                </div>
              </div>
            </template>
          </div>
          <div v-else class="ml-16 mt-8">
            <el-text type="info">{{ $t('views.applicationWorkflow.tip.noData') }}</el-text>
          </div>
        </el-scrollbar>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { menuNodes, functionLibNode, functionNode, applicationNode } from '@/workflow/common/data'
import { iconComponent } from '@/workflow/icons/utils'
import applicationApi from '@/api/application'
import { isWorkFlow, isAppIcon } from '@/utils/application'
const search_text = ref<string>('')
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  id: {
    type: String,
    default: ''
  },
  workflowRef: Object
})

const emit = defineEmits(['clickNodes', 'onmousedown'])

const loading = ref(false)
const activeName = ref('base')

const functionLibList = ref<any[]>([])
const filter_function_lib_list = computed(() => {
  return functionLibList.value.filter((item: any) =>
    item.name.toLocaleLowerCase().includes(search_text.value.toLocaleLowerCase())
  )
})
const applicationList = ref<any[]>([])
const filter_application_list = computed(() => {
  return applicationList.value.filter((item: any) =>
    item.name.toLocaleLowerCase().includes(search_text.value.toLocaleLowerCase())
  )
})

const filter_menu_nodes = computed(() => {
  return menuNodes.filter((item) =>
    item.label.toLocaleLowerCase().includes(search_text.value.toLocaleLowerCase())
  )
})
function clickNodes(item: any, data?: any, type?: string) {
  if (data) {
    item['properties']['stepName'] = data.name
    if (type == 'function') {
      item['properties']['node_data'] = {
        ...data,
        function_lib_id: data.id,
        input_field_list: data.input_field_list.map((field: any) => ({
          ...field,
          value: field.source == 'reference' ? [] : ''
        }))
      }
    }
    if (type == 'application') {
      if (isWorkFlow(data.type)) {
        const nodeData = data.work_flow.nodes[0].properties.node_data
        const fileUploadSetting = nodeData.file_upload_setting
        item['properties']['node_data'] = {
          name: data.name,
          icon: data.icon,
          application_id: data.id,
          api_input_field_list: data.work_flow.nodes[0].properties.api_input_field_list,
          user_input_field_list: data.work_flow.nodes[0].properties.user_input_field_list,
          ...(!fileUploadSetting
            ? {}
            : {
                ...(fileUploadSetting.document ? { document_list: [] } : {}),
                ...(fileUploadSetting.image ? { image_list: [] } : {}),
                ...(fileUploadSetting.audio ? { audio_list: [] } : {})
              })
        }
      } else {
        item['properties']['node_data'] = {
          name: data.name,
          icon: data.icon,
          application_id: data.id
        }
      }
    }
  }
  props.workflowRef?.addNode(item)

  emit('clickNodes', item)
}

function onmousedown(item: any, data?: any, type?: string) {
  if (data) {
    item['properties']['stepName'] = data.name
    if (type == 'function') {
      item['properties']['node_data'] = {
        ...data,
        function_lib_id: data.id,
        input_field_list: data.input_field_list.map((field: any) => ({
          ...field,
          value: field.source == 'reference' ? [] : ''
        }))
      }
    }
    if (type == 'application') {
      if (isWorkFlow(data.type)) {
        const nodeData = data.work_flow.nodes[0].properties.node_data
        const fileUploadSetting = nodeData.file_upload_setting
        item['properties']['node_data'] = {
          name: data.name,
          icon: data.icon,
          application_id: data.id,
          api_input_field_list: data.work_flow.nodes[0].properties.api_input_field_list,
          user_input_field_list: data.work_flow.nodes[0].properties.user_input_field_list,
          ...(!fileUploadSetting
            ? {}
            : {
                ...(fileUploadSetting.document ? { document_list: [] } : {}),
                ...(fileUploadSetting.image ? { image_list: [] } : {}),
                ...(fileUploadSetting.audio ? { audio_list: [] } : {})
              })
        }
      } else {
        item['properties']['node_data'] = {
          name: data.name,
          icon: data.icon,
          application_id: data.id
        }
      }
    }
  }
  props.workflowRef?.onmousedown(item)
  emit('onmousedown', item)
}

function getList() {
  applicationApi.listFunctionLib(props.id, loading).then((res: any) => {
    functionLibList.value = res.data
  })
  applicationApi.getApplicationList(props.id, loading).then((res: any) => {
    applicationList.value = res.data
  })
}

onMounted(() => {
  getList()
})
</script>
<style lang="scss" scoped>
.workflow-dropdown-menu {
  -moz-user-select: none; /* Firefox */
  -webkit-user-select: none; /* WebKit内核 */
  -ms-user-select: none; /* IE10及以后 */
  -khtml-user-select: none; /* 早期浏览器 */
  -o-user-select: none; /* Opera */
  user-select: none; /* CSS3属性 */
  position: absolute;
  top: 49px;
  right: 122px;
  z-index: 99;
  width: 268px;
  box-shadow: 0px 4px 8px 0px var(--app-text-color-light-1);
  background: #ffffff;
  padding-bottom: 8px;

  .title {
    padding: 12px 12px 4px;
  }
  .workflow-dropdown-item {
    &:hover {
      background: var(--app-text-color-light-1);
    }
  }
}
</style>
