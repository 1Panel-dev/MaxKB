import zhCn from 'element-plus/es/locale/lang/zh-cn';
import components from './components';
import layout from './layout';
import views from './views';

export default {
    lang: '简体中文',
    layout,
    views,
    components,
    zhCn,
    login: {
        authentication: '登录认证',
        ldap: {
            title: 'LDAP设置',
            address: 'LDAP地址',
            serverPlaceholder: '请输入LDAP地址',
            bindDN: '绑定DN',
            bindDNPlaceholder: '请输入绑定DN',
            password: '密码',
            passwordPlaceholder: '请输入密码',
            ou: '用户OU',
            ouPlaceholder: '请输入用户OU',
            ldap_filter: '用户过滤器',
            ldap_filterPlaceholder: '请输入用户过滤器',
            ldap_mapping: 'LDAP属性映射',
            ldap_mappingPlaceholder: '请输入LDAP属性映射',
            test: '测试连接',
            enableAuthentication: '启用LDAP认证',
            save: '保存',
            testConnectionSuccess: '测试连接成功',
            testConnectionFailed: '测试连接失败',
            saveSuccess: '保存成功',
        }
    }
};
