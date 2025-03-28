export default {
  title: 'Function',
  internalTitle: 'Internal Function',
  added: 'Added',
  createFunction: 'Create Function',
  editFunction: 'Edit Function',
  copyFunction: 'Copy Function',
  importFunction: 'Import Function',
  searchBar: {
    placeholder: 'Search by function name'
  },
  setting: {
    disabled: 'Disabled'
  },
  tip: {
    saveMessage: 'Unsaved changes will be lost. Are you sure you want to exit?'
  },
  delete: {
    confirmTitle: 'Confirm deletion of function:',
    confirmMessage:
      'Deleting this function will cause errors in APP that reference it when they are queried. Please proceed with caution.'
  },
  disabled: {
    confirmTitle: 'Confirm disable function:',
    confirmMessage:
      'Disabling this function will cause errors in APP that reference it when they are queried. Please proceed with caution.'
  },
  functionForm: {
    title: {
      copy: 'Copy',
      baseInfo: 'Basic Information'
    },
    form: {
      functionName: {
        label: 'Name',
        name: 'Function Name',
        placeholder: 'Please enter the function name',
        requiredMessage: 'Please enter the function name'
      },
      functionDescription: {
        label: 'Description',
        placeholder: 'Please enter a description of the function'
      },
      permission_type: {
        label: 'Permissions',
        requiredMessage: 'Please select'
      },
      paramName: {
        label: 'Parameter Name',
        placeholder: 'Please enter the parameter name',
        requiredMessage: 'Please enter the parameter name'
      },
      dataType: {
        label: 'Data Type'
      },
      source: {
        label: 'Source',
        custom: 'Custom',
        reference: 'Reference Parameter'
      },
      required: {
        label: 'Required'
      },
      param: {
        paramInfo1: 'Displayed when using the function',
        paramInfo2: 'Not displayed when using the function',
        code: 'Content (Python)',
        selectPlaceholder: 'Please select parameter',
        inputPlaceholder: 'Please enter parameter values',
      },
      debug: {
        run: 'Run',
        output: 'Output',
        runResult: 'Run Result',
        runSuccess: 'Successful',
        runFailed: 'Run Failed'
      }
    }
  }
}
