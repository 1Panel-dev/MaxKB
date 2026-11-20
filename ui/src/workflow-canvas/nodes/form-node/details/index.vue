<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import { MkDynamicsForm } from '@/components/mk-dynamics-form'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'

defineOptions({ name: 'FormNodeDetail' })
const { t } = useI18n({ useScope: 'global' })

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

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">
        {{ t('workflow.executionResult.outputParams') }}
        <span v-if="!data.is_submit" class="text-danger">({{ t('workflow.form.notSubmitted') }})</span>
      </h6>
      <div>
        <MkDynamicsForm v-model="formData" :render-data="data.form_field_list" :view="true" />
      </div>
    </div>
  </DetailContainer>
</template>
