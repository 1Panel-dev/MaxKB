interface ChatProfile {
  // 是否开启认证
  authentication: boolean
  // icon
  icon?: string
  // 应用名称
  application_name?: string
  // 背景图
  bg_icon?: string
  // 认证类型
  authentication_type?: 'password' | 'login'
  // 登录类型
  login_value?: Array<string>
}
export { type ChatProfile }
