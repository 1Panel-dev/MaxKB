<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('workflow.nodeSetting') }}</h5>
    <InputFieldTable :nodeModel="nodeModel"></InputFieldTable>
    <OutFieldTable :nodeModel="nodeModel"></OutFieldTable>
  </NodeContainer>
</template>
<script setup lang="ts">
import NodeContainer from '@/workflow/common/NodeContainer.vue'
const props = defineProps<{ nodeModel: any }>()
import InputFieldTable from './component/input/InputFieldTable.vue'
import OutFieldTable from './component/output/OutputFieldTable.vue'
</script>
<style lang="scss" scoped></style>
