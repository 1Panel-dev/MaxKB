import { t } from '@/locales'

const inputTypeList = [
  { key: 'dynamicsForm.input_type_list.TextInput', value: 'TextInput' },
  { key: 'dynamicsForm.input_type_list.TextareaInput', value: 'TextareaInput' },
  { key: 'dynamicsForm.input_type_list.JsonInput', value: 'JsonInput' },
  { key: 'dynamicsForm.input_type_list.PasswordInput', value: 'PasswordInput' },
  { key: 'dynamicsForm.input_type_list.SingleSelect', value: 'SingleSelect' },
  { key: 'dynamicsForm.input_type_list.MultiSelect', value: 'MultiSelect' },
  { key: 'dynamicsForm.input_type_list.RadioCard', value: 'RadioCard' },
  { key: 'dynamicsForm.input_type_list.RadioRow', value: 'RadioRow' },
  { key: 'dynamicsForm.input_type_list.MultiRow', value: 'MultiRow' },
  { key: 'dynamicsForm.input_type_list.Slider', value: 'Slider' },
  { key: 'dynamicsForm.input_type_list.SwitchInput', value: 'SwitchInput' },
  { key: 'dynamicsForm.input_type_list.DatePicker', value: 'DatePicker' },
  { key: 'dynamicsForm.input_type_list.UploadInput', value: 'UploadInput' },
  { key: 'dynamicsForm.input_type_list.Model', value: 'Model' },
  { key: 'dynamicsForm.input_type_list.Knowledge', value: 'Knowledge' },
  { key: 'dynamicsForm.TreeSelect.label', value: 'TreeSelect' },
]

const input_type_list = inputTypeList.map((item) => ({
  get label() {
    return t(item.key)
  },
  value: item.value,
}))

export { input_type_list }
