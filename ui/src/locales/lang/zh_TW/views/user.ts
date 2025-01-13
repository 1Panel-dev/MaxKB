export default {
  title: '使用者管理',
  createUser: '建立使用者',
  editUser: '編輯使用者',
  setting: {
    updatePwd: '修改使用者密碼'
  },
  tip: {
    professionalMessage: '社群版最多支援 2 個使用者，如需擁有更多使用者，請升級為專業版。',
    updatePwdSuccess: '使用者密碼修改成功'
  },
  delete: {
    confirmTitle: '是否刪除該使用者？',
    confirmMessage:
      '刪除該使用者後，該使用者建立的所有資源（應用、知識庫、模型）都會被刪除，請謹慎操作。'
  },
  disabled: {
    confirmTitle: '是否停用函數？',
    confirmMessage: '停用後，引用該函數的應用在查詢時會報錯，請謹慎操作。'
  },
  userForm: {
    form: {
      username: {
        label: '使用者名稱',
        placeholder: '請輸入使用者名稱',
        requiredMessage: '請輸入使用者名稱',
        lengthMessage: '長度須介於 6 到 20 個字元之間'
      },
      nick_name: {
        label: '姓名',
        placeholder: '請輸入姓名'
      },
      email: {
        label: '電子信箱',
        placeholder: '請輸入電子信箱',
        requiredMessage: '請輸入電子信箱'
      },
      phone: {
        label: '手機號碼',
        placeholder: '請輸入手機號碼'
      },
      password: {
        label: '登入密碼',
        placeholder: '請輸入密碼',
        requiredMessage: '請輸入密碼',
        lengthMessage: '長度須介於 6 到 20 個字元之間'
      },
      new_password: {
        label: '新密碼',
        placeholder: '請輸入新密碼',
        requiredMessage: '請輸入新密碼'
      },
      re_password: {
        label: '確認密碼',
        placeholder: '請輸入確認密碼',
        requiredMessage: '請輸入確認密碼',
        validatorMessage: '密碼不一致'
      }
    }
  },
  source: {
    label: '使用者類型',
    local: '系統使用者',
    wecom: '企業微信',
    lark: '飛書',
    dingtalk: '釘釘'
  }
}
