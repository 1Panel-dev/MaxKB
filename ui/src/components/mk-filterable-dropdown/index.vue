<script setup lang="ts" generic="Option extends { label: string; value: string | number }">
import { computed, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'

/**
 * 带搜索过滤和滚动列表的下拉选择组件。
 * 使用 v-model 传入当前选中值，使用 options 传入菜单数据；
 * 触发器由默认插槽定义，菜单项内容由 option 插槽定义。
 */
defineOptions({ name: 'MkFilterableDropdown' })

type DropdownValue = string | number

const props = withDefaults(
  defineProps<{
    /** 下拉菜单数据 */
    options: Option[]
    /** 未选中数据时触发器显示的文字 */
    placeholder?: string
    /** 搜索输入框的占位文字 */
    searchPlaceholder?: string
    /** 没有匹配结果时显示的文字 */
    emptyText?: string
  }>(),
  {
    placeholder: '请选择',
    searchPlaceholder: '搜索',
    emptyText: '暂无匹配结果',
  },
)

/** 当前选中菜单项的 value */
const selectedValue = defineModel<DropdownValue>({ required: true })
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
  default(props: { selectedOption?: Option; text: string }): unknown
  /** 菜单项内容，接收当前 option；未传入时显示 option.label */
  option?(props: { option: Option }): unknown
}>()

function handleVisibleChange(visible: boolean) {
  if (!visible) searchKeyword.value = ''
}
</script>

<template>
  <MkDropdown
    class="mk-filterable-dropdown"
    trigger="click"
    placement="bottom-start"
    @visible-change="handleVisibleChange"
  >
    <slot :selected-option="selectedOption" :text="selectedOption?.label ?? placeholder" />

    <template #dropdown>
      <div class="w-70 overflow-hidden rounded-md">
        <div class="p-2 pb-1" @click.stop @keydown.stop>
          <el-input
            v-model="searchKeyword"
            :prefix-icon="Search"
            :placeholder="searchPlaceholder"
            clearable
          />
        </div>

        <el-scrollbar max-height="200px">
          <MkDropdownMenu>
            <MkDropdownItem
              v-for="option in filteredOptions"
              :key="option.value"
              selectable
              :selected="option.value === selectedValue"
              @click="selectedValue = option.value"
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
