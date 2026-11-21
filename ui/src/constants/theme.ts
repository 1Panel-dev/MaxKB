import { computed, reactive } from 'vue'
import defaultThemeImage from '@/assets/login-theme/default.png'
import greenThemeImage from '@/assets/login-theme/green.png'
import orangeThemeImage from '@/assets/login-theme/orange.png'
import purpleThemeImage from '@/assets/login-theme/purple.png'
import redThemeImage from '@/assets/login-theme/red.png'
import { t } from '@/locales'

export const DEFAULT_THEME_COLOR = '#3370ff'

export const THEME_OPTIONS = reactive([
  { label: computed(() => t('appearance.colors.default')), value: DEFAULT_THEME_COLOR, loginBackground: defaultThemeImage },
  { label: computed(() => t('appearance.colors.orange')), value: '#ff6000', loginBackground: orangeThemeImage },
  { label: computed(() => t('appearance.colors.green')), value: '#00b69d', loginBackground: greenThemeImage },
  { label: computed(() => t('appearance.colors.purple')), value: '#7f3bf5', loginBackground: purpleThemeImage },
  { label: computed(() => t('appearance.colors.red')), value: '#f01d94', loginBackground: redThemeImage },
] as const)

/** 根据主题色返回内置登录插图，自定义颜色使用默认插图。 */
export function getThemeImg(themeColor?: string) {
  const normalizedThemeColor = themeColor?.trim().toLowerCase()
  return THEME_OPTIONS.find((themeOption) => themeOption.value === normalizedThemeColor)?.loginBackground ?? defaultThemeImage
}

export const DEFAULT_THEME_SETTING = reactive({
  icon: '',
  loginLogo: '',
  loginImage: '',
  title: 'MaxKB',
  slogan: computed(() => t('layout.slogan')),
  theme: DEFAULT_THEME_COLOR,
})

export const DEFAULT_PLATFORM_SETTING = {
  showUserManual: true,
  userManualUrl: 'https://docs.fit2cloud.com/maxkb/',
  showForum: true,
  forumUrl: 'https://bbs.fit2cloud.com/c/mk/11',
  showProject: true,
  projectUrl: 'https://github.com/1Panel-dev/MaxKB',
}
