<script setup lang="ts">
import { computed, ref } from 'vue'
import type { CheckboxValueType } from 'element-plus'
import type { OptionItem } from '@/api/types'

defineOptions({ name: 'MkTableFilter' })

const props = defineProps<{ label: string; options: OptionItem<string>[] }>()
const emit = defineEmits<{ change: [values: string[]] }>()
const selectedValues = defineModel<string[]>({ required: true })

const visible = ref(false)
const pendingValues = ref<string[]>([])
const allOptionValues = computed(() => props.options.map(({ value }) => value))
const allSelected = computed(() => allOptionValues.value.length > 0 && pendingValues.value.length === allOptionValues.value.length)
const selectionIndeterminate = computed(() => pendingValues.value.length > 0 && !allSelected.value)

function handleOpen() {
  pendingValues.value = [...selectedValues.value]
}

function handleSelectAllChange(checked: CheckboxValueType) {
  pendingValues.value = checked ? [...allOptionValues.value] : []
}

function handleReset() {
  pendingValues.value = []
  selectedValues.value = []
  visible.value = false
  emit('change', [])
}

function handleConfirm() {
  selectedValues.value = [...pendingValues.value]
  visible.value = false
  emit('change', selectedValues.value)
}
</script>

<template>
  <el-popover v-model:visible="visible" placement="bottom-start" trigger="click" width="192" @before-enter="handleOpen">
    <template #reference>
      <el-button text>
        <span class="mr-1 font-semibold">{{ label }}</span>
        <MkIcon name="icon-filter" :class="selectedValues.length ? 'text-primary!' : 'text-N600'" />
      </el-button>
    </template>

    <el-scrollbar max-height="280px">
      <div class="flex flex-col gap-2 p-3 pb-0">
        <el-checkbox :indeterminate="selectionIndeterminate" :model-value="allSelected" class="mr-0!" @change="handleSelectAllChange"> 全部 </el-checkbox>
        <el-checkbox-group v-model="pendingValues" class="flex flex-col gap-2">
          <el-checkbox v-for="option in options" :key="option.value" :value="option.value" class="mk-table-filter__option mr-0! w-full min-w-0">
            <span class="block min-w-0 truncate" :title="option.label">{{ option.label }}</span>
          </el-checkbox>
        </el-checkbox-group>
      </div>
    </el-scrollbar>

    <div class="p-3 text-right">
      <el-button class="min-w-12! w-12!" size="small" @click="handleReset">重置</el-button>
      <el-button class="min-w-12! w-12!" :disabled="pendingValues.length === 0" size="small" type="primary" @click="handleConfirm"> 确定 </el-button>
    </div>
  </el-popover>
</template>

<style scoped lang="scss">
.mk-table-filter__option {
  :deep(.el-checkbox__label) {
    min-width: 0;
    overflow: hidden;
  }
}
</style>
