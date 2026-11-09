import type { FormField } from './type'

// Chat forms are data, not arbitrary Vue component/attribute definitions.
const inputTypes = new Set([
  'TextInput', 'TextareaInput', 'JsonInput', 'PasswordInput', 'SingleSelect', 'MultiSelect',
  'RadioCard', 'RadioRow', 'MultiRow', 'Slider', 'SwitchInput', 'DatePicker', 'UploadInput',
  'Model', 'Knowledge', 'TreeSelect',
])
const attributes = new Set([
  'maxlength', 'minlength', 'show-word-limit', 'placeholder', 'rows', 'autosize', 'clearable',
  'type', 'format', 'value-format', 'multiple', 'data', 'filterable', 'min', 'max', 'step',
  'show-input', 'show-input-controls', 'precision', 'show-stops', 'range', 'disabled', 'accept', 'limit',
  'provider_list', 'knowledge_list',
])

export function safeChatFormFields(fields: unknown, depth = 0): FormField[] {
  if (!Array.isArray(fields) || depth > 10) return []
  return fields
    .filter((field) => field && typeof field.field === 'string' && inputTypes.has(field.input_type))
    .map((field) => {
      const attrs = Object.fromEntries(
        Object.entries(field.attrs || {}).filter(([key]) => attributes.has(key)),
      )
      if (Array.isArray(attrs.provider_list)) {
        attrs.provider_list = attrs.provider_list.filter((provider) => provider && typeof provider === 'object')
          .map((provider) => ({
            ...provider,
            model_form_field: safeChatFormFields(provider.model_form_field, depth + 1),
          }))
      }
      const label = typeof field.label === 'string' ? field.label : {
        input_type: 'TooltipLabel',
        label: typeof field.label?.label === 'string' ? field.label.label : '',
        attrs: { tooltip: typeof field.label?.attrs?.tooltip === 'string' ? field.label.attrs.tooltip : '' },
      }
      return { ...field, attrs, label }
    })
}
