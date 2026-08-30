import defaultThemeImage from '@/assets/login-theme/default.png'
import greenThemeImage from '@/assets/login-theme/green.png'
import orangeThemeImage from '@/assets/login-theme/orange.png'
import purpleThemeImage from '@/assets/login-theme/purple.png'
import redThemeImage from '@/assets/login-theme/red.png'

export const DEFAULT_THEME_COLOR = '#3370ff'

export const THEME_OPTIONS = [
  { label: '默认', value: DEFAULT_THEME_COLOR, loginBackground: defaultThemeImage },
  { label: '活力橙', value: '#ff6000', loginBackground: orangeThemeImage },
  { label: '松石绿', value: '#00b69d', loginBackground: greenThemeImage },
  { label: '神秘紫', value: '#7f3bf5', loginBackground: purpleThemeImage },
  { label: '胭脂红', value: '#f01d94', loginBackground: redThemeImage },
] as const

/** 根据主题色返回内置登录插图，自定义颜色使用默认插图。 */
export function getThemeImg(themeColor?: string) {
  const normalizedThemeColor = themeColor?.trim().toLowerCase()
  return THEME_OPTIONS.find((themeOption) => themeOption.value === normalizedThemeColor)?.loginBackground ?? defaultThemeImage
}

export const DEFAULT_THEME_SETTING = { icon: '', loginLogo: '', loginImage: '', title: 'MaxKB', slogan: '强大易用的企业级智能体平台', theme: DEFAULT_THEME_COLOR }

export const DEFAULT_PLATFORM_SETTING = {
  showUserManual: true,
  userManualUrl: 'https://maxkb.cn/docs/v2/',
  showForum: true,
  forumUrl: 'https://bbs.fit2cloud.com/c/mk/11',
  showProject: true,
  projectUrl: 'https://github.com/1Panel-dev/MaxKB',
}
