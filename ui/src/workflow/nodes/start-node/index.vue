<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">全局变量</h5>
    <div
      class="flex-between border-r-4 p-8-12 mb-8 layout-bg lighter"
      @mouseenter="showicon = true"
      @mouseleave="showicon = false"
    >
      <span>当前时间 {time}</span>
      <el-tooltip effect="dark" content="复制参数" placement="top" v-if="showicon === true">
        <el-button link @click="copyClick(globeLabel)" style="padding: 0">
          <AppIcon iconName="app-copy"></AppIcon>
        </el-button>
      </el-tooltip>
    </div>
    <div v-for="(item, index) in inputFieldList" :key="index"
         class="flex-between border-r-4 p-8-12 mb-8 layout-bg lighter"
         @mouseenter="showicon = true"
         @mouseleave="showicon = false"
    >
      <span>{{ item.name }} {{ '{' + item.variable + '}' }}</span>
      <el-tooltip effect="dark" content="复制参数" placement="top" v-if="showicon === true">
        <el-button link @click="copyClick('{{' + '全局变量.' + item.variable + '}}')" style="padding: 0">
          <AppIcon iconName="app-copy"></AppIcon>
        </el-button>
      </el-tooltip>
    </div>
  </NodeContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { copyClick } from '@/utils/clipboard'
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{ nodeModel: any }>()

const globeLabel = '{{全局变量.time}}'

const showicon = ref(false)

const inputFieldList = ref<any[]>([])

function handleRefreshFieldList(data: any[]) {
  props.nodeModel.graphModel.nodes
    .filter((v: any) => v.id === 'base-node')
    .map((v: any) => {
      // eslint-disable-next-line vue/no-mutating-props
      props.nodeModel.properties.config.globalFields = [
        {
          label: '当前时间',
          value: 'time'
        }, ...v.properties.input_field_list.map((i: any) => {
          return { label: i.name, value: i.variable }
        })
      ]
      inputFieldList.value = v.properties.input_field_list
    })
}

props.nodeModel.graphModel.eventCenter.on('refreshFieldList', (data: any) => {
  handleRefreshFieldList(data)
})

onMounted(() => {
  handleRefreshFieldList([])
})
</script>
<style lang="scss" scoped></style>
