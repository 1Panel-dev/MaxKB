<script setup lang="ts">
import { computed, onMounted, inject } from 'vue'
import RadioRow from '@/components/mk-dynamics-form/items/radio/RadioRow.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import type { FormField } from '@/components/mk-dynamics-form/type'
const getModel = inject('getModel') as any

const assignment_method_option_list = computed(() => {
  const option_list = [
    {
      label: '自定义',
      value: 'custom',
    },
  ]
  if (getModel) {
    option_list.push({
      label: '引用变量',
      value: 'ref_variables',
    })
  }
  return option_list
})

const model = computed(() => {
  if (getModel) {
    return getModel()
  } else {
    return null
  }
})
const props = defineProps<{
  modelValue: any
}>()
const emit = defineEmits(['update:modelValue'])
const formValue = computed({
  set: (item) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  },
})

const default_ref_variables_value_rule = {
  required: true,
  validator: (rule: any, value: any, callback: any) => {
    if (!(Array.isArray(value) && value.length > 1)) {
      callback('引用变量必填')
    }

    return true
  },
  trigger: 'blur',
}
const addOption = () => {
  formValue.value.option_list.push({ value: '', label: '' })
}

const delOption = (index: number) => {
  const option = formValue.value.option_list[index]
  if (option.value && formValue.value.default_value === option.value) {
    formValue.value.default_value = ''
  }
  formValue.value.option_list.splice(index, 1)
}
const formField = computed<FormField>(() => {
  return { field: '', ...getData() }
})
const getData = () => {
  return {
    input_type: 'RadioRow',
    attrs: {},
    default_value: formValue.value.default_value,
    text_field: 'label',
    value_field: 'value',
    option_list: formValue.value.option_list,
    assignment_method: formValue.value.assignment_method || 'custom',
  }
}
const render = (form_data: MkDynamicFormValue) => {
  formValue.value.option_list = form_data.option_list || []
  formValue.value.default_value = form_data.default_value
  formValue.value.assignment_method = form_data.assignment_method || 'custom'
}

defineExpose({ getData, render })
onMounted(() => {
  formValue.value.option_list = []
  formValue.value.default_value = ''
  formValue.value.assignment_method = 'custom'
  if (formValue.value.show_default_value === undefined) {
    formValue.value.show_default_value = true
  }
  addOption()
})
</script>

<template>
  <el-form-item v-if="getModel">
    <template #label>
      <div class="flex-between">赋值方式</div>
    </template>

    <el-row class="w-full">
      <el-radio-group @change="formValue.option_list = []" v-model="formValue.assignment_method">
        <el-radio
          :value="item.value"
          size="large"
          v-for="(item, index) in assignment_method_option_list"
          :key="index"
        >
          <span class="flex align-center">
            {{ item.label }}

            <el-tooltip effect="dark" placement="right" v-if="item.value === 'ref_variables'">
              <template #content>
                变量的值必须符合:<br />
                [<br />
                {<br />
                "label": "xx",<br />
                "value": "xx",<br />
                "default": false<br />
                }<br />
                ]<br />
                label: 标签 必填<br />
                value: 值 必填<br />
                default: 是否为默认值
              </template>
              <MkIcon name="icon_warning_filled" class="app-warning-icon ml-4"></MkIcon>
            </el-tooltip>
          </span>
        </el-radio>
      </el-radio-group>
    </el-row>
  </el-form-item>
  <el-form-item
    v-if="formValue.assignment_method === 'ref_variables'"
    :required="true"
    prop="option_list"
    :rules="[default_ref_variables_value_rule]"
  >
    <NodeCascader
      ref="nodeCascaderRef"
      :nodeModel="model"
      class="w-full"
      placeholder="请选择变量"
      v-model="formValue.option_list"
    />
  </el-form-item>
  <el-form-item v-if="formValue.assignment_method === 'custom'">
    <template #label>
      <div class="flex-between">
        选项值
        <el-button link type="primary" @click.stop="addOption()">
          <MkIcon name="icon_add_outlined" class="mr-4"></MkIcon>
          添加
        </el-button>
      </div>
    </template>

    <el-row style="width: 100%" :gutter="10">
      <el-col :span="10"> 标签 </el-col>
      <el-col :span="12"> 选项值 </el-col>
    </el-row>
    <el-row
      style="width: 100%"
      v-for="(option, $index) in formValue.option_list"
      :key="$index"
      :gutter="10"
      class="mb-8"
    >
      <el-col :span="10">
        <el-input v-model="formValue.option_list[$index].label" placeholder="请输入选项标签" />
      </el-col>
      <el-col :span="12">
        <el-input v-model="formValue.option_list[$index].value" placeholder="请输入选项值" />
      </el-col>
      <el-col :span="1">
        <el-button link class="ml-8" @click.stop="delOption(Number($index))">
          <MkIcon name="icon_delete-trash_outlined"></MkIcon>
        </el-button>
      </el-col>
    </el-row>
  </el-form-item>
  <el-form-item
    v-if="formValue.assignment_method === 'custom'"
    class="defaultValueItem"
    label="默认值"
    :required="formValue.required"
    prop="default_value"
    :rules="
      formValue.required
        ? [
            {
              required: true,
              message: '默认值为必填属性',
            },
          ]
        : []
    "
  >
    <div class="defaultValueCheckbox">
      <el-checkbox v-model="formValue.show_default_value" label="显示默认值" />
    </div>
    <RadioRow
      :form-field="formField"
      v-model="formValue.default_value"
      :other-params="{}"
      field="default_value"
    >
    </RadioRow>
  </el-form-item>
</template>
<style lang="scss" scoped>
.defaultValueItem {
  position: relative;
  .defaultValueCheckbox {
    position: absolute;
    right: 0;
    top: -35px;
  }
}
</style>
