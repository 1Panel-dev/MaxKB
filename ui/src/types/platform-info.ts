/** 平台版本、许可和外观主题使用的数据类型。 */

export interface PlatformInfo {
  edition: 'CE' | 'EE' | 'PE'
  license_is_valid: boolean
  permissions?: string[]
  role?: string[]
  rsa: string
  version?: string
}

export interface ThemeInfo {
  forumUrl?: string
  icon?: string
  loginImage?: string
  loginLogo?: string
  projectUrl?: string
  showForum?: boolean
  showProject?: boolean
  showUserManual?: boolean
  slogan?: string
  theme?: string
  title?: string
  userManualUrl?: string
}
