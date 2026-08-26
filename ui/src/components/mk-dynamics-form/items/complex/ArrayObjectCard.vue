<script setup lang="ts">
import type { MkDynamicFormValue } from '../../type'
import { computed, ref } from 'vue'
import type { DynamicFormResponse, FormField } from '../../type'
import DynamicsForm from '../../index.vue'
const props = defineProps<{
  modelValue?: Array<MkDynamicFormValue>
  formValue?: MkDynamicFormValue
  formfieldList?: Array<FormField>
  field: string
  otherParams: MkDynamicFormValue
  formField: FormField
  view?: boolean
}>()

const getChildFields = () => {
  return Promise.resolve({
    data: props.formField.children as Array<FormField>,
  } satisfies DynamicFormResponse<Array<FormField>>)
}
const deleteKnowledge = (item: MkDynamicFormValue) => {
  _data.value = _data.value.filter((row) => row !== item)
}
const emit = defineEmits(['update:modelValue', 'change'])

// 校验实例对象
const dynamicsFormRef = ref<Array<InstanceType<typeof DynamicsForm>>>([])

const _data = computed<Array<MkDynamicFormValue>>({
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

const props_info = computed(() => {
  return props.formField.props_info ? props.formField.props_info : {}
})
const add_msg = computed(() => {
  return props_info.value.add_msg ? props_info.value.add_msg : '添加'
})
/**
 * 添加一个card
 */
const add_card = () => {
  _data.value = [..._data.value, {}]
}

/**
 * 组件样式
 */
const formStyle = computed(() => {
  return props_info.value.form_style ? props_info.value.form_style : {}
})
const style = computed(() => {
  return props_info.value.style ? props_info.value.style : {}
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

defineExpose({
  validate,
  field: props.field,
})
</script>

<template v-loading="_loading">
  <div class="arrt-object-card flex w-full">
    <el-card class="box-card" :style="style" v-for="(item, index) in _data" :key="index">
      <DynamicsForm
        :style="formStyle"
        :view="view"
        ref="ceFormRef"
        v-model="_data[index]"
        :model="_data[index]"
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
    <el-card shadow="never" class="card-add box-card" @click="add_card">
      <div class="flex-center">
        <MkIcon name="icon_add_outlined" class="add-icon layout-bg p-8 border-r-6" />
        <span>{{ add_msg }}</span>
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
