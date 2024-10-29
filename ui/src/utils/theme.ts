export const themeList = [
  {
    label: '默认',
    value: '#3370FF',
    loginBackground: 'default'
  },
  {
    label: '活力橙',
    value: '#FF8800',
    loginBackground: 'orange'
  },
  {
    label: '松石绿',
    value: '#00B69D',
    loginBackground: 'green'
  },
  {
    label: '神秘紫',
    value: '#7F3BF5',
    loginBackground: 'purple'
  },
  {
    label: '胭脂红',
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
  slogan: '欢迎使用 MaxKB 智能知识库问答系统'
}

export const defaultPlatformSetting = {
  showUserManual: true,
  userManualUrl: 'https://maxkb.cn/docs/',
  showForum: true,
  forumUrl: 'https://bbs.fit2cloud.com/c/mk/11',
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
