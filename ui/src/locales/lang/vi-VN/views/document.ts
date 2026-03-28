export default {
  uploadDocument: 'Load tài liệu lên',
  importDocument: 'Nhập tài liệu',
  syncDocument: 'Đồng bộ hóa tài liệu',
  items: '',
  migrateDocument: 'Move to',
  setting: {
    migration: 'Move',
    cancelGenerateQuestion: 'Hủy việc tạo câu hỏi',
    cancelVectorization: 'Hủy véc tơ hóa',
    cancelGenerate: 'Hủy tạo',
    export: 'Xuất sang',
    download: 'Download',
    replace: 'Replace',
  },

  tip: {
    saveMessage: 'Những thay đổi hiện tại chưa được lưu. Xác nhận việc thoát?',
    cancelSuccess: 'Successful',
    sendMessage: 'Successful',
    vectorizationSuccess: 'Successful',
    nameMessage: 'Tài liệu tên không được để trống!',
    importMessage: 'Successful',
    migrationSuccess: 'Successful',
    replaceSuccess: 'Successful',
    fileLimitCountTip1: 'Tải lên tối đa mỗi lần',
    fileLimitCountTip2: 'files',
    fileLimitSizeTip1: 'mỗi tập tin không được vượt quá',
    toImportDocConfirm:
      'Hiện tại cơ sở dữ liệu hoạt động không thể xuất bản và không thể nhập tài liệu. Vui lòng xuất bản quy trình làm việc trước đó.',
     fileLimitSizeTip2: 'kích thước không được vượt quá',
  },
  upload: {
    selectFile: 'Choose file',
    selectFiles: 'Chọn thư mục',
    uploadMessage: 'Kéo và thả tập tin vào đây để tải lên hoặc',
    formats: 'Các định dạng được hỗ trợ:',
    requiredMessage: 'Vui lòng tải lên một tập tin',
    errorMessage1: 'File size vượt quá 100mb',
    errorMessage2: 'File Format không được hỗ trợ',
    errorMessage3: 'File không thể trống',
    errorMessage4: 'Có thể tải lên tối đa 50 tệp cùng một lúc',
    template: 'Template',
    download: 'Download',
  },

  fileType: {
    txt: {
      label: 'Bản văn bản',
      tip1: '1. Nên chuẩn hóa các dấu phân đoạn đánh dấu trong tệp trước khi tải lên.',
      tip2: '2. Có thể tải lên tối đa 50 tệp cùng một lúc, mỗi tệp không vượt quá 100 MB.',
    },
    table: {
      label: 'Table',
      tip1: '1. Nhấp để tải mẫu tương ứng và điền đầy đủ thông tin:',
      tip2: '2. Hàng đầu tiên phải là cột tiêu đề và cột tiêu đề phải là thuật ngữ có nghĩa thuật ngữ. Mỗi bản ghi trong bảng sẽ được coi là một đoạn phân tích.',
      tip3: '3. Mỗi trang tính trong bảng tệp được tải lên sẽ được coi là một tài liệu, với trang tính tên là tài liệu tên.',
      tip4: '4. Có thể tải lên tối đa 50 tệp cùng một lúc, mỗi tệp không vượt quá 100 MB.',
    },
    QA: {
      label: 'Cặp QA',
      tip1: '1. Nhấp để tải mẫu tương ứng và điền đầy đủ thông tin:',
      tip2: '2. Mỗi trang tính trong bảng tệp được tải lên sẽ được coi là một tài liệu, với trang tính tên là tài liệu tên.',
      tip3: '3. Có thể tải lên tối đa 50 tệp cùng một lúc, mỗi tệp không vượt quá 100 MB.',
    },
  },
  setRules: {
    title: {
      setting: 'Đặt đoạn quy tắc',
      preview: 'Preview',
    },
    intelligent: {
      label: 'Phân đoạn tự động ( Khuyến nghị)',
      text: 'Nếu bạn không chắc chắn về cách đặt quy tắc phân đoạn, bạn nên sử dụng tự động phân đoạn.',
    },
    advanced: {
      label: 'Cao phân đoạn nâng cao',
      text: 'Người dùng có thể tùy chỉnh các dấu phân tích, phân đoạn dài và quy tắc làm sạch dựa trên tài liệu tiêu chuẩn.',
    },
    patterns: {
      label: 'Dấu vết phân đoạn',
      tooltip:
        'Phân vùng đệ quy theo thứ tự đã chọn các ký hiệu. Nếu kết quả phân tích quá dài, nó sẽ bị cắt theo đoạn dài.',
      placeholder: 'Vui lòng chọn',
    },
    limit: {
      label: 'Đoạn dài',
    },
    with_filter: {
      label: 'Tự động làm sạch',
      text: 'Loại bỏ các ký hiệu, dấu cách, dòng trống và từ vòng lặp tab trùng lặp.',
    },
    checkedConnect: {
      label: 'Thêm phần "Câu hỏi liên quan" cho các cặp QA dựa trên câu hỏi trong quá trình nhập.',
    },
  },
  buttons: {
    import: 'Start input',
    preview: 'Apply',
    continueImporting: 'Tiếp tục nhập tài liệu',
  },
  tag: {
    label: 'Quản lý thẻ',
    key: 'Tag',
    value: 'Value',
    addTag: 'Thêm thẻ',
    noTag: 'Không có thẻ',
    relate: 'Link',
    unrelate: 'Unlink',
    relatedDoc: 'Tài liệu được liên kết',
    unrelatedDoc: 'Tài liệu đã hủy liên kết',
    setting: 'Cài đặt thẻ',
    create: 'Tạo thẻ',
    createValue: 'Tạo thẻ giá trị',
    edit: 'Chỉnh sửa thẻ chỉnh sửa',
    editValue: 'Chỉnh sửa thẻ giá trị',
    deleteConfirm: 'Xác nhận đã xóa thẻ:',
    deleteTip:
      'Sau khi xóa, tài nguyên sử dụng thẻ này sẽ bị xóa thẻ. Hãy tiến hành cẩn thận!',
    requiredMessage1: 'Vui lòng nhập thẻ',
    requiredMessage2: 'Vui lòng nhập một giá trị',
    requiredMessage3: 'Vui lòng nhập thẻ hoặc giá trị',
  },
  table: {
    name: 'Tài liệu tên',
    char_length: 'Character',
    paragraph: 'Segment',
    all: 'All',
    updateTime: 'Cập nhật thời gian',
  },
  fileStatus: {
    label: 'File status',
    SUCCESS: 'Success',
    FAILURE: 'Failure',
    EMBEDDING: 'Indexing',
    PENDING: 'Queuing',
    GENERATE: 'Generating',
    SYNC: 'Syncing',
    finish: 'Finish',
  },
  enableStatus: {
    label: 'Status',
    enable: 'Enabled',
    close: 'Disabled',
  },
  sync: {
    label: 'Sync',
    confirmTitle: 'Xác nhận việc đồng bộ hóa tài liệu?',
    confirmMessage1:
      'Đồng bộ hóa sẽ xóa dữ liệu hiện có và truy xuất dữ liệu mới. Hãy tiến hành cẩn thận.',
    confirmMessage2: 'Không thể đồng bộ hóa, trước tiên hãy đặt tài liệu URL.',
    successMessage: 'Successful',
  },
  delete: {
    confirmTitle1: 'Xác nhận xóa hàng loạt',
    confirmTitle2: 'tài liệu?',
    confirmMessage:
      'Các đoạn trong tài liệu đã chọn cũng sẽ bị xóa. Hãy tiến hành cẩn thận.',
    successMessage: 'Successful',
    confirmTitle3: 'Xác nhận đã xóa tài liệu:',
    confirmMessage1: 'Theo tài liệu này',
    confirmMessage2: 'Tất cả các đoạn sẽ bị xóa, vui lòng thực hiện một cách cẩn thận.',
  },
  form: {
    source_url: {
      label: 'Tài liệu URL',
      placeholder: 'Nhập tài liệu URL, mỗi URL một dòng. URL không xác định chính xác sẽ gây ra lỗi nhập.',
      requiredMessage: 'Vui lòng nhập tài liệu URL',
    },
    selector: {
      label: 'Selector',
      placeholder: 'Mặc định là body, bạn có thể nhập .classname/#idname/tagname',
    },
    hit_handling_method: {
      label: 'Retrieve-Respond',
      tooltip: 'Khi người dùng đặt câu hỏi, hãy xử lý các đoạn trùng lặp theo phương thức đã đặt.',
    },
    similarity: {
      label: 'So sánh độ cao hơn',
      placeholder: 'Trả lời trực tiếp về phân khúc nội dung',
      requiredMessage: 'Vui lòng nhập giá trị tương ứng',
    },
    allow_download: {
      label: 'Cho phép tải xuống trong cơ sở dữ liệu nguồn',
    },
  },
  hitHandlingMethod: {
    optimization: 'Model tối ưu hóa',
    directly_return: 'Trả lời trực tiếp',
  },
  movePosition: {
    title: 'Di chuyển vị trí',
    moveUp: 'Move up',
    moveDown: 'Di chuyển xuống',
    moveTop: 'Di chuyển lên trên',
    moveBottom: 'Di chuyển xuống dưới',
  },
  generateQuestion: {
    title: 'Tạo câu hỏi',
    successMessage: 'Successful',
    tip1: '{data} trong lời nhắc là trình quản lý nội dung được phân đoạn, được thay thế bằng nội dung được phân đoạn khi được thực thi và gửi đến AI mô hình;',
    tip2: 'Mô hình AI tạo ra các câu hỏi có liên quan dựa trên nội dung được phân đoạn. Vui lòng đặt các câu hỏi được tạo trong',
    tip3: 'các thẻ và hệ thống sẽ tự động liên kết các câu hỏi trong các thẻ này;',
    tip4: 'Kích hoạt ứng dụng tạo phụ thuộc vào mô hình và lời nhắc. Người dùng có thể điều chỉnh để đạt được hiệu quả tốt nhất.',
    prompt1:
      'Content: {data}\n \n Please summarize the above and generate 5 questions based on the summary. \nAnswer requirements: \n - Please output only questions; \n - Please place each question in',
    prompt2: 'tag.',
  },
  feishu: {
    selectDocument: 'Choose the document',
    tip1: 'Chỉ có tài liệu và bảng được hỗ trợ. Tài liệu sẽ được phân tích dựa trên tiêu đề và các bảng sẽ được chuyển đổi sang Markdown định dạng trước khi phân đoạn.',
    tip2: 'Trước khi nhập tài liệu, nên chuẩn hóa các tài liệu phân đoạn đánh dấu.',
  },
}
