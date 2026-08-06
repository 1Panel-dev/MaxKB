<script setup lang="ts">
import { computed, ref } from 'vue'
import type { OptionItem } from '@/types'

/**
 * 带搜索过滤和滚动列表的下拉选择组件。
 * 使用 v-model 传入当前选中值，使用 options 传入菜单数据；
 * 触发器由默认插槽定义，菜单项内容由 option 插槽定义。
 */
defineOptions({ name: 'MkFilterableDropdown' })

const props = withDefaults(
  defineProps<{
    /** 下拉菜单数据 */
    options: OptionItem[]
    /** 没有匹配结果时显示的文字 */
    emptyText?: string
  }>(),
  {
    emptyText: '暂无匹配结果',
  },
)

/** 当前选中菜单项的 value */
const selectedValue = defineModel<string | number>({ required: true })
const emit = defineEmits<{
  select: [option: OptionItem]
}>()
const searchKeyword = ref('')

const selectedOption = computed(() =>
  props.options.find((option) => option.value === selectedValue.value),
)

const filteredOptions = computed(() => {
  const normalizedKeyword = searchKeyword.value.trim().toLocaleLowerCase()
  if (!normalizedKeyword) return props.options

  return props.options.filter((option) =>
    option.label.toLocaleLowerCase().includes(normalizedKeyword),
  )
})

defineSlots<{
  /** 下拉框触发器，由使用方决定按钮结构和样式 */
  default(props: { selectedOption?: OptionItem; text: string }): unknown
  /** 菜单项内容，接收当前 option；未传入时显示 option.label */
  option?(props: { option: OptionItem }): unknown
}>()

function handleVisibleChange(visible: boolean) {
  if (!visible) searchKeyword.value = ''
}

function handleItemClick(option: OptionItem) {
  selectedValue.value = option.value
  emit('select', option)
}
</script>

<template>
  <MkDropdown
    class="mk-filterable-dropdown"
    trigger="click"
    placement="bottom-start"
    @visible-change="handleVisibleChange"
  >
    <slot :selected-option="selectedOption" :text="selectedOption?.label ?? ''" />

    <template #dropdown>
      <div class="w-70 overflow-hidden rounded-md">
        <div class="p-2 pb-1" @click.stop @keydown.stop>
          <MkSearchInput v-model="searchKeyword" />
        </div>

        <el-scrollbar max-height="200px">
          <MkDropdownMenu>
            <MkDropdownItem
              v-for="option in filteredOptions"
              :key="option.value"
              selectable
              :selected="option.value === selectedValue"
              @click="handleItemClick(option)"
            >
              <slot name="option" :option="option">
                <span class="block truncate">{{ option.label }}</span>
              </slot>
            </MkDropdownItem>

            <MkDropdownItem v-if="filteredOptions.length === 0" disabled>
              <span class="text-N600">{{ emptyText }}</span>
            </MkDropdownItem>
          </MkDropdownMenu>
        </el-scrollbar>
      </div>
    </template>
  </MkDropdown>
</template>
