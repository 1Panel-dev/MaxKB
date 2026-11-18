<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

defineOptions({ name: 'LayoutBatchFooter' })
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ allSelected: boolean; selectedCount: number; total: number }>()

const emit = defineEmits<{ cancel: []; 'select-all': [selected: boolean] }>()

defineSlots<{ default?: () => unknown }>()

const isIndeterminate = computed(() => props.selectedCount > 0 && !props.allSelected)

function handleSelectAllChange(selected: boolean | string | number) {
  emit('select-all', Boolean(selected))
}
</script>

<template>
  <footer class="flex-align-center shrink-0 border-t bg-white px-6 py-4">
    <div class="mr-4 flex-align-center gap-3">
      <el-checkbox :indeterminate="isIndeterminate" :model-value="allSelected" @change="handleSelectAllChange" />
      <span>{{ t('common.labels.selected') }} {{ selectedCount }}/{{ total }}</span>
    </div>

    <slot />
    <!-- 取消批量选择 -->
    <el-button text type="primary" class="ml-3! shrink-0" @click="emit('cancel')">{{ t('common.actions.cancel') }}</el-button>
  </footer>
</template>
