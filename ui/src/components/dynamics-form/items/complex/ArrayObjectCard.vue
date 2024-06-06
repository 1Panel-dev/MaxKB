<template v-loading="_loading">
  <div class="arrt-object-card flex w-full">
    <el-card class="box-card" :style="style" v-for="(item, index) in _data" :key="index">
      <DynamicsForm
        :style="formStyle"
        :view="view"
        label-position="top"
        require-asterisk-position="right"
        ref="ceFormRef"
        v-model="_data[index]"
        :other-params="other"
        :render_data="render_data()"
        v-bind="attr"
        :parent_field="formField.field + '.' + index"
      ></DynamicsForm>
      <el-tooltip effect="dark" content="删除" placement="top">
        <el-button text @click.stop="deleteDataset(item)" class="delete-button">
          <el-icon><Delete /></el-icon>
        </el-button>
      </el-tooltip>
    </el-card>
    <el-card shadow="never" class="card-add box-card" @click="add_card">
      <div class="flex-center">
        <AppIcon iconName="Plus" class="add-icon layout-bg p-8 border-r-4" />
        <span>{{ add_msg }}</span>
      </div>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import _ from 'lodash'
import type { FormField } from '@/components/dynamics-form/type'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import Result from '@/request/Result'
const props = defineProps<{
  modelValue?: Array<any>
  formValue?: any
  formfieldList?: Array<FormField>
  field: string
  otherParams: any
  formField: FormField
  view?: boolean
}>()

const render_data = () => {
  return Promise.resolve(Result.success(props.formField.children as Array<FormField>))
}
const deleteDataset = (item: any) => {
  _data.value = _data.value.filter((row) => row !== item)
}
const emit = defineEmits(['update:modelValue', 'change'])

// 校验实例对象
const dynamicsFormRef = ref<Array<InstanceType<typeof DynamicsForm>>>([])

const _data = computed<Array<any>>({
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
  }
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
  field: props.field
})
</script>
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
    background: #eff0f1;
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
