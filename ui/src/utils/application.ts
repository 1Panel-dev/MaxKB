import { APPLICATION_TYPE } from '@/api/enums'
export function isWorkFlow(type: string | undefined) {
  return type === APPLICATION_TYPE.WORK_FLOW
}
