/**
 * 按钮权限对外入口。
 *  - 模板中免 import 用全局 `$perm`（见 install.ts）
 *  - <script setup> / 工具函数中：`import { perm } from '@/permission'`
 *  - 引擎与常量在 `@/permission/core`
 */

import modules from './modules'

export const perm = modules

export default perm
