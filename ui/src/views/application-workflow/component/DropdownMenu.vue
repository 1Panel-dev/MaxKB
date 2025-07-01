<template>
  <div v-show="show" class="workflow-dropdown-menu border border-r-6">
    <el-tabs v-model="activeName" class="workflow-dropdown-tabs">
      <div style="display: flex; width: 100%; justify-content: center;" class="mb-12">
        <el-input v-model="search_text" class="mr-12 ml-12"
          :placeholder="$t('views.applicationWorkflow.searchBar.placeholder')">
          <template #suffix>
            <el-icon class="el-input__icon"><search /></el-icon>
          </template>
        </el-input>
      </div>

      <el-tab-pane :label="$t('views.applicationWorkflow.baseComponent')" name="base">
        <el-scrollbar height="400">
          <div v-if="filter_menu_nodes.length > 0">
            <template v-for="(node, index) in filter_menu_nodes" :key="index">
              <el-text type="info" size="small" class="color-secondary ml-12">{{ node.label }}</el-text>
              <div class="flex-wrap mt-8">
                <template v-for="(item, index) in node.list" :key="index">
                  <el-popover placement="right" :width="280">
                    <template #reference>
                      <div class="flex align-center border border-r-6 mb-12 p-8-12 cursor ml-12" style="width: 39%; " @click.stop="clickNodes(item)"
                        @mousedown.stop="onmousedown(item)">
                        <component :is="iconComponent(`${item.type}-icon`)" class="mr-8" :size="32" />
                        <div class="lighter">{{ item.label }}</div>
                      </div>
                    </template>
                    <template #default>
                      <div class="flex align-center mb-8">
                        <component :is="iconComponent(`${item.type}-icon`)" class="mr-8" :size="32" />
                        <div class="lighter color-text-primary">{{ item.label }}</div>
                      </div>
                      <el-text type="info" size="small" class="color-secondary lighter">{{ item.text }}</el-text>
                    </template>
                  </el-popover>
                </template>
              </div>
            </template>
          </div>
          <div v-else class="ml-16 mt-8">
            <el-text type="info">{{ $t('views.applicationWorkflow.tip.noData') }}</el-text>
          </div>
        </el-scrollbar>
      </el-tab-pane>
      <el-tab-pane :label="$t('views.tool.title')" name="tool">
        <el-scrollbar height="400">
          <div
            class="workflow-dropdown-item cursor flex p-8-12"
            @click.stop="clickNodes(toolNode)"
            @mousedown.stop="onmousedown(toolNode)"
          >
            <component :is="iconComponent(`tool-lib-node-icon`)" class="mr-8 mt-4" :size="32" />
            <div class="pre-wrap">
              <div class="lighter">{{ toolNode.label }}</div>
              <el-text type="info" size="small">{{ toolNode.text }}</el-text>
            </div>
          </div>

          <template v-for="(item, index) in filter_tool_lib_list" :key="index">
            <div
              class="workflow-dropdown-item cursor flex p-8-12 align-center"
              @click.stop="clickNodes(toolLibNode, item, 'tool')"
              @mousedown.stop="onmousedown(toolLibNode, item, 'tool')"
            >
              <component
                :is="iconComponent(`tool-lib-node-icon`)"
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
import { menuNodes, toolNode, toolLibNode, applicationNode } from '@/workflow/common/data'
import { iconComponent } from '@/workflow/icons/utils'
import applicationApi from '@/api/application/application'
import { isWorkFlow } from '@/utils/application'
import { isAppIcon } from '@/utils/common'
const search_text = ref<string>('')
const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  id: {
    type: String,
    default: '',
  },
  workflowRef: Object,
})

const emit = defineEmits(['clickNodes', 'onmousedown'])

const loading = ref(false)
const activeName = ref('base')

const toolList = ref<any[]>([])
const filter_tool_lib_list = computed(() => {
  return toolList.value.filter((item: any) =>
    item.name.toLocaleLowerCase().includes(search_text.value.toLocaleLowerCase()),
  )
})
const applicationList = ref<any[]>([])
const filter_application_list = computed(() => {
  return applicationList.value.filter((item: any) =>
    item.name.toLocaleLowerCase().includes(search_text.value.toLocaleLowerCase()),
  )
})

const filter_menu_nodes = computed(() => {
  if (!search_text.value) return menuNodes;
  const searchTerm = search_text.value.toLowerCase();
  
  return menuNodes.reduce((result: any[], item) => {
    const filteredList = item.list.filter(listItem => 
      listItem.label.toLowerCase().includes(searchTerm)
    );
    
    if (filteredList.length) {
      result.push({ ...item, list: filteredList });
    }
    
    return result;
  }, []);
});
function clickNodes(item: any, data?: any, type?: string) {
  if (data) {
    item['properties']['stepName'] = data.name
    if (type == 'tool') {
      item['properties']['node_data'] = {
        ...data,
        tool_lib_id: data.id,
        input_field_list: data.input_field_list.map((field: any) => ({
          ...field,
          value: field.source == 'reference' ? [] : '',
        })),
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
              ...(fileUploadSetting.audio ? { audio_list: [] } : {}),
            }),
        }
      } else {
        item['properties']['node_data'] = {
          name: data.name,
          icon: data.icon,
          application_id: data.id,
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
    if (type == 'tool') {
      item['properties']['node_data'] = {
        ...data,
        tool_lib_id: data.id,
        input_field_list: data.input_field_list.map((field: any) => ({
          ...field,
          value: field.source == 'reference' ? [] : '',
        })),
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
              ...(fileUploadSetting.audio ? { audio_list: [] } : {}),
            }),
        }
      } else {
        item['properties']['node_data'] = {
          name: data.name,
          icon: data.icon,
          application_id: data.id,
        }
      }
    }
  }
  props.workflowRef?.onmousedown(item)
  emit('onmousedown', item)
}

function getList() {
  // applicationApi.listTool(props.id, loading).then((res: any) => {
  //   toolList.value = res.data
  // })
  // applicationApi.getApplicationList(props.id, loading).then((res: any) => {
  //   applicationList.value = res.data
  // })
}

onMounted(() => {
  // getList()
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
  width: 400px;
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
