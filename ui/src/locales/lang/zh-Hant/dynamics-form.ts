export default {
  input_type_list: {
    TextInput: '文字框',
    PasswordInput: '密文框',
    Slider: '滑桿',
    SwitchInput: '開關',
    SingleSelect: '單選框',
    MultiSelect: '多選框',
    DatePicker: '日期選擇器',
    JsonInput: 'JSON文字框',
    RadioCard: '選項卡',
    RadioRow: '單行選項卡'
  },
  default: {
    label: '預設值',
    placeholder: '請輸入預設值',
    requiredMessage: '為必填屬性',
    show: '顯示預設值'
  },
  tip: {
    requiredMessage: '不能為空',
    jsonMessage: 'JSON格式不正確'
  },
  searchBar: {
    placeholder: '請輸入關鍵字搜索'
  },
  paramForm: {
    field: {
      label: '參數',
      placeholder: '請輸入參數',
      requiredMessage: '參數 為必填屬性',
      requiredMessage2: '只能輸入字母、數字和底線'
    },
    name: {
      label: '顯示名稱',
      placeholder: '請輸入顯示名稱',
      requiredMessage: '顯示名稱 為必填屬性'
    },
    tooltip: {
      label: '參數提示說明',
      placeholder: '請輸入參數提示說明'
    },
    required: {
      label: '是否必填',
      requiredMessage: '是否必填 為必填屬性'
    },
    input_type: {
      label: '組件類型',
      placeholder: '請選擇組件類型',
      requiredMessage: '組件類型 為必填屬性'
    }
  },
  DatePicker: {
    placeholder: '選擇日期',
    year: '年',
    month: '月',
    date: '日期',
    datetime: '日期時間',
    dataType: {
      label: '時間類型',
      placeholder: '請選擇時間類型'
    },
    format: {
      label: '格式',
      placeholder: '請選擇格式'
    }
  },
  Select: {
    label: '選項值',
    placeholder: '請輸入選項值'
  },
  tag: {
    label: '標籤',
    placeholder: '請輸入選項標籤'
  },
  Slider: {
    showInput: {
      label: '是否帶輸入框'
    },
    valueRange: {
      label: '取值範圍',
      minRequired: '最小值必填',
      maxRequired: '最大值必填'
    },
    step: {
      label: '步長值',
      requiredMessage1: '步長值必填',
      requiredMessage2: '步長不能為0'
    }
  },
  TextInput: {
    length: {
      label: '文字長度',
      minRequired: '最小長度必填',
      maxRequired: '最大長度必填',
      requiredMessage1: '長度在',
      requiredMessage2: '到',
      requiredMessage3: '個字元',
      requiredMessage4: '文字長度為必填參數'
    }
  }
}
