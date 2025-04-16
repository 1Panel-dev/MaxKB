export default {
  input_type_list: {
    TextInput: '文本框',
    PasswordInput: '密码框',
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
    requiredMessage: '为必填属性',
    show: '显示默认值'
  },
  tip: {
    requiredMessage: '不能为空',
    jsonMessage: 'JSON格式不正确'
  },
  searchBar: {
    placeholder: '请输入关键字搜索'
  },
  paramForm: {
    field: {
      label: '参数',
      placeholder: '请输入参数',
      requiredMessage: '参数 为必填属性',
      requiredMessage2: '只能输入字母数字和下划线'
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
  },
  DatePicker: {
    placeholder: '选择日期',
    year: '年',
    month: '月',
    date: '日期',
    datetime: '日期时间',
    dataType: {
      label: '时间类型',
      placeholder: '请选择时间类型'
    },
    format: {
      label: '格式',
      placeholder: '请选择格式'
    }
  },
  Select: {
    label: '选项值',
    placeholder: '请输入选项值'
  },
  tag: {
    label: '标签',
    placeholder: '请输入选项标签'
  },
  Slider: {
    showInput: {
      label: '是否带输入框'
    },
    valueRange: {
      label: '取值范围',
      minRequired: '最小值必填',
      maxRequired: '最大值必填'
    },
    step: {
      label: '步长值',
      requiredMessage1: '步长值必填',
      requiredMessage2: '步长不能为0'
    }
  },
  TextInput: {
    length: {
      label: '文本长度',
      minRequired: '最小长度必填',
      maxRequired: '最大长度必填',
      requiredMessage1: '长度在',
      requiredMessage2: '到',
      requiredMessage3: '个字符',
      requiredMessage4: '文本长度为必填参数'
    }
  }
}
