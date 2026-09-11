/** 提供 Admin 忘记密码页面发送验证码与重置密码的接口。 */

import { post } from '../core/request'
import type { ResetPasswordRequest, SendEmailRequest } from '@/api/types/login'

/** 向指定邮箱发送用于重置密码的验证码。 */
const postSendVerificationCode = (email: string) => {
  return post<SendEmailRequest>('/user/send_email', { email, type: 'reset_password' })
}

/** 校验邮箱验证码并重置密码。 */
const postResetPassword = (request: ResetPasswordRequest) => {
  return post<ResetPasswordRequest>('/user/re_password', request)
}

export default { postResetPassword, postSendVerificationCode }
