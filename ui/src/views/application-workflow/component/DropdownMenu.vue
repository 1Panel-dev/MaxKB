<template>
  <div v-show="show" class="workflow-dropdown-menu border border-r-4">
    <el-tabs v-model="activeName" class="workflow-dropdown-tabs">
      <div style="display: flex; width: 100%; justify-content: center">
        <el-input v-model="search_text" style="width: 240px" placeholder="按名称搜索">
          <template #suffix>
            <el-icon class="el-input__icon"><search /></el-icon>
          </template>
        </el-input>
      </div>

      <el-tab-pane label="基础组件" name="base">
        <el-scrollbar height="400">
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
        </el-scrollbar>
      </el-tab-pane>
      <el-tab-pane label="函数库" name="function">
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
              class="workflow-dropdown-item cursor flex p-8-12"
              @click.stop="clickNodes(functionLibNode, item)"
              @mousedown.stop="onmousedown(functionLibNode, item)"
            >
              <component
                :is="iconComponent(`function-lib-node-icon`)"
                class="mr-8 mt-4"
                :size="32"
              />
              <div class="pre-wrap">
                <div class="lighter">{{ item.name }}</div>
                <el-text type="info" size="small">{{ item.desc }}</el-text>
              </div>
            </div>
          </template>
        </el-scrollbar>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { menuNodes, functionLibNode, functionNode } from '@/workflow/common/data'
import { iconComponent } from '@/workflow/icons/utils'
import applicationApi from '@/api/application'
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
const filter_menu_nodes = computed(() => {
  return menuNodes.filter((item) =>
    item.label.toLocaleLowerCase().includes(search_text.value.toLocaleLowerCase())
  )
})
function clickNodes(item: any, data?: any) {
  if (data) {
    item['properties']['stepName'] = data.name
    item['properties']['node_data'] = {
      ...data,
      function_lib_id: data.id,
      input_field_list: data.input_field_list.map((field: any) => ({
        ...field,
        value: field.source == 'reference' ? [] : ''
      }))
    }
  }
  props.workflowRef?.addNode(item)

  emit('clickNodes', item)
}

function onmousedown(item: any, data?: any) {
  if (data) {
    item['properties']['stepName'] = data.name
    item['properties']['node_data'] = {
      ...data,
      function_lib_id: data.id,
      input_field_list: data.input_field_list.map((field: any) => ({
        ...field,
        value: field.source == 'reference' ? [] : ''
      }))
    }
  }
  props.workflowRef?.onmousedown(item)
  emit('onmousedown', item)
}

function getList() {
  applicationApi.listFunctionLib(props.id, loading).then((res: any) => {
    functionLibList.value = res.data
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
  right: 90px;
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
