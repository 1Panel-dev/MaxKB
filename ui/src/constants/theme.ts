import defaultThemeImage from '@/assets/login-theme/default.png'
import greenThemeImage from '@/assets/login-theme/green.png'
import orangeThemeImage from '@/assets/login-theme/orange.png'
import purpleThemeImage from '@/assets/login-theme/purple.png'
import redThemeImage from '@/assets/login-theme/red.png'

export const DEFAULT_THEME_COLOR = '#3370ff'

const THEME_IMAGE_MAP: Record<string, string> = {
  [DEFAULT_THEME_COLOR]: defaultThemeImage,
  '#00b69d': greenThemeImage,
  '#7f3bf5': purpleThemeImage,
  '#f01d94': redThemeImage,
  '#ff6000': orangeThemeImage,
}

/** 根据主题色返回内置登录插图，自定义颜色使用默认插图。 */
export function getThemeImg(themeColor?: string) {
  return THEME_IMAGE_MAP[themeColor?.trim().toLowerCase() ?? ''] ?? defaultThemeImage
}

// 默认设置
export const defaultThemeSetting = {
  icon: '',
  loginLogo: '',
  loginImage: '',
  title: 'MaxKB',
  slogan: '强大易用的企业级智能体平台',
}

export const defaultPlatformSetting = {
  showUserManual: true,
  userManualUrl: 'https://maxkb.cn/docs/v2/',
  showForum: true,
  forumUrl: 'https://bbs.fit2cloud.com/c/mk/11',
  showProject: true,
  projectUrl: 'https://github.com/1Panel-dev/MaxKB',
}
