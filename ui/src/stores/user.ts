import { defineStore } from 'pinia'
import type { User } from '@/api/user/type'
import UserApi from '@/api/user'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<User>()
  // 用户认证token
  const token = ref<string>()

  const getToken = () => {
    if (token.value) {
      return token.value
    }
    return localStorage.getItem('token')
  }

  const getPermissions = () => {
    if (userInfo.value) {
      return userInfo.value.permissions
    } else {
      return []
    }
  }

  const getRole = () => {
    if (userInfo.value) {
      return userInfo.value.role
    } else {
      return ''
    }
  }

  const profile = () => {
    return UserApi.profile().then((ok) => {
      userInfo.value = ok.data
    })
  }

  const login = (username: string, password: string) => {
    return UserApi.login({ username, password }).then((ok) => {
      token.value = ok.data
      localStorage.setItem('token', ok.data)
      return profile()
    })
  }

  const logout = () => {
    return UserApi.logout().then(() => {
      localStorage.removeItem('token')
      return true
    })
  }
  return { token, getToken, userInfo, profile, login, logout, getPermissions, getRole }
})
