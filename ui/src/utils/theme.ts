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
  slogan: '欢迎使用 MaxKB 智能知识库'
}
