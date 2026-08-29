import { nanoid } from 'nanoid'
/*
  随机id
*/
export function randomId() {
  return nanoid()
}


export const relatedObject = (list: Array<Record<string, unknown>>, val: unknown, attr: string) => {
  const filterData = list.find((item) => item[attr] === val)
  return filterData || null
}
export const getAttrsArray = (array: Array<Record<string, unknown>>, attr: string) => {
  return array.map((item) => {
    return item[attr]
  })
}

export const downloadByURL = (url: string, name: string) => {
  const a = document.createElement('a')
  a.setAttribute('href', url)
  a.setAttribute('target', '_blank')
  a.setAttribute('download', name)
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

export const getFileUrl = (fileId?: string) => {
  if (fileId) {
    return `./oss/file/${fileId}`
  }
  return ''
}
