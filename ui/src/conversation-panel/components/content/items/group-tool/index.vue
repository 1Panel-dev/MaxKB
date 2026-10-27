<template>
  <div class="content-group-tool">
    <!-- 分组头部：摘要 + 状态，点击展开/收起组内工具 -->
    <button type="button" class="group-header" @click="isExpanded = !isExpanded">
      <span class="group-name">调用了 {{ toolItems.length }} 个工具</span>
      <span v-if="groupStatus" class="group-status" :class="groupStatus">{{ statusText }}</span>
      <svg class="group-chevron" :class="{ open: isExpanded }" viewBox="0 0 16 16" fill="none">
        <path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>

    <!-- 组内工具：每个工具一行，有专用渲染器的按工具名展示，其余可单独展开参数与结果 -->
    <div v-show="isExpanded && toolItems.length" class="group-body">
      <template v-for="(toolItem, index) in toolItems" :key="toolItem.id ?? index">
        <div v-if="resolveToolRenderer(toolItem.name)" class="group-row group-row-custom">
          <component
            :is="resolveToolRenderer(toolItem.name)"
            :content="toolItem"
            :loading="toolItem.status === 'RUNNING'"
            :expanded="isToolExpanded(toolItem, index)"
            @toggle="toggleTool(toolItem, index)"
          />
        </div>
        <ToolItem v-else :tool-item="toolItem" class="group-row" />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, type Component } from 'vue'
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

/**
 * 分组工具卡：由 content-list 把相邻 TOOL 折叠而成，content.children 为组内 TOOL 内容项。
 * 组内工具按工具名使用专用渲染器（与单个 TOOL 的 tool/index.vue 一致），未匹配的工具以参数/结果行展示。
 * 状态由组内工具汇总：有执行中为执行中，否则有失败为失败，否则成功。
 * 执行中默认展开，结束后默认收起，手动切换后以手动为准。
 */
const props = defineProps<{ content: any }>()

const toolItems = computed<any[]>(() => props.content.children ?? [])

// 工具名（小写）→ 专用渲染器；新增工具时与 tool/index.vue 同步
const toolRenderers: Record<string, Component> = {
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

type GroupToolItem = { id?: string; status?: string }

// 组内专用渲染器的展开状态：执行中默认展开，结束后默认收起，手动切换后以手动为准
const manualToolExpanded = ref<Record<string, boolean>>({})

function toolKey(toolItem: GroupToolItem, index: number) {
  return String(toolItem.id ?? index)
}

function isToolExpanded(toolItem: GroupToolItem, index: number) {
  return manualToolExpanded.value[toolKey(toolItem, index)] ?? toolItem.status === 'RUNNING'
}

function toggleTool(toolItem: GroupToolItem, index: number) {
  manualToolExpanded.value[toolKey(toolItem, index)] = !isToolExpanded(toolItem, index)
}

const groupStatus = computed(() => {
  const childStatuses = toolItems.value.map((toolItem) => toolItem.status)
  if (childStatuses.includes('RUNNING')) return 'running'
  if (childStatuses.some((childStatus) => childStatus === 'FAIL' || childStatus === 'FAILURE')) return 'error'
  return childStatuses.length ? 'success' : ''
})

const STATUS_TEXT: Record<string, string> = { running: '执行中', success: '成功', error: '失败' }
const statusText = computed(() => STATUS_TEXT[groupStatus.value] ?? '')

const manualExpanded = ref<boolean>()
const isExpanded = computed({
  get: () => manualExpanded.value ?? groupStatus.value === 'running',
  set: (value: boolean) => (manualExpanded.value = value),
})
</script>

<style scoped lang="scss">
.content-group-tool {
  margin-bottom: 8px;
}

.group-header {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 100%;
  padding: 4px 0;
  border: none;
  background: none;
  cursor: pointer;
  font-family: inherit;
  font-size: 13px;
  color: var(--t2, #606266);
  transition: color 0.15s;
}

.group-header:hover {
  color: var(--t1, #303133);
}

.group-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.group-status {
  flex-shrink: 0;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--hv, #f5f7fa);
}

.group-status.success {
  color: #67c23a;
}

.group-status.error {
  color: #f56c6c;
}

.group-status.running {
  color: var(--t3, #909399);
}

.group-chevron {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
  color: var(--t3, #909399);
  transition: transform 0.15s;
}

.group-chevron:not(.open) {
  transform: rotate(-90deg);
}

.group-body {
  margin-top: 4px;
  background: var(--bg2, #fafafa);
  border: 1px solid var(--bd, #dcdfe6);
  border-radius: 8px;
  overflow: hidden;
}

.group-row-custom {
  padding: 5px 12px;
}

.group-row + .group-row {
  border-top: 1px solid var(--bd, #ebeef5);
}
</style>
