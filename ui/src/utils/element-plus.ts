// Element Plus 全局默认行为配置。
import { ElFormItem } from 'element-plus'

/** 禁止表单项标题自动关联并激活内部控件，保留显式 for 配置。 */
export function configureElementPlus() {
  // 在创建应用前设置默认值；升级 Element Plus 时需复核 FormItem 的 labelFor 实现。
  Object.assign(ElFormItem.props, {
    for: { type: String, default: '' },
  })
}
