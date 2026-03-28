export default {
  input_type_list: {
    TextInput: 'Input',
    PasswordInput: 'Password',
    Slider: 'Slider',
    SwitchInput: 'Switch',
    SingleSelect: 'Chọn một lần',
    MultiSelect: 'Nhiều lựa chọn',
    DatePicker: 'Bộ chọn ngày',
    JsonInput: 'JSON',
    RadioCard: 'Thẻ vô tuyến',
    RadioRow: 'Hàng đài phát thanh',
    UploadInput: 'Tải tập tin lên',
    TextareaInput: 'Đầu vào nhiều dòng',
    MultiRow: 'nhiều hàng',
    Model: 'Model',
    Knowledge: 'Knowledge',
  },
  default: {
    label: 'Default',
    placeholder: 'Vui lòng nhập mặc định',
    requiredMessage: 'là thuộc tính bắt buộc',
    show: 'Hiển thị mặc định',
  },
  tip: {
    requiredMessage: 'không thể trống',
    jsonMessage: 'Định dạng JSON không chính xác',
  },
  paramForm: {
    field: {
      label: 'Parameter',
      placeholder: 'Vui lòng nhập một tham số',
      requiredMessage: 'Tham số là thuộc tính bắt buộc',
      requiredMessage2: 'Chỉ cho phép chữ cái, số và dấu gạch dưới',
    },
    name: {
      label: 'Name',
      placeholder: 'Vui lòng nhập tên',
      requiredMessage: 'Tên là thuộc tính bắt buộc',
    },
    tooltip: {
      label: 'Tooltip',
      placeholder: 'Vui lòng nhập chú giải công cụ',
    },
    required: {
      label: 'Required',
      requiredMessage: 'Bắt buộc là thuộc tính bắt buộc',
    },
    input_type: {
      label: 'Type',
      placeholder: 'Vui lòng chọn một loại',
      requiredMessage: 'Loại là thuộc tính bắt buộc',
    },
    desc: {
      label: 'description',
      placeholder: 'Vui lòng nhập mô tả',
    },
  },
  DatePicker: {
    placeholder: 'Chọn ngày',
    year: 'Year',
    month: 'Month',
    date: 'Date',
    datetime: 'Ngày giờ',
    dataType: {
      label: 'Loại ngày',
      placeholder: 'Vui lòng chọn loại ngày',
    },
    format: {
      label: 'Format',
      placeholder: 'Vui lòng chọn một định dạng',
    },
  },
  Select: {
    label: 'Giá trị tùy chọn',
    placeholder: 'Vui lòng nhập một giá trị tùy chọn',
  },
  tag: {
    label: 'Tag',
    placeholder: 'Vui lòng nhập nhãn tùy chọn',
  },
  Slider: {
    showInput: {
      label: 'Hiển thị hộp nhập liệu',
    },
    valueRange: {
      label: 'Phạm vi giá trị',
      minRequired: 'Giá trị tối thiểu là bắt buộc',
      maxRequired: 'Giá trị tối đa là bắt buộc',
    },
    step: {
      label: 'Giá trị bước',
      requiredMessage1: 'Giá trị bước là bắt buộc',
      requiredMessage2: 'Giá trị bước không thể là 0',
    },
  },
  TextInput: {
    length: {
      label: 'Độ dài văn bản',
      minRequired: 'Chiều dài tối thiểu là bắt buộc',
      maxRequired: 'Cần có độ dài tối đa',
      requiredMessage1: 'Độ dài phải ở giữa',
      requiredMessage2: 'and',
      requiredMessage3: 'characters',
      requiredMessage4: 'Độ dài văn bản là một tham số bắt buộc',
    },
  },
  UploadInput: {
    limit: {
      label: 'Số lượng tệp tối đa cho mỗi lần tải lên',
      required: 'Cần có số lượng tệp tối đa',
    },
    max_file_size: {
      label: 'Kích thước tệp tối đa (MB)',
      required: 'Kích thước tệp tối đa là bắt buộc',
    },
    accept: {
      label: 'Loại tệp',
      required: 'Loại tệp là bắt buộc',
    },
  },
  AssignmentMethod: {
    label: 'Phương pháp phân công',
    ref_variables: {
      label: 'Biến tham chiếu',
      popover: 'Giá trị biến phải tuân theo',
      json_format: 'định dạng JSON',
      popover_label: 'Label',
      popover_value: 'Value',
      popover_default: 'Là mặc định',
    },
  },
  ModelConstructor: {
    optionalModel: 'Mẫu tùy chọn',
    defaultModel: 'Mẫu mặc định',
    modelPlaceholder: 'Vui lòng nhập một mô hình',
  },
  KnowledgeConstructor: {
    optionalModel: 'Mẫu tùy chọn',
    defaultModel: 'Mẫu mặc định',
    modelPlaceholder: 'Vui lòng nhập một mô hình',
  },
}
