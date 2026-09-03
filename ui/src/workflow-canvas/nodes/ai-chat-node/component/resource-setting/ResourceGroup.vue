<script setup lang="ts">
import { computed, ref } from 'vue'
import { CaretRight, Close, Plus } from '@element-plus/icons-vue'
import type { ResourceOption } from '../../types'

defineOptions({ name: 'AiChatNodeResourceGroup' })

const props = withDefaults(defineProps<{ application?: boolean; ids: string[]; label: string; options: ResourceOption[] }>(), { application: false })
const emit = defineEmits<{ add: []; remove: [id: string] }>()

const expanded = ref(true)
const selectedResources = computed(() => props.ids.map((id) => props.options.find((option) => option.id === id) ?? { id, name: `已选资源（${id}）` }))
</script>

<template>
  <div>
    <div class="flex-between cursor-pointer py-2" @click="expanded = !expanded">
      <span class="flex min-w-0 items-center gap-1 text-N600">
        <MkIcon :icon="CaretRight" class="transition-transform" :class="{ 'rotate-90': expanded }" />
        {{ label }}<span v-if="ids.length">（{{ ids.length }}）</span>
      </span>
      <el-button link type="primary" :title="`添加${label}`" @click.stop="emit('add')">
        <MkIcon :icon="Plus" />
      </el-button>
    </div>

    <div v-if="expanded && selectedResources.length" class="mb-2 flex flex-col gap-1">
      <div v-for="resource in selectedResources" :key="resource.id" class="flex-between rounded-md border border-N200 bg-white px-2 py-1.5">
        <span class="flex min-w-0 items-center gap-2">
          <ApplicationIcon v-if="application" :icon="resource.icon" :size="20" />
          <ToolIcon v-else :icon="resource.icon" :size="20" :type="'tool_type' in resource ? resource.tool_type : undefined" />
          <span class="truncate" :title="resource.name">{{ resource.name }}</span>
        </span>
        <el-button text title="移除" @click="emit('remove', resource.id)"><MkIcon :icon="Close" /></el-button>
      </div>
    </div>
  </div>
</template>
