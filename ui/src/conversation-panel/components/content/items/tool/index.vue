<script setup lang="ts">
import { computed, ref, watch, type Component } from 'vue'
import type { ChatContent, Dict } from '@/api/types'
import Terminal from './Terminal.vue'
import Patch from './Patch.vue'
import ReadFile from './ReadFile.vue'
import ListDir from './ListDir.vue'
import Grep from './Grep.vue'
import Glob from './Glob.vue'
import CreateFile from './CreateFile.vue'
import ListSkills from './ListSkills.vue'
import DownloadSkills from './DownloadSkills.vue'
import RunSkill from './RunSkill.vue'
import DefaultTool from './tool.vue'

defineOptions({ name: 'ConversationToolContent' })

const props = defineProps<{ content: ChatContent }>()

// 工具执行状态与展开状态。
const loading = computed(() => props.content.status === 'RUNNING')
const isExpanded = ref(props.content.status === 'RUNNING')

// 工具执行完成自动收起
watch(loading, (current, previous) => {
  if (previous && !current) isExpanded.value = false
})

// 按工具名选择渲染组件，未匹配时使用默认展示。
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
const toolRenderer = computed(() => toolRenderers[(props.content.name || '').toLowerCase()])
</script>

<template>
  <component
    v-if="toolRenderer"
    :is="toolRenderer"
    :content="content"
    :loading="loading"
    v-model:expanded="isExpanded"
    @toggle="isExpanded = !isExpanded"
  />
  <DefaultTool v-else :content="content" />
</template>
