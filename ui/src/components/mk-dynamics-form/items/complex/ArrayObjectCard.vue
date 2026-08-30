<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, ref } from 'vue'
import type { DynamicFormResponse, FormField } from '../../type'
import DynamicsForm from '../../index.vue'
const props = defineProps<{
  modelValue?: DynamicFormValue[]
  formValue?: DynamicFormValue
  formfieldList?: FormField[]
  field: string
  otherParams: DynamicFormValue
  formField: FormField
  view?: boolean
}>()

const getChildFields = () => {
  return Promise.resolve({ data: props.formField.children as FormField[] } satisfies DynamicFormResponse<FormField[]>)
}
const deleteKnowledge = (item: DynamicFormValue) => {
  localValue.value = localValue.value.filter((row) => row !== item)
}
const emit = defineEmits(['update:modelValue', 'change'])

// 校验实例对象
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>[]>([])

const localValue = computed<DynamicFormValue[]>({
  get() {
    if (props.modelValue) {
      return props.modelValue
    } else {
      emit('update:modelValue', [{}])
      return []
    }
  },
  set(value) {
    emit('update:modelValue', value)
  },
})

const fieldProps = computed(() => {
  return props.formField.props_info ? props.formField.props_info : {}
})
const addMessage = computed(() => {
  return fieldProps.value.add_msg ? fieldProps.value.add_msg : '添加'
})
/**
 * 添加一个card
 */
const addCard = () => {
  localValue.value = [...localValue.value, {}]
}

/**
 * 组件样式
 */
const formStyle = computed(() => {
  return fieldProps.value.form_style ? fieldProps.value.form_style : {}
})
const style = computed(() => {
  return fieldProps.value.style ? fieldProps.value.style : {}
})
const attr = computed(() => {
  if (props.formField.attrs) {
    return props.formField.attrs
  }
  return {}
})

/**
 * 校验方法
 */
function validate() {
  return Promise.all(dynamicsFormRef.value.map((item) => item.validate()))
}
const other = computed(() => {
  return { ...(props.formValue ? props.formValue : {}), ...props.otherParams }
})

defineExpose({ validate, field: props.field })
</script>

<template v-loading="_loading">
  <div class="arrt-object-card flex w-full">
    <el-card class="box-card" :style="style" v-for="(item, index) in localValue" :key="index">
      <DynamicsForm
        :style="formStyle"
        :view="view"
        ref="ceFormRef"
        v-model="localValue[index]"
        :model="localValue[index]"
        :other-params="other"
        :render-data="getChildFields()"
        v-bind="attr"
        :parent-field="formField.field + '.' + index"
        label-position="top"
        require-asterisk-position="right"
      ></DynamicsForm>
      <el-tooltip effect="dark" content="删除" placement="top">
        <el-button text @click.stop="deleteKnowledge(item)" class="delete-button">
          <MkIcon name="icon_delete-trash_outlined"></MkIcon>
        </el-button>
      </el-tooltip>
    </el-card>
    <el-card shadow="never" class="card-add box-card" @click="addCard">
      <div class="flex-center">
        <MkIcon name="icon_add_outlined" class="add-icon layout-bg p-8 border-r-6" />
        <span>{{ addMessage }}</span>
      </div>
    </el-card>
  </div>
</template>
<style lang="scss" scoped>
.arrt-object-card {
  .box-card {
    width: 30%;
    position: relative;
    margin: 10px;
    padding-top: 20px;
  }
  .card-add {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    font-size: 16px;
    cursor: pointer;
    min-height: var(--card-min-height);
    border: 1px dashed var(--el-color-primary);
    background: var(--el-disabled-bg-color);
    padding-bottom: 20px;

    .add-icon {
      font-size: 14px;
      border: 1px solid var(--app-border-color-dark);
      margin-right: 12px;
    }
    &:hover {
      color: var(--el-color-primary);
      background: #ffffff;
      .add-icon {
        background: #ffffff;
        border-color: var(--el-color-primary);
      }
    }
  }
  .delete-button {
    position: absolute;
    right: 12px;
    top: 10px;
    height: auto;
  }
}
</style>
