<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'VariableAssignNodeDetail' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <!-- 输入参数 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">输入参数</h6>
      <div class="space-y-2">
        <p v-for="(assignment, assignmentIndex) in data.result_list" :key="assignmentIndex">
          <span class="text-N600">{{ assignment.name }} ({{ assignment.input_type }})：</span>{{ assignment.input_value }}
        </p>
      </div>
    </div>

    <!-- 输出参数 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">输出参数</h6>
      <div class="space-y-2">
        <p v-for="(assignment, assignmentIndex) in data.result_list" :key="assignmentIndex">
          <span class="text-N600">{{ assignment.name }} ({{ assignment.output_type }})：</span>{{ assignment.output_value }}
        </p>
      </div>
    </div>
  </DetailContainer>
</template>
