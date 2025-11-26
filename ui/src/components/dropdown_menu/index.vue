<template>
  <component :is="kw[workflow_mode]" :show="show" :id="id" :workflow-ref="workflowRef"></component>
</template>
<script setup lang="ts">
import { inject } from 'vue'
import { WorkflowMode } from '@/enums/application'
import ApplicationDropdownMenu from '@/components/dropdown_menu/application/index.vue'
import KnowledgeDropdownMenu from '@/components/dropdown_menu/knowledge/index.vue'
const workflow_mode = inject('workflowMode') || WorkflowMode.Application
defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  id: {
    type: String,
    default: '',
  },
  workflowRef: Object,
})
const kw: any = {
  [WorkflowMode.Application]: ApplicationDropdownMenu,
  [WorkflowMode.Knowledge]: KnowledgeDropdownMenu,
}
</script>
<style lang="scss">
@use './index.scss';
</style>
