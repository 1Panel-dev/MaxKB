<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">全局变量</h5>
    <div class="border-r-4 p-8-12 mb-8 layout-bg lighter">当前时间 {time}</div>
  </NodeContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{ nodeModel: any }>()

// onMounted(() => {
//   set(props.nodeModel, 'validate', validate)
// })
</script>
<style lang="scss" scoped></style>
