<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ResourceOption } from '../../types'

defineOptions({ name: 'AiChatNodeResourceSelectionDialog' })

const props = withDefaults(defineProps<{ application?: boolean; options: ResourceOption[]; title: string }>(), { application: false })
const emit = defineEmits<{ submit: [ids: string[]] }>()

const visible = ref(false)
const keyword = ref('')
const selectedIds = ref<string[]>([])

const filteredOptions = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLocaleLowerCase()
  if (!normalizedKeyword) return props.options
  return props.options.filter(({ desc, name }) => `${name} ${desc ?? ''}`.toLocaleLowerCase().includes(normalizedKeyword))
})

function open(ids: string[]) {
  selectedIds.value = [...ids]
  keyword.value = ''
  visible.value = true
}

function submit() {
  emit('submit', [...selectedIds.value])
  visible.value = false
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="title" width="680">
    <el-input v-model="keyword" class="mb-3" clearable placeholder="搜索名称或描述">
      <template #prefix><MkIcon name="icon_search" /></template>
    </el-input>

    <el-scrollbar height="420px">
      <el-checkbox-group v-if="filteredOptions.length" v-model="selectedIds" class="grid grid-cols-2 gap-2 pr-2">
        <el-checkbox
          v-for="option in filteredOptions"
          :key="option.id"
          :label="option.id"
          class="m-0! h-auto! w-full rounded-md border border-N200 p-3!"
        >
          <div class="flex min-w-0 items-center gap-2">
            <ApplicationIcon v-if="application" :icon="option.icon" :size="28" />
            <ToolIcon v-else :icon="option.icon" :size="28" :type="'tool_type' in option ? option.tool_type : undefined" />
            <div class="min-w-0">
              <div class="truncate" :title="option.name">{{ option.name }}</div>
              <div v-if="option.desc" class="truncate text-sm text-N600" :title="option.desc">{{ option.desc }}</div>
            </div>
          </div>
        </el-checkbox>
      </el-checkbox-group>
      <MkEmpty v-else description="暂无可选资源" />
    </el-scrollbar>

    <template #footer>
      <span class="mr-auto text-N600">已选择 {{ selectedIds.length }} 项</span>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit">确定</el-button>
    </template>
  </MkDialog>
</template>
