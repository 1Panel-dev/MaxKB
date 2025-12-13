export default {
  input_type_list: {
    TextInput: 'Input',
    PasswordInput: 'Password',
    Slider: 'Slider',
    SwitchInput: 'Switch',
    SingleSelect: 'Single Select',
    MultiSelect: 'Multi Select',
    DatePicker: 'Date Picker',
    JsonInput: 'JSON',
    RadioCard: 'Radio Card',
    RadioRow: 'Radio Row',
    UploadInput: 'File upload',
    TextareaInput: 'Multiline Input',
    MultiRow: 'Multi Row',
  },
  default: {
    label: 'Default',
    placeholder: 'Please enter a default',
    requiredMessage: ' is a required property',
    show: 'Show Default',
  },
  tip: {
    requiredMessage: 'cannot be empty',
    jsonMessage: 'Incorrect JSON format',
  },
  paramForm: {
    field: {
      label: 'Parameter',
      placeholder: 'Please enter a parameter',
      requiredMessage: 'Parameter is a required property',
      requiredMessage2: 'Only letters, numbers, and underscores are allowed',
    },
    name: {
      label: 'Name',
      placeholder: 'Please enter a name',
      requiredMessage: 'Name is a required property',
    },
    tooltip: {
      label: 'Tooltip',
      placeholder: 'Please enter a tooltip',
    },
    required: {
      label: 'Required',
      requiredMessage: 'Required is a required property',
    },
    input_type: {
      label: 'Type',
      placeholder: 'Please select a type',
      requiredMessage: 'Type is a required property',
    },
  },
  DatePicker: {
    placeholder: 'Select Date',
    year: 'Year',
    month: 'Month',
    date: 'Date',
    datetime: 'Date Time',
    dataType: {
      label: 'Date Type',
      placeholder: 'Please select a date type',
    },
    format: {
      label: 'Format',
      placeholder: 'Please select a format',
    },
  },
  Select: {
    label: 'Option Value',
    placeholder: 'Please enter an option value',
  },
  tag: {
    label: 'Tag',
    placeholder: 'Please enter an option label',
  },
  Slider: {
    showInput: {
      label: 'Show Input Box',
    },
    valueRange: {
      label: 'Value Range',
      minRequired: 'Minimum value is required',
      maxRequired: 'Maximum value is required',
    },
    step: {
      label: 'Step Value',
      requiredMessage1: 'Step value is required',
      requiredMessage2: 'Step value cannot be 0',
    },
  },
  TextInput: {
    length: {
      label: 'Text Length',
      minRequired: 'Minimum length is required',
      maxRequired: 'Maximum length is required',
      requiredMessage1: 'Length must be between',
      requiredMessage2: 'and',
      requiredMessage3: 'characters',
      requiredMessage4: 'Text length is a required parameter',
    },
  },
  UploadInput: {
    limit: {
      label: 'Maximum number of files per upload',
      required: 'Maximum number of files is required',
    },
    max_file_size: {
      label: 'Maximum file size (MB)',
      required: 'Maximum file size is required',
    },
    accept: {
      label: 'File type',
      required: 'File type is required',
    },
  },
  AssignmentMethod: {
    label: 'Assignment Method',
    custom: {
      label: 'Custom',
    },
    ref_variables: {
      label: 'Reference Variables',
      popover: 'Variable values must comply with',
      json_format: 'JSON format',
      popover_label: 'Label',
      popover_value: 'Value',
      popover_default: 'Is Default',
    },
  },
}
