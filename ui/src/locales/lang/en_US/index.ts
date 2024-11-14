import en from 'element-plus/es/locale/lang/en'
import components from './components'
import layout from './layout'
import views from './views'

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
      saveSuccess: 'Save Success'
    },
    cas: {
      title: 'CAS Settings',
      ldpUri: 'ldpUri',
      ldpUriPlaceholder: 'Please enter ldpUri',
      validateUrl: 'Validation Address',
      validateUrlPlaceholder: 'Please enter Validation Address',
      redirectUrl: 'Callback Address',
      redirectUrlPlaceholder: 'Please enter Callback Address',
      enableAuthentication: 'Enable CAS Authentication',
      saveSuccess: 'Save Success',
      save: 'Save'
    },
    oidc: {
      title: 'OIDC Settings',
      authEndpoint: 'Auth Endpoint',
      authEndpointPlaceholder: 'Please enter Auth Endpoint',
      tokenEndpoint: 'Token Endpoint',
      tokenEndpointPlaceholder: 'Please enter Token Endpoint',
      userInfoEndpoint: 'User Info Endpoint',
      userInfoEndpointPlaceholder: 'Please enter User Info Endpoint',
      clientId: 'Client ID',
      clientIdPlaceholder: 'Please enter Client ID',
      clientSecret: 'Client Secret',
      clientSecretPlaceholder: 'Please enter Client Secret',
      logoutEndpoint: 'Logout Endpoint',
      logoutEndpointPlaceholder: 'Please enter Logout Endpoint',
      redirectUrl: 'Redirect URL',
      redirectUrlPlaceholder: 'Please enter Redirect URL',
      enableAuthentication: 'Enable OIDC Authentication'
    },
    jump_tip: 'Jumping to the authentication source page for authentication',
    jump: 'Jump',
    oauth2: {
      title: 'OAUTH2 Settings',
      authEndpoint: 'Auth Endpoint',
      authEndpointPlaceholder: 'Please enter Auth Endpoint',
      tokenEndpoint: 'Token Endpoint',
      tokenEndpointPlaceholder: 'Please enter Token Endpoint',
      userInfoEndpoint: 'User Info Endpoint',
      userInfoEndpointPlaceholder: 'Please enter User Info Endpoint',
      scope: 'Scope',
      scopePlaceholder: 'Please enter Scope',
      clientId: 'Client ID',
      clientIdPlaceholder: 'Please enter Client ID',
      clientSecret: 'Client Secret',
      clientSecretPlaceholder: 'Please enter Client Secret',
      redirectUrl: 'Redirect URL',
      redirectUrlPlaceholder: 'Please enter Redirect URL',
      filedMapping: 'Field Mapping',
      filedMappingPlaceholder: 'Please enter Field Mapping',
      enableAuthentication: 'Enable OAUTH2 Authentication',
      save: 'Save',
      saveSuccess: 'Save Success'
    }
  }
}
