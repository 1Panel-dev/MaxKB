<template>
  <div style="width: 1024px">
    <DynamicsForm v-model="form_data" :render_data="damo_data" ref="dynamicsFormRef">
      <template #default="scope">
        <el-form-item label="其他字段">
          <el-input v-model="scope.form_value['zha']" /> </el-form-item
      ></template>
    </DynamicsForm>
    <el-button @click="click">点我校验</el-button>
  </div>
</template>
<script setup lang="ts">
import type { FormField } from '@/components/dynamics-form/type'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import { ref } from 'vue'
import type { Dict } from '@/api/type/common'
const damo_data: Array<FormField> = [
  { field: 'name', input_type: 'PasswordInput', label: '用戶名', required: false },
  {
    field: 'array_object_card_field',
    input_type: 'ArrayObjectCard',
    label: '測試',
    trigger_type: 'CHILD_FORMS',
    attrs: { 'label-width': '120px', 'label-suffix': ':ssss', 'label-position': 'top' },
    required: false,
    children: [
      { field: 'name1', input_type: 'TextInput', label: '用戶名1' },
      { field: 'name2', input_type: 'TextInput', label: '用戶名2' },
      { field: 'name3', input_type: 'TextInput', label: '用戶名3' }
    ]
  },
  {
    field: 'object_card_field',
    input_type: 'ObjectCard',
    label: '測試',
    trigger_type: 'CHILD_FORMS',
    attrs: { 'label-width': '120px', 'label-suffix': ':ssss', 'label-position': 'left' },
    required: false,
    children: [
      { field: 'name1', input_type: 'TextInput', label: '用戶名1' },
      { field: 'name2', input_type: 'TextInput', label: '用戶名2' },
      { field: 'name3', input_type: 'TextInput', label: '用戶名3' }
    ]
  },
  {
    field: 'tab_card_field',
    input_type: 'TabCard',
    label: '測試',
    trigger_type: 'CHILD_FORMS',
    attrs: { 'label-width': '120px', 'label-suffix': ':ssss', 'label-position': 'left' },
    required: false,
    relation_trigger_field_dict: {
      'array_object_card_field.0.name1': ['111']
    },
    props_info: { tabs_label: '用户' },
    children: [
      { field: 'name1', input_type: 'TextInput', label: '用戶名1' },
      { field: 'name2', input_type: 'TextInput', label: '用戶名2' },
      { field: 'name3', input_type: 'TextInput', label: '用戶名3' }
    ]
  },
  {
    field: 'single_select_field',
    input_type: 'SingleSelect',
    label: '测试单选',
    required: true,
    attrs: { placeholder: '请选择' },
    option_list: [
      {
        key: '测试',
        value: 'test'
      },
      {
        key: '测试1',
        value: 'test1'
      }
    ]
  },
  {
    field: 'multi_select_field',
    input_type: 'MultiSelect',
    default_value: ['test1'],
    relation_show_field_dict: {
      'object_card_field.name1': []
    },
    label: '测试多选下拉',
    required: true,
    attrs: { placeholder: '请选择' },
    option_list: [
      {
        key: '测试',
        value: 'test'
      },
      {
        key: '测试1',
        value: 'test1'
      }
    ]
  },
  {
    field: 'radio_field',
    input_type: 'Radio',
    label: '测试单选',
    required: true,
    attrs: { placeholder: '请选择' },
    option_list: [
      {
        key: '测试',
        value: 'test'
      },
      {
        key: '测试1',
        value: 'test1'
      }
    ]
  },
  {
    field: 'radio_button_field',
    input_type: 'RadioButton',
    label: '测试单选',
    required: true,
    attrs: { placeholder: '请选择' },
    option_list: [
      {
        key: '测试',
        value: 'test'
      },
      {
        key: '测试1',
        value: 'test1'
      }
    ]
  },
  {
    field: 'radio_card_field',
    input_type: 'RadioCard',
    label: '测试单选1',
    required: true,
    attrs: { placeholder: '请选择' },
    option_list: [
      {
        key: '测试',
        value: 'test'
      },
      {
        key: '测试111111',
        value: 'test1'
      }
    ]
  },
  {
    field: 'table_radio_field',
    input_type: 'TableRadio',
    label: '表格单选',
    required: true,
    attrs: { placeholder: '请选择' },
    props_info: {
      active_msg: '当前选中',
      table_columns: [
        {
          property: '`${row.key}${row.number}`',
          label: '名称',
          type: 'eval'
        },
        {
          property: 'ProgressTableItem',
          label: '数值',
          type: 'component',
          value_field: 'number',
          attrs: {
            color: [
              { color: '#f56c6c', percentage: 20 },
              { color: '#e6a23c', percentage: 40 },
              { color: '#5cb87a', percentage: 60 },
              { color: '#1989fa', percentage: 80 },
              { color: '#6f7ad3', percentage: 100 }
            ]
          },
          props_info: {
            view_card: [
              {
                type: 'eval',
                title: '测试',
                value_field:
                  '`${parseFloat(row.number).toLocaleString("zh-CN",{style: "decimal",maximumFractionDigits:1})}%&nbsp;&nbsp;&nbsp;`'
              },
              {
                type: 'eval',
                title: '名称',
                value_field: '`${row.key}&nbsp;&nbsp;&nbsp;`'
              }
            ]
          }
        }
      ],
      style: { width: '500px' }
    },
    option_list: [
      {
        key: '测试',
        value: 'test',
        number: 10
      },
      {
        key: '测试111111',
        value: 'test1',
        number: 100
      }
    ]
  },
  {
    field: 'table_checkbox_field',
    input_type: 'TableCheckbox',
    label: '表格多选',
    required: true,
    attrs: { placeholder: '请选择' },
    props_info: {
      active_msg: '当前选中',
      table_columns: [
        {
          property: '`${row.key}${row.number}`',
          label: '名称',
          type: 'eval'
        },
        {
          property: 'ProgressTableItem',
          label: '数值',
          type: 'component',
          value_field: 'number',
          attrs: {
            color: [
              { color: '#f56c6c', percentage: 20 },
              { color: '#e6a23c', percentage: 40 },
              { color: '#5cb87a', percentage: 60 },
              { color: '#1989fa', percentage: 80 },
              { color: '#6f7ad3', percentage: 100 }
            ]
          },
          props_info: {
            view_card: [
              {
                type: 'eval',
                title: '测试',
                value_field:
                  '`${parseFloat(row.number).toLocaleString("zh-CN",{style: "decimal",maximumFractionDigits:1})}%&nbsp;&nbsp;&nbsp;`'
              },
              {
                type: 'eval',
                title: '名称',
                value_field: '`${row.key}&nbsp;&nbsp;&nbsp;`'
              }
            ]
          }
        }
      ],
      style: { width: '500px' }
    },
    option_list: [
      {
        key: '测试',
        value: 'test',
        number: 10
      },
      {
        key: '测试111111',
        value: 'test1',
        number: 100
      }
    ]
  }
]
const form_data = ref<Dict<any>>({})
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const click = () => {
  dynamicsFormRef.value?.validate()
}
</script>
<style lang="scss" scope></style>
