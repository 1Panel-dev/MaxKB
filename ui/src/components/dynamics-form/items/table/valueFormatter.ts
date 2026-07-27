interface ValueFormatConfig {
  type?: string
  property?: string
  value_field?: string
  value_fields?: Array<string>
  separator?: string
  locale?: string
  minimum_fraction_digits?: number
  maximum_fraction_digits?: number
  prefix?: string
  suffix?: string
}

const toText = (value: unknown) => (value === null || value === undefined ? '' : String(value))

export const formatTableValue = (config: ValueFormatConfig, row: Record<string, any>) => {
  let value: string

  if (config.type === 'concat') {
    value = (config.value_fields || [])
      .map((field) => toText(row[field]))
      .join(config.separator || '')
  } else {
    const field = config.value_field || config.property || ''
    const rawValue = row[field]

    if (config.type === 'number') {
      const numberValue =
        typeof rawValue === 'number' ? rawValue : Number.parseFloat(toText(rawValue))
      value = Number.isFinite(numberValue)
        ? numberValue.toLocaleString(config.locale, {
            style: 'decimal',
            minimumFractionDigits: config.minimum_fraction_digits,
            maximumFractionDigits: config.maximum_fraction_digits,
          })
        : toText(rawValue)
    } else {
      value = toText(rawValue)
    }
  }

  return `${config.prefix || ''}${value}${config.suffix || ''}`
}
