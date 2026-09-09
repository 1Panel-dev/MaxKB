<script setup lang="ts">
import { ref, watch } from 'vue'
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import { MkDynamicsForm } from '@/components/mk-dynamics-form'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

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
    <template #header="{ show }">
      <BaseHeader :data="data" :show="show" />
    </template>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">
        输出参数
        <span v-if="!data.is_submit" class="text-danger">(未提交)</span>
      </h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <MkDynamicsForm
          v-model="formData"
          :render-data="data.form_field_list"
          :view="true"
          label-position="top"
        />
      </div>
    </div>
  </DetailContainer>
</template>
