import zhCn from 'element-plus/es/locale/lang/zh-cn'
import components from './components'
import layout from './layout'
import views from './views'

export default {
  lang: '简体中文',
  layout,
  views,
  components,
  zhCn,
  login: {
    authentication: '登录认证',
    ldap: {
      title: 'LDAP 设置',
      address: 'LDAP 地址',
      serverPlaceholder: '请输入LDAP 地址',
      bindDN: '绑定DN',
      bindDNPlaceholder: '请输入绑定 DN',
      password: '密码',
      passwordPlaceholder: '请输入密码',
      ou: '用户OU',
      ouPlaceholder: '请输入用户 OU',
      ldap_filter: '用户过滤器',
      ldap_filterPlaceholder: '请输入用户过滤器',
      ldap_mapping: 'LDAP 属性映射',
      ldap_mappingPlaceholder: '请输入 LDAP 属性映射',
      test: '测试连接',
      enableAuthentication: '启用 LDAP 认证',
      save: '保存',
      testConnectionSuccess: '测试连接成功',
      testConnectionFailed: '测试连接失败',
      saveSuccess: '保存成功'
    },
    cas: {
      title: 'CAS 设置',
      ldpUri: 'ldpUri',
      ldpUriPlaceholder: '请输入ldpUri',
      validateUrl: '验证地址',
      validateUrlPlaceholder: '请输入验证地址',
      redirectUrl: '回调地址',
      redirectUrlPlaceholder: '请输入回调地址',
      enableAuthentication: '启用CAS认证',
      saveSuccess: '保存成功',
      save: '保存'
    },
    oidc: {
      title: 'OIDC 设置',
      authEndpoint: '授权端地址',
      authEndpointPlaceholder: '请输入授权端地址',
      tokenEndpoint: 'Token端地址',
      tokenEndpointPlaceholder: '请输入Token端地址',
      userInfoEndpoint: '用户信息端地址',
      userInfoEndpointPlaceholder: '请输入用户信息端地址',
      clientId: '客户端ID',
      clientIdPlaceholder: '请输入客户端ID',
      clientSecret: '客户端密钥',
      clientSecretPlaceholder: '请输入客户端密钥',
      logoutEndpoint: '注销端地址',
      logoutEndpointPlaceholder: '请输入注销端地址',
      redirectUrl: '回调地址',
      redirectUrlPlaceholder: '请输入回调地址',
      enableAuthentication: '启用OIDC认证'
    },
    jump_tip: '即将跳转至认证源页面进行认证',
    jump: '跳转',
    oauth2: {
      title: 'OAUTH2 设置',
      authEndpoint: '授权端地址',
      authEndpointPlaceholder: '请输入授权端地址',
      tokenEndpoint: 'Token端地址',
      tokenEndpointPlaceholder: '请输入Token端地址',
      userInfoEndpoint: '用户信息端地址',
      userInfoEndpointPlaceholder: '请输入用户信息端地址',
      scope: '连接范围',
      scopePlaceholder: '请输入连接范围',
      clientId: '客户端ID',
      clientIdPlaceholder: '请输入客户端ID',
      clientSecret: '客户端密钥',
      clientSecretPlaceholder: '请输入客户端密钥',
      redirectUrl: '回调地址',
      redirectUrlPlaceholder: '请输入回调地址',
      filedMapping: '字段映射',
      filedMappingPlaceholder: '请输入字段映射',
      enableAuthentication: '启用OAUTH2认证',
      save: '保存',
      saveSuccess: '保存成功'
    }
  }
}
