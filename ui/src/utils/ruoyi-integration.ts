/**
 * Ruoyi系统集成工具类
 */
import request from '@/request/index'
import { ElMessage } from 'element-plus'

export interface RuoyiUserInfo {
  userId: number
  username: string
  nickname?: string
  email?: string
  roles: string[]
  permissions: string[]
}

export interface RuoyiLoginResponse {
  code: number
  msg: string
  data: {
    token: string
    username: string
    nickname: string
    email: string
    role: string
  }
}

export class RuoyiIntegration {
  
  /**
   * 使用Ruoyi Token登录MaxKB
   */
  static async loginWithRuoyiToken(token: string): Promise<boolean> {
    try {
      const response = await request.post<RuoyiLoginResponse>('/api/user/ruoyi_login', {
        token: token
      })
      
      if (response.data.code === 200) {
        // 保存MaxKB token到localStorage
        localStorage.setItem('token', response.data.data.token)
        localStorage.setItem('user', JSON.stringify(response.data.data))
        
        ElMessage.success('登录成功')
        return true
      } else {
        ElMessage.error(response.data.msg || '登录失败')
        return false
      }
    } catch (error: any) {
      console.error('Ruoyi登录失败:', error)
      ElMessage.error(error.response?.data?.message || '登录失败')
      return false
    }
  }
  
  /**
   * 从URL参数获取Ruoyi Token
   */
  static getRuoyiTokenFromUrl(): string | null {
    const urlParams = new URLSearchParams(window.location.search)
    return urlParams.get('ruoyi_token')
  }
  
  /**
   * 从父窗口获取Ruoyi Token（iframe环境）
   */
  static getRuoyiTokenFromParent(): Promise<string | null> {
    return new Promise((resolve) => {
      // 设置超时
      const timeout = setTimeout(() => {
        resolve(null)
      }, 5000)
      
      // 监听父窗口消息
      const messageHandler = (event: MessageEvent) => {
        if (event.data.type === 'RUOYI_TOKEN') {
          clearTimeout(timeout)
          window.removeEventListener('message', messageHandler)
          resolve(event.data.token)
        }
      }
      
      window.addEventListener('message', messageHandler)
      
      // 向父窗口请求token
      if (window.parent !== window) {
        window.parent.postMessage({ 
          type: 'REQUEST_RUOYI_TOKEN' 
        }, '*')
      } else {
        clearTimeout(timeout)
        resolve(null)
      }
    })
  }
  
  /**
   * 检查Ruoyi Token状态
   */
  static async checkRuoyiTokenStatus(token: string): Promise<boolean> {
    try {
      const response = await request.get('/api/user/ruoyi_status', {
        params: { ruoyi_token: token }
      })
      
      return response.data.data?.valid === true
    } catch (error) {
      console.error('检查Ruoyi Token状态失败:', error)
      return false
    }
  }
  
  /**
   * 检查是否在iframe环境中
   */
  static isInIframe(): boolean {
    return window.self !== window.top
  }
  
  /**
   * 检查是否来自Ruoyi系统
   */
  static isFromRuoyi(): boolean {
    const referer = document.referrer.toLowerCase()
    return referer.includes('ruoyi') || 
           referer.includes('localhost:8080') || 
           this.getRuoyiTokenFromUrl() !== null
  }
  
  /**
   * 自动登录处理
   */
  static async autoLogin(): Promise<boolean> {
    try {
      // 1. 先从URL参数获取token
      let ruoyiToken = this.getRuoyiTokenFromUrl()
      
      // 2. 如果URL中没有，且在iframe中，尝试从父窗口获取
      if (!ruoyiToken && this.isInIframe()) {
        ruoyiToken = await this.getRuoyiTokenFromParent()
      }
      
      // 3. 如果有token，尝试登录
      if (ruoyiToken) {
        console.log('检测到Ruoyi Token，尝试自动登录...')
        
        // 验证token有效性
        const isValid = await this.checkRuoyiTokenStatus(ruoyiToken)
        if (!isValid) {
          ElMessage.error('Ruoyi Token无效或已过期')
          return false
        }
        
        // 执行登录
        const success = await this.loginWithRuoyiToken(ruoyiToken)
        if (success) {
          // 清除URL中的token参数
          this.clearTokenFromUrl()
        }
        return success
      }
      
      return false
    } catch (error) {
      console.error('自动登录失败:', error)
      return false
    }
  }
  
  /**
   * 清除URL中的token参数
   */
  static clearTokenFromUrl(): void {
    if (this.getRuoyiTokenFromUrl()) {
      const url = new URL(window.location.href)
      url.searchParams.delete('ruoyi_token')
      window.history.replaceState({}, '', url.toString())
    }
  }
  
  /**
   * 向父窗口发送消息
   */
  static postMessageToParent(message: any): void {
    if (window.parent !== window) {
      window.parent.postMessage(message, '*')
    }
  }
  
  /**
   * 通知父窗口登录状态
   */
  static notifyParentLoginStatus(success: boolean, userInfo?: any): void {
    this.postMessageToParent({
      type: 'MAXKB_LOGIN_STATUS',
      success: success,
      userInfo: userInfo
    })
  }
}
