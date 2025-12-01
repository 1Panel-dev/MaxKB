<template>
  <NodeContainer :nodeModel="nodeModel">
    <UserInputFieldTable ref="UserInputFieldTableFef" :node-model="nodeModel" />
    <template v-if="nodeFields.length > 0">
      <h5 class="title-decoration-1 mb-8 mt-8">
        {{ $t('common.param.outputParam') }}
      </h5>
      <template v-for="(item, index) in nodeFields" :key="index">
        <div
          class="flex-between border-r-6 p-8-12 mb-8 layout-bg lighter"
          @mouseenter="showicon = index"
          @mouseleave="showicon = null"
        >
          <span class="break-all">{{ item.label }} {{ '{' + item.value + '}' }}</span>
          <el-tooltip
            effect="dark"
            :content="$t('views.workflow.setting.copyParam')"
            placement="top"
            v-if="showicon === index"
          >
            <el-button link @click="copyClick(item.globeLabel)" style="padding: 0">
              <AppIcon iconName="app-copy"></AppIcon>
            </el-button>
          </el-tooltip>
        </div>
      </template>
    </template>
  </NodeContainer>
</template>
<script setup lang="ts">
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { ref, computed, onMounted, inject } from 'vue'
import { copyClick } from '@/utils/clipboard'
import { set } from 'lodash'

import UserInputFieldTable from './component/UserInputFieldTable.vue'
const showicon = ref<number | null>(null)
const getResourceDetail = inject('getResourceDetail') as any

const props = defineProps<{ nodeModel: any }>()

const UserInputFieldTableFef = ref()

const nodeFields = computed(() => {
  if (props.nodeModel.properties.user_input_field_list) {
    const fields = props.nodeModel.properties.user_input_field_list.map((item: any) => ({
      label: typeof item.label == 'string' ? item.label : item.label.label,
      value: item.field,
      globeLabel: `{{global.${typeof item.label == 'string' ? item.label : item.label.label}}}`,
      globeValue: `{{context['global'].${item.field}}}`,
    }))
    set(props.nodeModel.properties.config, 'globalFields', fields)
    return fields
  }
  set(props.nodeModel.properties.config, 'globalFields', [])
  return []
})
const resource = getResourceDetail()

onMounted(() => {})
</script>
<style lang="scss" scoped>
:deep(.el-form-item__label) {
  display: block;
}
</style>
