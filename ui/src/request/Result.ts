export class Result<T> {
  message: string;
  code: number;
  data: T;
  constructor(message: string, code: number, data: T) {
    this.message = message;
    this.code = code;
    this.data = data;
  }

  static success(data: any) {
    return new Result("请求成功", 200, data);
  }
  static error(message: string, code: number) {
    return new Result(message, code, null);
  }
}

interface Page<T> {
  /**
   *分页数据
   */
  records: Array<T>;
  /**
   *当前页
   */
  current: number;
  /**
   * 每页展示size
   */
  size: number;
  /**
   *总数
   */
  total: number;
  /**
   *是否有下一页
   */
  hasNext: boolean;
}
export type { Page };
export default Result;
