// 由 scripts/locale-schema.ts 根据默认语言的 JSON 文件生成。
import 'vue-i18n'

declare module 'vue-i18n' {
  interface DefineLocaleMessage {
    "application": typeof import("./zh-CN/application.json")
    "auth": typeof import("./zh-CN/auth.json")
    "common": typeof import("./zh-CN/common.json")
    "dynamicForm": typeof import("./zh-CN/dynamic-form.json")
    "folder": typeof import("./zh-CN/folder.json")
    "knowledge": typeof import("./zh-CN/knowledge.json")
    "model": typeof import("./zh-CN/model.json")
    "resource": typeof import("./zh-CN/resource.json")
    "tool": typeof import("./zh-CN/tool.json")
    "workspace": typeof import("./zh-CN/workspace.json")
  }
}
