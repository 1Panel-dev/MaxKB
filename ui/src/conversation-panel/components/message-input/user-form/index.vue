<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { MkDynamicsForm } from '@/components/mk-dynamics-form'
import type { DynamicFormValue, FormField } from '@/components/mk-dynamics-form'
import type { Dict } from '@/api/types'
import { MsgWarning } from '@/utils/message'
import { useMessageInputStore } from '../index'

defineOptions({ name: 'ConversationUserForm' })

// 行内字段按类型固定宽度，按容器宽度计算能展示的数量，其余收进弹出层
const INLINE_FIELD_WIDTH = 140
// 模型选择包含供应商图标和参数按钮，需要更宽
const INLINE_MODEL_FIELD_WIDTH = 200
// 开关带边框和标签，按标签字数估算宽度：左右内边距与边框 26px、开关 40px、间距 8px
const INLINE_SWITCH_EXTRA_WIDTH = 74
const INLINE_SWITCH_CHAR_WIDTH = 14
// 开关标签最大宽度，超出省略，悬停显示原文
const INLINE_SWITCH_LABEL_MAX_WIDTH = 56
const INLINE_GAP = 8
const MORE_BUTTON_WIDTH = 32

const { userForm } = useMessageInputStore()
const { formData, apiFormData, userInputFields, apiInputFields, exposedFieldNames, menuTitle, hasFields, apiInputEditable } = userForm

const route = useRoute()
const accessToken = typeof route.params.accessToken === 'string' ? route.params.accessToken : ''
const storageKey = accessToken ? `${accessToken}userForm` : ''

const inlineFormRef = ref<InstanceType<typeof MkDynamicsForm>>()
const popoverFormRef = ref<InstanceType<typeof MkDynamicsForm>>()
const apiFormRef = ref<InstanceType<typeof MkDynamicsForm>>()
const moreButtonRef = ref<{ $el: HTMLElement }>()
const moreButtonEl = computed(() => moreButtonRef.value?.$el)
const popoverVisible = ref(false)

// ===== 自适应：按宽度决定行内字段 =====
const containerRef = ref<HTMLElement>()
const containerWidth = ref(0)
let resizeObserver: ResizeObserver | null = null

// 模型下拉挂载到 body，避免被输入框和弹出层的滚动容器裁剪
const displayFields = computed(() =>
  userInputFields.value.map((field) => (field.input_type === 'Model' ? { ...field, attrs: { teleported: true, ...field.attrs } } : field)),
)

const exposedFields = computed(() =>
  exposedFieldNames.value.map((fieldName) => displayFields.value.find((field) => field.field === fieldName)).filter((field) => !!field),
)

function getFieldLabel(field: FormField) {
  return typeof field.label === 'string' ? field.label : field.label?.label || field.field
}

function getInlineFieldWidth(field: FormField) {
  if (field.input_type === 'Model') return INLINE_MODEL_FIELD_WIDTH
  if (field.input_type === 'SwitchInput') {
    return Math.min(INLINE_SWITCH_LABEL_MAX_WIDTH, getFieldLabel(field).length * INLINE_SWITCH_CHAR_WIDTH) + INLINE_SWITCH_EXTRA_WIDTH
  }
  return INLINE_FIELD_WIDTH
}

/** 按顺序累加字段宽度，返回能放下的字段数量。 */
function getFitCount(width: number) {
  let usedWidth = -INLINE_GAP
  let fitCount = 0
  for (const field of exposedFields.value) {
    usedWidth += getInlineFieldWidth(field) + INLINE_GAP
    if (usedWidth > width) break
    fitCount++
  }
  return fitCount
}

const inlineCount = computed(() => {
  const allFit = getFitCount(containerWidth.value)
  const needsMore = allFit < userInputFields.value.length || (apiInputEditable && apiInputFields.value.length > 0)
  return needsMore ? getFitCount(containerWidth.value - MORE_BUTTON_WIDTH - INLINE_GAP) : allFit
})

/** 行内字段不展示表单标签：开关将标签放在框内左侧，其他字段以标签作为占位提示；校验结果统一用消息提示。 */
const inlineFields = computed<FormField[]>(() =>
  exposedFields.value.slice(0, inlineCount.value).map((field) => {
    const label = getFieldLabel(field)
    return {
      ...field,
      label: undefined,
      attrs:
        field.input_type === 'SwitchInput'
          ? { ...field.attrs, class: 'mk-conversation-user-form__switch', 'inactive-text': label, title: label }
          : { placeholder: label, ...field.attrs },
      props_info: { ...field.props_info, style: { width: `${getInlineFieldWidth(field)}px` }, item_style: { margin: 0 } },
    }
  }),
)
const popoverFields = computed(() => {
  const inlineFieldNames = new Set(inlineFields.value.map((field) => field.field))
  return displayFields.value.filter((field) => !inlineFieldNames.has(field.field))
})
const showMoreButton = computed(() => popoverFields.value.length > 0 || (apiInputEditable && apiInputFields.value.length > 0))

// MkDynamicsForm 只在挂载时读取 renderData，字段分组变化后通过 key 重建
const formRefreshKey = ref(0)
watch([inlineFields, popoverFields, apiInputFields], () => formRefreshKey.value++)

// ===== 地址栏参数 =====
function decodeQuery(query: string) {
  try {
    return decodeURIComponent(query)
  } catch {
    return query
  }
}

function getRouteQueryValue(field: string) {
  const queryValue = route.query[field]
  if (queryValue == null) return null
  if (Array.isArray(queryValue)) {
    return queryValue.filter((value): value is string => value != null).map(decodeQuery)
  }
  return decodeQuery(queryValue)
}

