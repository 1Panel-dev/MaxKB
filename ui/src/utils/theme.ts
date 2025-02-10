import { t } from '@/locales'

export const themeList = [
  {
    label: t('views.system.theme.default'),
    value: '#3370FF',
    loginBackground: 'default'
  },
  {
    label: t('views.system.theme.orange'),
    value: '#FF8800',
    loginBackground: 'orange'
  },
  {
    label: t('views.system.theme.green'),
    value: '#00B69D',
    loginBackground: 'green'
  },
  {
    label: t('views.system.theme.purple'),
    value: '#7F3BF5',
    loginBackground: 'purple'
  },
  {
    label: t('views.system.theme.red'),
    value: '#F01D94',
    loginBackground: 'red'
  }
]

export function getThemeImg(val: string) {
  return themeList.filter((v) => v.value === val)?.[0]?.loginBackground || 'default'
}

export const defaultSetting = {
  icon: '',
  loginLogo: '',
  loginImage: '',
  title: 'MaxKB',
  slogan: t('views.system.theme.defaultSlogan')
}

export const defaultPlatformSetting = {
  showUserManual: true,
  userManualUrl: t('layout.userManualUrl'),
  showForum: true,
  forumUrl: t('layout.forumUrl'),
  showProject: true,
  projectUrl: 'https://github.com/1Panel-dev/MaxKB'
}

export function hexToRgba(hex?: string, alpha?: number) {
  // 将16进制颜色值的两个字符一起转换成十进制
  if (!hex) {
    return ''
  } else {
    const r = parseInt(hex.slice(1, 3), 16)
    const g = parseInt(hex.slice(3, 5), 16)
    const b = parseInt(hex.slice(5, 7), 16)

    // 返回RGBA格式的字符串
    return `rgba(${r}, ${g}, ${b}, ${alpha})`
  }
}
