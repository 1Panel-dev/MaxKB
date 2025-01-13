export default {
  input_type_list: {
    TextInput: '文本框',
    Slider: '滑块',
    SwitchInput: '开关',
    SingleSelect: '单选框',
    MultiSelect: '多选框',
    DatePicker: '日期',
    JsonInput: 'JSON文本框',
    RadioCard: '选项卡',
    RadioRow: '单行选项卡'
  },
  default: {
    label: '默认值',
    placeholder: '请输入默认值',
    requiredMessage: '请输入默认值'
  },
  paramForm: {
    field: {
      label: '参数',
      placeholder: '请输入参数',
      requiredMessage: '参数 为必填属性'
    },
    name: {
      label: '显示名称',
      placeholder: '请输入显示名称',
      requiredMessage: '显示名称 为必填属性'
    },
    tooltip: {
      label: '参数提示说明',
      placeholder: '请输入参数提示说明'
    },
    required: {
      label: '是否必填',
      requiredMessage: '是否必填 为必填属性'
    },
    input_type: {
      label: '组件类型',
      placeholder: '请选择组件类型',
      requiredMessage: '组建类型 为必填属性'
    }
  }
}
