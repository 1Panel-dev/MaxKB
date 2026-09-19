<script setup lang="ts">
import { ref, watch } from 'vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import { MkDynamicsForm } from '@/components/mk-dynamics-form'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'FormNodeDetail' })

const props = defineProps<{
  data: ExecutionNodeDetail
}>()

const formData = ref(props.data?.form_data || {})
watch(
  () => props.data?.form_data,
  (value) => {
    formData.value = value || {}
  },
)
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">
        输出参数
        <span v-if="!data.is_submit" class="text-danger">(未提交)</span>
      </h6>
      <div>
        <MkDynamicsForm v-model="formData" :render-data="data.form_field_list" :view="true" label-position="top" />
      </div>
    </div>
  </DetailContainer>
</template>
