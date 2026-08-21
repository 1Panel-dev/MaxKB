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
export const resetUrl = (url: string, defaultUrl?: string) => {
  if (url && url.startsWith('./')) {
    return `${window.MaxKB?.prefix}/${url.substring(2)}`
  }
  return url ? url : defaultUrl ? defaultUrl : ''
}
