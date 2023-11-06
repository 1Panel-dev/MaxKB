function toThousands(num: any) {
  return num.toString().replace(/\d+/, function (n: any) {
    return n.replace(/(\d)(?=(?:\d{3})+$)/g, '$1,')
  })
}
export function numberFormat(num: number) {
  return num < 1000 ? toThousands(num) : toThousands((num / 1000).toFixed(1)) + 'k'
}

export function filesize(size: number) {
  if (!size) return ''
  const num = 1024.0 //byte

  if (size < num) return size + 'B'
  if (size < Math.pow(num, 2)) return (size / num).toFixed(2) + 'K' //kb
  if (size < Math.pow(num, 3)) return (size / Math.pow(num, 2)).toFixed(2) + 'M' //M
  if (size < Math.pow(num, 4)) return (size / Math.pow(num, 3)).toFixed(2) + 'G' //G
  return (size / Math.pow(num, 4)).toFixed(2) + 'T' //T
}

// 获取文件后缀
export function fileType(name: string) {
  const suffix = name.split('.')
  return suffix[suffix.length - 1]
}

// 获得文件对应图片
export function getImgUrl(name: string) {
  const type = fileType(name) || 'txt'
  return `/src/assets/${type}-icon.svg`
}
