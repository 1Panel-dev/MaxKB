interface ThemeSetting {
  /**
   *element-ui Namespace
   */
  namespace: string;
  /**
   * 数据分隔符
   */
  division: string;
  /**
   * 前缀
   */
  startDivision: string;
  /**
   * 颜色外推设置
   */
  colorInferSetting: ColorInferSetting;
}

/**
 * 颜色混和设置
 */
interface ColorInferSetting {
  /**
   * 与白色混
   */
  light: Array<number>;
  /**
   * 与黑色混
   */
  dark: Array<number>;
  /**
   * 类型
   */
  type: string;
}

/**
 * 平滑数据
 */
interface KeyValueData {
  [propName: string]: string;
}
type UpdateInferData = KeyValueData;

type UpdateKeyValueData = KeyValueData;
/**
 *平滑数据
 */
interface InferData {
  /**
   * 设置
   */
  setting?: ColorInferSetting | any;
  /**
   * 健
   */
  key: string;
  /**
   * 值
   */
  value: string;
}

export type {
  KeyValueData,
  InferData,
  ThemeSetting,
  UpdateInferData,
  UpdateKeyValueData,
};
