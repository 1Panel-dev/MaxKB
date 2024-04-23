import type {
  ThemeSetting,
  InferData,
  KeyValueData,
  UpdateInferData,
  UpdateKeyValueData
} from './type'
import { TinyColor } from '@ctrl/tinycolor'
// 引入默认推断数据
import inferData from './defaultInferData'
// 引入默认keyValue数据
import keyValueData from './defaultKeyValueData'
// 引入设置对象
import setting from './setting'
import type { App } from 'vue'
declare global {
  interface ChildNode {
    innerText: string
  }
}
class Theme {
  /**
   * 主题设置
   */
  themeSetting: ThemeSetting
  /**
   * 键值数据
   */
  keyValue: KeyValueData
  /**
   * 外推数据
   */
  inferData: Array<InferData>
  /**
   *是否是第一次初始化
   */
  isFirstWriteStyle: boolean
  /**
   * 混色白
   */
  colorWhite: string
  /**
   * 混色黑
   */
  colorBlack: string

  constructor(themeSetting: ThemeSetting, keyValue: KeyValueData, inferData: Array<InferData>) {
    this.themeSetting = themeSetting
    this.keyValue = keyValue
    this.inferData = inferData
    this.isFirstWriteStyle = true
    this.colorWhite = '#ffffff'
    this.colorBlack = '#000000'
    this.initDefaultTheme()
  }

  /**
   * 拼接
   * @param setting 主题设置
   * @param names   需要拼接的所有值
   * @returns       拼接后的数据
   */
  getVarName = (setting: ThemeSetting, ...names: Array<string>) => {
    return (
      setting.startDivision + setting.namespace + setting.division + names.join(setting.division)
    )
  }

  /**
   * 转换外推数据
   * @param setting      主题设置对象
   * @param inferData    外推数据
   * @returns
   */
  mapInferMainStyle = (setting: ThemeSetting, inferData: InferData) => {
    const key: string = this.getVarName(
      setting,
      inferData.setting ? inferData.setting.type : setting.colorInferSetting.type,
      inferData.key
    )
    return {
      [key]: inferData.value,
      ...this.mapInferDataStyle(setting, inferData)
    }
  }
  /**
   * 转换外推数据
   * @param setting    设置
   * @param inferData 外推数据
   */
  mapInferData = (setting: ThemeSetting, inferData: Array<InferData>) => {
    return inferData
      .map((itemData) => {
        return this.mapInferMainStyle(setting, itemData)
      })
      .reduce((pre, next) => {
        return { ...pre, ...next }
      }, {})
  }
  /**
   * 转换外推数据
   * @param setting      主题设置对象
   * @param inferData    外推数据
   * @returns
   */
  mapInferDataStyle = (setting: ThemeSetting, inferData: InferData) => {
    const inferSetting = inferData.setting ? inferData.setting : setting.colorInferSetting
    if (inferSetting.type === 'color') {
      return Object.keys(inferSetting)
        .map((key: string) => {
          if (key === 'light' || key === 'dark') {
            return inferSetting[key]
              .map((l: any) => {
                const varName = this.getVarName(
                  setting,
                  inferSetting.type,
                  inferData.key,
                  key,
                  l.toString()
                )
                return {
                  [varName]: new TinyColor(inferData.value)
                    .mix(key === 'light' ? this.colorWhite : this.colorBlack, l * 10)
                    .toHexString()
                }
              })
              .reduce((pre: any, next: any) => {
                return { ...pre, ...next }
              }, {})
          }
          return {}
        })
        .reduce((pre, next) => {
          return { ...pre, ...next }
        }, {})
    }
    return {}
  }

