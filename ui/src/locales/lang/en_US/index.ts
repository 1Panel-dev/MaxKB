import en from 'element-plus/es/locale/lang/en';
import components from './components';
import layout from './layout';
import views from './views';

export default {
    lang: 'English',
    layout,
    views,
    components,
    en,
    login: {
        authentication: 'Login Authentication',
        ldap: {
            title: 'LDAP Settings',
            address: 'LDAP Address',
            serverPlaceholder: 'Please enter LDAP address',
            bindDN: 'Bind DN',
            bindDNPlaceholder: 'Please enter Bind DN',
            password: 'Password',
            passwordPlaceholder: 'Please enter password',
            ou: 'User OU',
            ouPlaceholder: 'Please enter User OU',
            ldap_filter: 'User Filter',
            ldap_filterPlaceholder: 'Please enter User Filter',
            ldap_mapping: 'LDAP Attribute Mapping',
            ldap_mappingPlaceholder: 'Please enter LDAP Attribute Mapping',
            test: 'Test Connection',
            enableAuthentication: 'Enable LDAP Authentication',
            save: 'Save',
            testConnectionSuccess: 'Test Connection Success',
            testConnectionFailed: 'Test Connection Failed',
            saveSuccess: 'Save Success',
        }
    }
};
