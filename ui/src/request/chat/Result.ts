export class Result<T> {
  message: string
  code: number
  data: T
  constructor(message: string, code: number, data: T) {
    this.message = message
    this.code = code
    this.data = data
  }

  static success(data: any) {
    return new Result('请求成功', 200, data)
  }
  static error(message: string, code: number) {
    return new Result(message, code, null)
  }
}

export default Result
