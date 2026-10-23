<script setup lang="ts">
import { ref, watch } from 'vue'

defineOptions({ name: 'ConversationReasoningContent' })

const props = defineProps<{ content: { content?: string | null; status?: string } }>()
const isExpanded = ref(true)
let prevStatus = props.content.status

watch(
  () => props.content.status,
  (status) => {
    if (prevStatus === 'RUNNING' && status !== 'RUNNING') {
      isExpanded.value = false
    }
    prevStatus = status
  },
)
</script>

<template>
  <!-- 展开或收起思考内容 -->
  <MkCollapse v-model:expanded="isExpanded" indicator-position="after" trigger-class="group text-N500! mb-2 w-fit hover:text-N900!">
    <template #indicator="{ expanded }">
      <MkIcon
        name="icon_right_outlined"
        :size="12"
        class="transition-transform text-N500! group-hover:text-N900!"
        :class="{ 'rotate-90': expanded }"
      />
    </template>
    <template #label>
      <MkIcon name="icon_two-ellipses_outlined" />
      <span class="-mx-1">思考中</span>
    </template>
    <div class="text-N500! whitespace-pre-wrap break-words">
      {{ content.content }}
    </div>
  </MkCollapse>
</template>

<style scoped lang="scss"></style>
