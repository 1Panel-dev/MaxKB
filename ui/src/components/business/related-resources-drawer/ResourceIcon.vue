<script setup lang="ts">
import { computed } from 'vue'
import { RESOURCE_TYPE, TOOL_TYPE } from '@/api/enums'
import type { ModelProviderItem, ResourceType } from '@/api/types'

defineOptions({ name: 'RelatedResourceIcon' })
const props = defineProps<{
  resourceType: ResourceType
  type?: string | number | null
  icon?: string | null
  provider?: string
  providers: ModelProviderItem[]
}>()
const toolType = computed(() => Object.values(TOOL_TYPE).find((type) => type === props.type))
const providerIcon = computed(() => props.providers.find(({ provider }) => provider === (props.provider ?? props.icon))?.icon)
</script>

<template>
  <KnowledgeIcon v-if="resourceType === RESOURCE_TYPE.KNOWLEDGE" :type="String(type ?? icon ?? '')" :size="24" />
  <ApplicationIcon v-else-if="resourceType === RESOURCE_TYPE.APPLICATION" :icon="icon ?? undefined" :size="24" />
  <ToolIcon v-else-if="resourceType === RESOURCE_TYPE.TOOL" :icon="icon ?? undefined" :type="toolType" :size="24" />
  <span v-else-if="providerIcon" class="flex-center size-6 shrink-0" v-html="providerIcon" />
  <MkIcon v-else :size="24" />
</template>
