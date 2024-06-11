<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
      
    </el-card>
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
