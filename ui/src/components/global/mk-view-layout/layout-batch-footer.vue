<script setup lang="ts">
import { computed } from 'vue'

defineOptions({ name: 'LayoutBatchFooter' })

const props = defineProps<{ allSelected: boolean; selectedCount: number; total: number }>()

const emit = defineEmits<{ cancel: []; 'select-all': [selected: boolean] }>()

defineSlots<{ default?: () => unknown }>()

const isIndeterminate = computed(() => props.selectedCount > 0 && !props.allSelected)

function handleSelectAllChange(selected: boolean | string | number) {
  emit('select-all', Boolean(selected))
}
</script>

<template>
  <footer class="flex shrink-0 items-center border-t bg-white px-6 py-4">
    <div class="mr-4 flex items-center gap-3">
      <el-checkbox :indeterminate="isIndeterminate" :model-value="allSelected" @change="handleSelectAllChange" />
      <span>已选 {{ selectedCount }}/{{ total }}</span>
    </div>

    <slot />
    <el-button text type="primary" class="ml-3! shrink-0" @click="emit('cancel')"> 取消 </el-button>
  </footer>
</template>
