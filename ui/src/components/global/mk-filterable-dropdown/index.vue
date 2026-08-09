<script setup lang="ts" generic="TOption extends object">
import { computed, ref } from 'vue'

/**
 * 带搜索过滤和滚动列表的下拉选择组件。
 * 使用 v-model 传入当前选中值，使用 options 传入菜单数据；
 * 触发器由默认插槽定义，菜单项内容由 option 插槽定义。
 */
defineOptions({ name: 'MkFilterableDropdown' })

const componentProps = withDefaults(
  defineProps<{
    /** 下拉菜单数据 */
    options: TOption[]
    /** 将业务数据的字段名映射为组件的展示字段和唯一值字段 */
    props?: {
      label?: keyof TOption & string
      value?: keyof TOption & string
    }
    /** 没有匹配结果时显示的文字 */
    emptyText?: string
  }>(),
  {
    emptyText: '暂无匹配结果',
    props: () => ({}),
  },
)

/** 当前选中菜单项的 value */
const selectedValue = defineModel<string | number>({ required: true })
const emit = defineEmits<{
  select: [option: TOption]
}>()
const searchKeyword = ref('')
const labelField = computed(() => componentProps.props.label ?? ('label' as keyof TOption & string))
const valueField = computed(() => componentProps.props.value ?? ('value' as keyof TOption & string))

function getOptionLabel(option: TOption) {
  return String(option[labelField.value] ?? '')
}

function getOptionValue(option: TOption) {
  const value = option[valueField.value]
  return typeof value === 'string' || typeof value === 'number' ? value : String(value ?? '')
}

const selectedOption = computed(() =>
  componentProps.options.find((option) => getOptionValue(option) === selectedValue.value),
)
const selectedText = computed(() =>
  selectedOption.value === undefined ? '' : getOptionLabel(selectedOption.value),
)

const filteredOptions = computed(() => {
  const normalizedKeyword = searchKeyword.value.trim().toLocaleLowerCase()
  if (!normalizedKeyword) return componentProps.options

  return componentProps.options.filter((option) =>
    getOptionLabel(option).toLocaleLowerCase().includes(normalizedKeyword),
  )
})

defineSlots<{
  /** 下拉框触发器，由使用方决定按钮结构和样式 */
  default(props: { selectedOption?: TOption; text: string }): unknown
  /** 菜单项内容，接收当前原始 option */
  option?(props: { option: TOption }): unknown
}>()

function handleVisibleChange(visible: boolean) {
  if (!visible) searchKeyword.value = ''
}

function handleItemClick(option: TOption) {
  selectedValue.value = getOptionValue(option)
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
    <slot :selected-option="selectedOption" :text="selectedText" />

    <template #dropdown>
      <div class="w-70 overflow-hidden rounded-md">
        <div class="p-2 pb-1" @click.stop @keydown.stop>
          <MkSearchInput v-model="searchKeyword" />
        </div>

        <el-scrollbar max-height="200px">
          <MkDropdownMenu>
            <MkDropdownItem
              v-for="option in filteredOptions"
              :key="getOptionValue(option)"
              selectable
              :selected="getOptionValue(option) === selectedValue"
              @click="handleItemClick(option)"
            >
              <slot name="option" :option="option">
                <span class="block truncate">{{ getOptionLabel(option) }}</span>
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
