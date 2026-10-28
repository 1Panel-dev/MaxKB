<script setup lang="ts">
import { computed, ref, type Component } from 'vue'
import type { ChatContent, Dict } from '@/api/types'
import ToolItem from './components/ToolItem.vue'
import Terminal from '../tool/Terminal.vue'
import Patch from '../tool/Patch.vue'
import ReadFile from '../tool/ReadFile.vue'
import ListDir from '../tool/ListDir.vue'
import Grep from '../tool/Grep.vue'
import Glob from '../tool/Glob.vue'
import CreateFile from '../tool/CreateFile.vue'
import ListSkills from '../tool/ListSkills.vue'
import DownloadSkills from '../tool/DownloadSkills.vue'
import RunSkill from '../tool/RunSkill.vue'

defineOptions({ name: 'ConversationGroupToolContent' })

const props = defineProps<{ content: ChatContent }>()

// 相邻工具由 content-list 聚合，分组内按工具名选择专用展示。
const toolItems = computed(() => props.content.children ?? [])

// 工具名（小写）→ 专用渲染器；新增工具时与 tool/index.vue 同步
const toolRenderers: Dict<Component> = {
  run_command: Terminal,
  apply_patch: Patch,
  read_file: ReadFile,
  list_dir: ListDir,
  grep: Grep,
  glob: Glob,
  create_file: CreateFile,
  list_skills: ListSkills,
  download_skills: DownloadSkills,
  run_skill: RunSkill,
}

function resolveToolRenderer(toolName: unknown): Component | undefined {
  return toolRenderers[String(toolName || '').toLowerCase()]
}

// 组内专用渲染器的展开状态：执行中默认展开，结束后默认收起，手动切换后以手动为准
const manualToolExpanded = ref<Dict<boolean>>({})

function toolKey(toolItem: ChatContent, index: number) {
  return String(toolItem.id ?? index)
}

function isToolExpanded(toolItem: ChatContent, index: number) {
  return manualToolExpanded.value[toolKey(toolItem, index)] ?? toolItem.status === 'RUNNING'
}

function toggleTool(toolItem: ChatContent, index: number) {
  manualToolExpanded.value[toolKey(toolItem, index)] = !isToolExpanded(toolItem, index)
}

// 汇总执行状态；分组和工具的手动展开状态优先于默认状态。
const groupStatus = computed(() => {
  const childStatuses = toolItems.value.map((toolItem) => toolItem.status)
  if (childStatuses.includes('RUNNING')) return 'running'
  if (childStatuses.some((childStatus) => childStatus === 'FAIL' || childStatus === 'FAILURE')) return 'error'
  return childStatuses.length ? 'success' : ''
})

// const STATUS_TEXT: Dict<string> = { running: '执行中', success: '成功', error: '失败' }
// const statusText = computed(() => STATUS_TEXT[groupStatus.value] ?? '')

const manualExpanded = ref<boolean>()
const isExpanded = computed({
  get: () => manualExpanded.value ?? groupStatus.value === 'running',
  set: (value: boolean) => (manualExpanded.value = value),
})
</script>

<template>
  <!-- 展开或收起分组工具 -->
  <MkCollapse
    class="mb-2 w-full"
    v-model:expanded="isExpanded"
    indicator-position="after"
    trigger-class="group text-N500! mb-2 w-fit hover:text-N900!"
  >
    <template #indicator="{ expanded }">
      <MkIcon
        name="icon_right_outlined"
        :size="12"
        class="transition-transform text-N500! group-hover:text-N900!"
        :class="{ 'rotate-90': expanded }"
      />
    </template>
    <template #label>
      <span v-if="groupStatus === 'running'" class="mk-conversation-loading" />
      <span>调用了 {{ toolItems.length }} 个工具</span>
    </template>

    <div v-show="toolItems.length">
      <template v-for="(toolItem, index) in toolItems" :key="toolItem.id ?? index">
        <div v-if="resolveToolRenderer(toolItem.name)">
          <component
            :is="resolveToolRenderer(toolItem.name)"
            :content="toolItem"
            :loading="toolItem.status === 'RUNNING'"
            :expanded="isToolExpanded(toolItem, index)"
            @update:expanded="manualToolExpanded[toolKey(toolItem, index)] = $event"
            @toggle="toggleTool(toolItem, index)"
          />
        </div>
        <ToolItem v-else :tool-item="toolItem" />
      </template>
    </div>
  </MkCollapse>
</template>
