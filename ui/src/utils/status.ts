import { type Dict } from '@/api/type/common'
interface TaskTypeInterface {
  // 向量化
  EMBEDDING: number
  // 生成问题
  GENERATE_PROBLEM: number
  // 同步
  SYNC: number
}
interface StateInterface {
  // 等待
  PENDING: '0'
  // 执行中
  STARTED: '1'
  // 成功
  SUCCESS: '2'
  // 失败
  FAILURE: '3'
  // 取消任务
  REVOKE: '4'
  // 取消成功
  REVOKED: '5'
  IGNORED: 'n'
}
const TaskType: TaskTypeInterface = {
  EMBEDDING: 1,
  GENERATE_PROBLEM: 2,
  SYNC: 3
}
const State: StateInterface = {
  // 等待
  PENDING: '0',
  // 执行中
  STARTED: '1',
  // 成功
  SUCCESS: '2',
  // 失败
  FAILURE: '3',
  // 取消任务
  REVOKE: '4',
  // 取消成功
  REVOKED: '5',
  IGNORED: 'n'
}
class Status {
  task_status: Dict<any>
  constructor(status?: string) {
    if (!status) {
      status = ''
    }
    status = status.split('').reverse().join('')
    this.task_status = {}
    for (const key in TaskType) {
      const value = TaskType[key as keyof TaskTypeInterface]
      const index = value - 1
      this.task_status[value] = status[index] ? status[index] : 'n'
    }
  }
  toString() {
    const r = []
    for (const key in TaskType) {
      const value = TaskType[key as keyof TaskTypeInterface]
      r.push(this.task_status[value])
    }
    return r.reverse().join('')
  }
}
export { Status, State, TaskType, type TaskTypeInterface, type StateInterface }