/** 接口传参未赋值时，从地址栏同名参数回填；同时回填提问人 asker。 */
function initRouteQueryValue() {
  const queryValues: Dict<DynamicFormValue> = {}
  for (const field of [...apiInputFields.value.map((apiField) => apiField.field), 'asker']) {
    if (apiFormData.value[field]) continue
    const queryValue = getRouteQueryValue(field)
    if (queryValue) queryValues[field] = queryValue
  }
  if (Object.keys(queryValues).length) {
    apiFormData.value = { ...apiFormData.value, ...queryValues }
  }
}

// ===== 校验 =====
/** 非调试场景接口传参只能来自地址栏，缺少必填参数时提示补充。 */
function validateApiQuery() {
  if (apiInputEditable) return Promise.resolve()
  const missingFields = apiInputFields.value.filter((field) => field.required && !apiFormData.value[field.field]).map((field) => field.field)
  if (missingFields.length) {
    MsgWarning(`请在URL中填写参数 ${missingFields.join('、')}的值`)
    return Promise.reject(false)
  }
  return Promise.resolve()
}

function validateInlineForm() {
  return (inlineFormRef.value?.validate() ?? Promise.resolve()).catch((error: unknown) => {
    const invalidFields = error && typeof error === 'object' ? Object.values(error as Dict<{ message?: string }[]>) : []
    const message = invalidFields[0]?.[0]?.message
    if (message) MsgWarning(message)
    throw error
  })
}

function validatePopoverForm() {
  return Promise.all([popoverFormRef.value?.validate(), apiFormRef.value?.validate()]).catch((error: unknown) => {
    // 弹出层内字段校验失败时打开弹出层展示错误
    popoverVisible.value = true
    throw error
  })
}

function saveFormData() {
  if (storageKey) localStorage.setItem(storageKey, JSON.stringify(formData.value))
}

/** 发送前校验全部参数，通过后保存用户输入。 */
function validate() {
  return validateInlineForm().then(validatePopoverForm).then(validateApiQuery).then(saveFormData)
}

// ===== 弹出层操作 =====
function confirmHandle() {
  validatePopoverForm().then(() => {
    saveFormData()
    popoverVisible.value = false
  })
}

function cancelHandle() {
  userForm.restoreSnapshot()
  formRefreshKey.value++
  popoverVisible.value = false
}

// ===== 生命周期 =====
let unbindValidator: (() => void) | null = null

onMounted(() => {
  if (storageKey && !Object.keys(formData.value).length) {
    try {
      formData.value = JSON.parse(localStorage.getItem(storageKey) || '{}')
    } catch {
      formData.value = {}
    }
  }
  initRouteQueryValue()
  unbindValidator = userForm.bindValidator(validate)

  if (containerRef.value) {
    resizeObserver = new ResizeObserver(([entry]) => {
      if (entry) containerWidth.value = entry.contentRect.width
    })
    resizeObserver.observe(containerRef.value)
  }
})

onBeforeUnmount(() => {
  unbindValidator?.()
  resizeObserver?.disconnect()
})
</script>

<template>
  <div ref="containerRef" class="mk-conversation-user-form flex min-w-0 flex-1 items-center gap-2 overflow-hidden">
    <template v-if="hasFields">
      <MkDynamicsForm
        v-if="inlineFields.length"
        :key="`inline-${formRefreshKey}`"
        ref="inlineFormRef"
        v-model="formData"
        :render-data="inlineFields"
        inline
        :show-message="false"
        class="flex items-center gap-2"
      />

      <!-- 打开更多参数 -->
      <el-button v-if="showMoreButton" ref="moreButtonRef" class="size-8! min-w-0! px-0!" @click="popoverVisible = !popoverVisible">
        <MkIcon name="icon_setting" :size="16" />
      </el-button>

      <el-popover
        v-if="showMoreButton"
        :visible="popoverVisible"
        :virtual-ref="moreButtonEl"
        virtual-triggering
        trigger="manual"
        placement="top-start"
        :width="400"
        :popper-style="{ padding: '16px 8px' }"
        @show="userForm.saveSnapshot"
      >
        <div class="mb-4 truncate break-all font-medium" :title="menuTitle">{{ menuTitle }}</div>
        <el-scrollbar max-height="450px">
          <MkDynamicsForm :key="`popover-${formRefreshKey}`" ref="popoverFormRef" v-model="formData" :render-data="popoverFields" />
          <MkDynamicsForm
            v-if="apiInputEditable"
            :key="`api-${formRefreshKey}`"
            ref="apiFormRef"
            v-model="apiFormData"
            :render-data="apiInputFields"
          />
        </el-scrollbar>
        <div class="mt-2 text-right">
          <!-- 取消修改 -->
          <el-button @click="cancelHandle">取消</el-button>
          <!-- 确认参数 -->
          <el-button type="primary" @click="confirmHandle">确认</el-button>
        </div>
      </el-popover>
    </template>
  </div>
</template>

<style scoped lang="scss">
/* 行内开关与下拉框同高同边框（主题将开关高度改为 22px），标签固定为常规文字色，不随开关状态高亮。 */
:deep(.mk-conversation-user-form__switch) {
  box-sizing: border-box;
  height: var(--el-component-size);
  justify-content: space-between;
  padding: 0 12px;
  border: 1px solid var(--el-border-color);
  border-radius: var(--el-border-radius-base);

  .el-switch__label {
    min-width: 0;
    max-width: 56px;
    margin-right: 8px;
    color: var(--el-text-color-regular);

    span {
      display: block;
      line-height: 20px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
}
</style>
