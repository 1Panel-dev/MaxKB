export default {
  input_type_list: {
    TextInput: 'Text Input',
    Slider: 'Slider',
    SwitchInput: 'Switch',
    SingleSelect: 'Single Select',
    MultiSelect: 'Multi Select',
    DatePicker: 'Date Picker',
    JsonInput: 'JSON Text Input',
    RadioCard: 'Radio Card',
    RadioRow: 'Radio Row'
  },
  default: {
    label: 'Default Value',
    placeholder: 'Please enter a default value',
    requiredMessage: ' is a required property',
    show: 'Show Default Value'
  },
  tip: {
    requiredMessage: 'Cannot be empty',
    jsonMessage: 'Incorrect JSON format'
  },
  searchBar: {
    placeholder: 'Please enter keywords to search'
  },
  paramForm: {
    field: {
      label: 'Parameter',
      placeholder: 'Please enter a parameter',
      requiredMessage: 'Parameter is a required property',
      requiredMessage2: 'Only letters, numbers, and underscores are allowed'
    },
    name: {
      label: 'Display Name',
      placeholder: 'Please enter a display name',
      requiredMessage: 'Display Name is a required property'
    },
    tooltip: {
      label: 'Parameter Tooltip',
      placeholder: 'Please enter a parameter tooltip'
    },
    required: {
      label: 'Is Required',
      requiredMessage: 'Is Required is a required property'
    },
    input_type: {
      label: 'Component Type',
      placeholder: 'Please select a component type',
      requiredMessage: 'Component Type is a required property'
    }
  },
  DatePicker: {
    placeholder: 'Select Date',
    year: 'Year',
    month: 'Month',
    date: 'Date',
    datetime: 'Date Time',
    dataType: {
      label: 'Date Type',
      placeholder: 'Please select a date type'
    },
    format: {
      label: 'Format',
      placeholder: 'Please select a format'
    }
  },
  Select: {
    label: 'Option Value',
    placeholder: 'Please enter an option value'
  },
  tag: {
    label: 'Tag',
    placeholder: 'Please enter an option label'
  },
  Slider: {
    showInput: ''
  }
}
