<script setup lang="ts">
import { computed, ref } from 'vue'

import aiChatIcon from '@/assets/workflow/icon_ai_chat.svg'
import replyIcon from '@/assets/workflow/icon_reply.svg'
import { WorkflowNodeType } from '@/workflow-canvas/types'

defineOptions({ name: 'NodeMenu' })

const emit = defineEmits<{ select: [nodeType: WorkflowNodeType] }>()

type WorkflowComponentTab = 'basic' | 'tool' | 'application'

const activeTab = ref<WorkflowComponentTab>('basic')
const searchKeyword = ref('')

const workflowComponentTabs: Array<{ label: string; value: WorkflowComponentTab }> = [
  { label: '基础组件', value: 'basic' },
  { label: '工具', value: 'tool' },
  { label: '智能体', value: 'application' },
]

const workflowComponentOptions = [
  { icon: aiChatIcon, iconClass: 'bg-primary-gradient', label: 'AI 对话', value: WorkflowNodeType.AiChat },
  { icon: replyIcon, iconClass: 'bg-warning', label: '指定回复', value: WorkflowNodeType.Reply },
] satisfies Array<{ icon: string; iconClass: string; label: string; value: WorkflowNodeType }>

const filteredComponentOptions = computed(() => {
  if (activeTab.value !== 'basic') return []

  const keyword = searchKeyword.value.trim().toLocaleLowerCase()
  if (!keyword) return workflowComponentOptions

  return workflowComponentOptions.filter((componentOption) => componentOption.label.toLocaleLowerCase().includes(keyword))
})
</script>

<template>
  <div class="w-[402px] overflow-hidden rounded-md border border-N300 bg-white shadow-lg" @click.stop @mousedown.stop @mousemove.stop>
    <div class="flex h-11 items-stretch gap-7 border-b border-N300 px-4" role="tablist">
      <button
        v-for="componentTab in workflowComponentTabs"
        :key="componentTab.value"
        type="button"
        role="tab"
        class="relative font-medium"
        :class="activeTab === componentTab.value ? 'text-primary' : 'text-N900'"
        :aria-selected="activeTab === componentTab.value"
        @click="activeTab = componentTab.value"
      >
        {{ componentTab.label }}
        <span v-if="activeTab === componentTab.value" class="absolute inset-x-0 bottom-0 h-0.5 rounded-full bg-primary" />
      </button>
    </div>

    <div class="p-3">
      <MkSearchInput v-model="searchKeyword" placeholder="按名称搜索" />

      <template v-if="filteredComponentOptions.length">
        <p class="mb-3 mt-3 text-N600">AI 能力</p>
        <div class="grid grid-cols-2 gap-3">
          <button
            v-for="componentOption in filteredComponentOptions"
            :key="componentOption.value"
            type="button"
            class="flex h-10 items-center gap-3 rounded-md border border-N300 px-3 text-left text-N900 hover:border-primary hover:text-primary"
            @click="emit('select', componentOption.value)"
          >
            <span class="flex size-6 shrink-0 items-center justify-center rounded-md" :class="componentOption.iconClass">
              <img :src="componentOption.icon" alt="" class="size-4" />
            </span>
            <span>{{ componentOption.label }}</span>
          </button>
        </div>
      </template>
      <MkEmpty v-else :type="searchKeyword ? 'search' : 'default'" :image-size="72" />
    </div>
  </div>
</template>
