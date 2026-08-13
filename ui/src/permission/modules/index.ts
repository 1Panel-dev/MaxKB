/**
 * 各资源 / 功能模块的按钮权限汇总。
 *
 * A 类（资源，含 workspace / system / share 场景）：application / knowledge / tool / model
 * B 类（系统全局项，扁平、单场景）：见 ./system 下的 user / role / ...
 */

import application from './application'
import knowledge from './knowledge'
import tool from './tool'
import model from './model'
import system from './system'

export default {
  application,
  knowledge,
  tool,
  model,
  ...system,
}
