<template>
  <component
    v-if="toolRenderers[toolName]"
    :is="toolRenderers[toolName]"
    :content="content"
    :loading="loading"
    :expanded="isExpanded"
    @toggle="isExpanded = !isExpanded"
  />
  <DefaultTool v-else :content="content" />
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
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

/** TOOL 内容项按工具名分发到专用渲染器，未匹配的工具沿用原有 tool.vue 展示。 */
const props = defineProps<{ content: any }>()

const loading = computed(() => props.content.status === 'RUNNING')
const toolName = computed(() => (props.content.name || '').toLowerCase())
const isExpanded = ref(props.content.status === 'RUNNING')

// 工具执行完成自动收起
watch(loading, (current, previous) => {
  if (previous && !current) isExpanded.value = false
})

const toolRenderers: Record<string, any> = {
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
</script>
