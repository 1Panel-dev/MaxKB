import { t } from '@/locales'

export const themeList = [
  {
    label: t('theme.default'),
    value: '#1A6DFF',
    loginBackground: 'default',
  },
  {
    label: t('theme.orange'),
    value: '#FF8800',
    loginBackground: 'orange',
  },
  {
    label: t('theme.green'),
    value: '#00B69D',
    loginBackground: 'green',
  },
  {
    label: t('theme.purple'),
    value: '#7F3BF5',
    loginBackground: 'purple',
  },
  {
    label: t('theme.red'),
    value: '#F01D94',
    loginBackground: 'red',
  },
]

export function getThemeImg(val: string) {
  if (!val) return 'default'
  return themeList.filter((v) => v.value === val)?.[0]?.loginBackground || 'default'
}

export const defaultSetting = {
  icon: '',
  loginLogo: '',
  loginImage: '',
  title: 'MaxKB',
  slogan: t('theme.defaultSlogan'),
}

export const defaultPlatformSetting = {
  showUserManual: true,
  userManualUrl: t('layout.userManualUrl'),
  showForum: true,
  forumUrl: t('layout.forumUrl'),
  showProject: true,
  projectUrl: 'https://github.com/1Panel-dev/MaxKB',
}

export function hexToRgba(hex?: string, alpha?: number) {
  if (!hex) {
    return ''
  } else {
    const r = parseInt(hex.slice(1, 3), 16)
    const g = parseInt(hex.slice(3, 5), 16)
    const b = parseInt(hex.slice(5, 7), 16)
    return `rgba(${r}, ${g}, ${b}, ${alpha})`
  }
}

// ===== 暗色模式 =====
export type DarkModeType = 'light' | 'dark' | 'system'

const DARK_MODE_KEY = 'MaxKB-dark-mode'

export function getDarkMode(): DarkModeType {
  return (localStorage.getItem(DARK_MODE_KEY) as DarkModeType) || 'light'
}

export function setDarkMode(mode: DarkModeType) {
  localStorage.setItem(DARK_MODE_KEY, mode)
  applyDarkMode(mode)
}

export function applyDarkMode(mode?: DarkModeType) {
  const currentMode = mode || getDarkMode()
  const root = document.documentElement

  if (currentMode === 'dark') {
    root.setAttribute('data-theme', 'dark')
  } else if (currentMode === 'light') {
    root.removeAttribute('data-theme')
  } else {
    // system: follow OS preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark) {
      root.setAttribute('data-theme', 'dark')
    } else {
      root.removeAttribute('data-theme')
    }
  }
}

export function initDarkMode() {
  applyDarkMode()
  // Listen for OS theme changes when in system mode
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (getDarkMode() === 'system') {
      applyDarkMode('system')
    }
  })
}
