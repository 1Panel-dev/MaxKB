<script setup lang="ts">
import { computed, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'

defineOptions({ name: 'MkFilterableDropdown' })

type DropdownValue = string | number

interface DropdownOption {
  label: string
  value: DropdownValue
}

const props = withDefaults(
  defineProps<{
    options: DropdownOption[]
    placeholder?: string
    searchPlaceholder?: string
    emptyText?: string
  }>(),
  {
    placeholder: '请选择',
    searchPlaceholder: '搜索',
    emptyText: '暂无匹配结果',
  },
)

const model = defineModel<DropdownValue>({ required: true })
const keyword = ref('')

const selectedOption = computed(() => props.options.find((option) => option.value === model.value))

const filteredOptions = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLocaleLowerCase()
  if (!normalizedKeyword) return props.options

  return props.options.filter((option) =>
    option.label.toLocaleLowerCase().includes(normalizedKeyword),
  )
})

defineSlots<{
  /** 下拉框触发器，由使用方决定按钮结构和样式 */
  default(props: { selectedOption?: DropdownOption; text: string }): unknown
  /** 菜单项左侧图标 */
  itemIcon?(props: { option: DropdownOption }): unknown
}>()

function handleVisibleChange(visible: boolean) {
  if (!visible) keyword.value = ''
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
      <div class="w-70">
        <div class="p-2 pb-1" @click.stop @keydown.stop>
          <el-input
            v-model="keyword"
            :prefix-icon="Search"
            :placeholder="searchPlaceholder"
            clearable
          />
        </div>

        <el-scrollbar max-height="160px">
          <MkDropdownMenu>
            <MkDropdownItem
              v-for="option in filteredOptions"
              :key="option.value"
              selectable
              :selected="option.value === model"
              @click="model = option.value"
            >
              <template v-if="$slots.itemIcon" #icon>
                <slot name="itemIcon" :option="option" />
              </template>
              {{ option.label }}
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
