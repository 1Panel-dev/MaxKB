export default {
  title: 'Tool',
  all: 'All',
  createTool: 'Tạo công cụ',
  editTool: 'Công cụ chỉnh sửa',
  copyTool: 'Công cụ sao chép',
  importTool: 'Công cụ nhập',
  settingTool: 'Đặt công cụ',
  updatedVersion: 'Phiên bản cập nhật',
  toolWorkflow: {
    creatToolWorkflow: 'Tạo quy trình làm việc',
    toActiveTip: 'Không thể kích hoạt. Vui lòng xuất bản quy trình làm việc trước.',
    debugResult: 'Kết quả gỡ lỗi',
  },
  dataSource: {
    title: 'Nguồn dữ liệu',
    createDataSource: 'Tạo nguồn dữ liệu',
    editDataSource: 'Chỉnh sửa nguồn dữ liệu',
    copyDataSource: 'Sao chép nguồn dữ liệu',
    selectDataSource: 'Chọn nguồn dữ liệu',
    requiredMessage: 'Vui lòng chọn nguồn dữ liệu',
  },
  toolStore: {
    title: 'Cửa hàng dụng cụ',
    createFromToolStore: 'Tạo từ Cửa hàng Công cụ',
    internal: 'Hệ thống tích hợp',
    recommend: 'Recommended',
    webSearch: 'Tìm kiếm trên web',
    databaseQuery: 'Truy vấn cơ sở dữ liệu',
    image: 'Image',
    developer: 'Developer',
    communication: 'Communication',
    searchResult: '{count} kết quả tìm kiếm cho',
    confirmTip: 'Bạn có chắc chắn cập nhật công cụ:',
    updateStoreToolMessage: 'Việc cập nhật các công cụ có thể ảnh hưởng đến tài nguyên đang sử dụng, vì vậy hãy thận trọng.',
  },
  mcp: {
    title: 'Dịch vụ MCP',
    label: 'Cấu hình máy chủ MCP',
    placeholder: 'Vui lòng nhập cấu hình máy chủ MCP',
    tip: 'Chỉ hỗ trợ các phương thức gọi HTTP SSE và Streamable',
    requiredMessage: 'Vui lòng nhập Cấu hình máy chủ MCP',
    createMcpTool: 'Tạo MCP',
    editMcpTool: 'Chỉnh sửa MCP',
    copyMcpTool: 'Sao chép MCP',
    mcpConfig: 'Cấu hình dịch vụ MCP',
  },
  skill: {
    title: 'Capabilities',
    copySkillTool: 'Sao chép kỹ năng',
    createSkillTool: 'Tạo kỹ năng',
    editSkillTool: 'Chỉnh sửa kỹ năng',
    initParamPlaceholder: 'Các thông số cần cấu hình khi kích hoạt kỹ năng',
    skillFile: 'Tệp kỹ năng',
    reUpload: 'Re-upload',
  },
  tip: {
    saveMessage: 'Những thay đổi chưa được lưu sẽ bị mất. Bạn có chắc chắn muốn thoát không?',
  },
  delete: {
    confirmTitle: 'Xác nhận xóa công cụ:',
    confirmMessage:
      'Việc xóa công cụ này sẽ gây ra lỗi trong tác nhân tham chiếu đến nó khi chúng được truy vấn. Hãy tiến hành thận trọng.',
    resourceCountMessage:
      'Công cụ này được liên kết với tài nguyên {count} và sẽ không khả dụng sau khi xóa. Hãy tiến hành thận trọng.',
  },
  disabled: {
    confirmTitle: 'Xác nhận vô hiệu hóa công cụ:',
    confirmMessage:
      'Việc tắt công cụ này sẽ gây ra lỗi trong tác nhân tham chiếu đến nó khi chúng được truy vấn. Hãy tiến hành thận trọng.',
  },

  form: {
    toolName: {
      label: 'Tên công cụ',
      placeholder: 'Vui lòng nhập tên công cụ',
      requiredMessage: 'Vui lòng nhập tên công cụ',
    },
    mcpName: {
      placeholder: 'Vui lòng nhập tên MCP',
      requiredMessage: 'Vui lòng nhập tên MCP',
    },
    workflowName: {
      label: 'Tên quy trình làm việc',
      placeholder: 'Vui lòng nhập tên quy trình làm việc',
      requiredMessage: 'Vui lòng nhập tên quy trình làm việc',
    },
    paramName: {
      label: 'Tên thông số',
      placeholder: 'Vui lòng nhập tên tham số',
      requiredMessage: 'Vui lòng nhập tên tham số',
    },
    dataType: {
      label: 'Kiểu dữ liệu',
    },
    source: {
      label: 'Source',
      reference: 'Tham số tham chiếu',
    },
    param: {
      paramInfo1: 'Hiển thị khi sử dụng công cụ',
      paramInfo2: 'Không hiển thị khi sử dụng công cụ',
      code: 'Nội dung (Python)',
      selectPlaceholder: 'Vui lòng chọn tham số',
      inputPlaceholder: 'Vui lòng nhập giá trị tham số',
    },
    debug: {
      run: 'Run',
      output: 'Output',
      runResult: 'Chạy kết quả',
      runSuccess: 'Successful',
      runFailed: 'Chạy không thành công',
    },
  },
}
