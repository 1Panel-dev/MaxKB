export default {
  title: '用戶管理',
  createUser: '建立用戶',
  editUser: '編輯用戶',
  roleSetting: '角色設定',
  addRole: '添加角色',
  setting: {
    updatePwd: '修改用戶密碼',
  },
  tip: {
    professionalMessage: '社群版最多支援 2 個使用者，如需擁有更多使用者，請升級為專業版。',
    updatePwdSuccess: '使用者密碼修改成功',
  },
  delete: {
    confirmTitle: '是否刪除該用戶？',
    confirmMessage:
      '刪除該用戶後，該使用者建立的所有資源（智能體、知識庫、模型）都不會被刪除，請謹慎操作。',
  },
  disabled: {
    confirmTitle: '是否停用工具？',
    confirmMessage: '停用後，引用該工具的智能體在查詢時會報錯，請謹慎操作。',
  },
  userForm: {
    nick_name: {
      label: '姓名',
      placeholder: '請輸入姓名',
      lengthMessage: '長度須介於 2 到 20 個字元之間',
    },

    phone: {
      label: '手機號碼',
      placeholder: '請輸入手機號碼',
      invalidMessage: '手機號碼格式不正確',
    },
  },
  source: {
    label: '用戶來源',
    local: '系統用戶',
     localCreate: '本地建立',
    wecom: '企業微信',
    lark: '飛書',
    dingtalk: '釘釘',
  },
  settingRole: '設定角色',
}
