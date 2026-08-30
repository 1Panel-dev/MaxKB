<script setup lang="ts" generic="T">
defineOptions({ name: 'MkFormList' })

const props = withDefaults(defineProps<{ addText?: string; defaultItem: T; firstRowHasLabel?: boolean; showAddButton?: boolean }>(), {
  addText: '添加',
  firstRowHasLabel: true,
  showAddButton: true,
})
const formRows = defineModel<T[]>({ required: true })

const emit = defineEmits<{ remove: [item: T, index: number] }>()

defineSlots<{ default(props: { index: number; item: T }): unknown }>()

function addRow() {
  formRows.value = [...formRows.value, props.defaultItem]
}

function removeRow(index: number) {
  if (formRows.value.length === 1) return
  const removedItem = formRows.value[index] as T
  formRows.value = formRows.value.filter((_, rowIndex) => rowIndex !== index)
  emit('remove', removedItem, index)
}
</script>

<template>
  <div v-for="(item, index) in formRows" :key="index" class="flex w-full gap-2">
    <slot :index="index" :item="item" />
    <el-form-item class="shrink-0" :class="firstRowHasLabel ? (index === 0 ? 'mt-8' : 'mt-0.5') : '-mt-4'">
      <el-button :disabled="formRows.length === 1" text @click="removeRow(index)">
        <MkIcon name="icon_delete-trash_outlined" class="text-N600" />
      </el-button>
    </el-form-item>
  </div>

  <el-button v-if="showAddButton" class="-mt-1 mb-6" link type="primary" @click="addRow">
    <MkIcon name="icon_add_outlined" />
    <span>{{ addText }}</span>
  </el-button>
</template>