  /**
   *
   * @param themeSetting 主题设置
   * @param keyValueData 键值数据
   * @returns            映射后的键值数据
   */
  mapKeyValue = (themeSetting: ThemeSetting, keyValueData: KeyValueData) => {
    return Object.keys(keyValueData)
      .map((key: string) => {
        return {
          [this.updateKeyBySetting(key, themeSetting)]: keyValueData[key]
        }
      })
      .reduce((pre, next) => {
        return { ...pre, ...next }
      }, {})
  }
  /**
   * 根据配置文件修改Key
   * @param key          key
   * @param themeSetting 主题设置
   * @returns
   */
  updateKeyBySetting = (key: string, themeSetting: ThemeSetting) => {
    return key.startsWith(themeSetting.startDivision)
      ? key
      : key.startsWith(themeSetting.namespace)
      ? themeSetting.startDivision + key
      : key.startsWith(themeSetting.division)
      ? themeSetting.startDivision + themeSetting.namespace
      : themeSetting.startDivision + themeSetting.namespace + themeSetting.division + key
  }
  /**
   *
   * @param setting    主题设置
   * @param keyValue   主题键值对数据
   * @param inferData 外推数据
   * @returns 合并后的键值对数据
   */
  tokeyValueStyle = () => {
    return {
      ...this.mapInferData(this.themeSetting, this.inferData),
      ...this.mapKeyValue(this.themeSetting, this.keyValue)
    }
  }

  /**
   * 将keyValue对象转换为S
   * @param keyValue
   * @returns
   */
  toString = (keyValue: KeyValueData) => {
    const inner = Object.keys(keyValue)
      .map((key: string) => {
        return key + ':' + keyValue[key] + ';'
      })
      .join('')
    return `@charset "UTF-8";:root{${inner}}`
  }

  /**
   *
   * @param elNewStyle 新的变量样式
   */
  writeNewStyle = (elNewStyle: string) => {
    if (this.isFirstWriteStyle) {
      const style = document.createElement('style')
      style.innerText = elNewStyle
      document.head.appendChild(style)
      this.isFirstWriteStyle = false
    } else {
      if (document.head.lastChild) {
        document.head.lastChild.innerText = elNewStyle
      }
    }
  }

  /**
   * 修改数据并且写入dom
   * @param updateInferData   平滑数据修改
   * @param updateKeyvalueData keyValue数据修改
   */
  updateWrite = (updateInferData?: UpdateInferData, updateKeyvalueData?: UpdateKeyValueData) => {
    this.update(updateInferData, updateKeyvalueData)
    const newStyle = this.tokeyValueStyle()
    const newStyleString = this.toString(newStyle)
    this.writeNewStyle(newStyleString)
  }

  /**
   * 修改数据
   * @param inferData
   * @param keyvalueData
   */
  update = (updateInferData?: UpdateInferData, updateKeyvalueData?: UpdateKeyValueData) => {
    if (updateInferData) {
      this.updateInferData(updateInferData)
    }
    if (updateKeyvalueData) {
      this.updateOrCreateKeyValueData(updateKeyvalueData)
    }
  }

  /**
   * 修改外推数据 外推数据只能修改,不能新增
   * @param inferData
   */
  updateInferData = (updateInferData: UpdateInferData) => {
    Object.keys(updateInferData).forEach((key) => {
      const findInfer = this.inferData.find((itemInfer) => {
        return itemInfer.key === key
      })
      if (findInfer) {
        findInfer.value = updateInferData[key]
      } else {
        this.inferData.push({ key, value: updateInferData[key] })
      }
    })
  }

  /**
   * 初始化默认主题
   */
  initDefaultTheme = () => {
    this.updateWrite()
  }
  /**
   * 修改KeyValue数据
   * @param keyvalueData keyValue数据
   */
  updateOrCreateKeyValueData = (updateKeyvalueData: UpdateKeyValueData) => {
    Object.keys(updateKeyvalueData).forEach((key) => {
      const newKey = this.updateKeyBySetting(key, this.themeSetting)
      this.keyValue[newKey] = updateKeyvalueData[newKey]
    })
  }
}

const install = (app: App) => {
  app.config.globalProperties.theme = new Theme(setting, keyValueData, inferData)
}
export default { install }
