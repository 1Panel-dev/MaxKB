import { nanoid } from 'nanoid'
/*
  随机id
*/
export function randomId() {
  return nanoid()
}

/*
  icon url
*/
export const resetUrl = (url?: string | null, useDefault?: boolean) => {
  const sourceUrl = url || (useDefault ? './favicon.ico' : '')
  if (sourceUrl && sourceUrl.startsWith('./')) {
    return `${window.MaxKB?.prefix}/${sourceUrl.substring(2)}`
  }
  return sourceUrl
}
