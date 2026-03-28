export default {
  title: 'Knowledge',
  relatedApplications: 'Đại liên kết được xử lý',
  document_count: 'docs',
  relatedApp_count: 'link đại lý',
  setting: {
    vectorization: 'Vectorization',
    sync: 'Sync',
  },
  tip: {
    professionalMessage:
      'Hỗ trợ cộng đồng phiên bản tới 50 kiến ​​thức. Để có thêm kiến ​​thức, vui lòng nâng cấp lên phiên bản chuyên nghiệp.',
    syncSuccess: 'Đã gửi đồng bộ hóa tác vụ',
    updateModeMessage:
      'Sau khi sửa đổi mô hình tri thức, bạn cần vector hóa kiến ​​thức. Bạn có muốn tiếp tục tiết kiệm không?',
  },
  delete: {
    confirmTitle: 'Xác nhận xóa kiến ​​trúc:',
    confirmMessage1: 'Kiến thức này có liên quan đến',
    confirmMessage2: 'đại lý. Việc xóa nó sẽ không thể thay đổi được, vui lòng tiến hành một cách cẩn thận.',
    resourceCountMessage:
      'Kiến trúc này được liên kết với tài nguyên {count} và sẽ không có sẵn sau khi xóa. Hãy tiến hành cẩn thận.',
  },
  knowledgeType: {
    label: 'Type',
    generalKnowledge: 'Chung thức',
    webKnowledge: 'Web kiến ​​thức',
    larkKnowledge: 'Kiến thức chim sơn ca',
    workflowKnowledge: 'Kiến thức về quy trình làm việc',
    yuqueKnowledge: 'Yuque Protocol',
    generalInfo: 'Tải lên địa phương tài liệu',
    webInfo: 'Đồng bộ hóa văn bản dữ liệu từ một trang web',
    larkInfo: 'Xây dựng kiến ​​trúc thông tin tài liệu Lark',
    yuqueInfo: 'Xây dựng kiến ​​trúc thông tin tài liệu Yuque',
    createGeneralKnowledge: 'Tạo biểu thức',
    createWebKnowledge: 'Tạo web kiến ​​trúc',
    createLarkKnowledge: 'Tạo kiến ​​thức về Lark',
    createYuqueKnowledge: 'Tạo kiến ​​trúc Yuque',
    createWorkflowKnowledge: 'Tạo kiến ​​thức về quy trình làm việc',
    workflowInfo: 'Xây dựng nền tảng kiến ​​thức thông qua tùy chỉnh các phương pháp',
  },
  form: {
    knowledgeName: {
      label: 'Name',
      placeholder: 'Vui lòng nhập tên theo quy định',
      requiredMessage: 'Vui lòng nhập tên theo quy định',
    },
    knowledgeDescription: {
      label: 'Description',
      placeholder:
        'nội dung kiến ​​trúc. Mô tả chi tiết sẽ giúp AI hiểu nội dung tốt hơn, cải thiện độ chính xác của việc truy xuất nội dung và tỷ lệ Việt.',
      requiredMessage: 'Vui lòng nhập mô tả kiến ​​thức',
    },
    EmbeddingModel: {
      label: 'Nhúng mô hình',
      placeholder: 'Vui lòng chọn nhúng mô hình',
      requiredMessage: 'Vui lòng chọn nhúng mô hình',
    },

    source_url: {
      label: 'URL gốc của trang web',
      placeholder: 'Vui lòng nhập URL gốc của web',
      requiredMessage: 'Vui lòng nhập URL gốc của web',
    },
    selector: {
      label: 'Selector',
      placeholder: 'Mặc định là thân phận, có thể nhập .classname/#idname/tagname',
    },
    file_count_limit: {
      label: 'Tối đa số lượng tệp được tải lên cùng một lúc',
    },
    file_size_limit: {
      label: 'Tối đa kích thước của mỗi tài liệu (MB)',
      placeholder: 'Xuất đề dựa trên cấu hình máy chủ, nếu không thể khiến dịch vụ bị tắt',
    },
    appTemplate: {
      blank: {
        title: 'Tạo trống',
      },
      basic: {
        title: 'Basic base',
        description:
          'Hỗ trợ cơ sở quy trình mẫu cho bộ tệp cục bộ, tài liệu Lark và nguồn trang web dữ liệu',
      },
    },
  },

  ResultSuccess: {
    title: 'Kiến thức được tạo thành công',
    paragraph: 'Segments',
    paragraph_count: 'Segments',
    documentList: 'Danh sách tài liệu',
    loading: 'Importing',
    buttons: {
      toKnowledge: 'Đến danh sách kiến ​​trúc',
      toDocument: 'Đi tới Tài liệu',
    },
  },
  syncWeb: {
    title: 'Đồng bộ hóa kiến ​​thức',
    syncMethod: 'Phương pháp đồng bộ hóa',
    replace: 'Thay thế bộ đồng hóa',
    replaceText: 'Tìm lại tài liệu trên Web, thay thế tài liệu ở dạng kiến ​​trúc địa phương',
    complete: 'Đồng bộ hóa hoàn toàn',
    completeText: 'Xóa tất cả tài liệu trong bộ kiến ​​trúc và tìm lại trang web tài liệu',
    tip: 'Lưu ý: Tất cả các lần đồng bộ hóa sẽ xóa dữ liệu hiện có và tải lại dữ liệu mới. Hãy tiến hành cẩn thận.',
  },
  transform: {
    button: 'Convert',
    title: 'Chuyển đổi cơ sở dữ liệu về quy trình làm việc',
    message1:
      "Tại đây, bạn có thể chuyển đổi cơ sở kiến ​​trúc quy trình công việc của mình—một loại cơ sở mở và linh hoạt hơn cho phép bạn tự động điều phối toàn bộ quy trình từ nhiều nguồn cơ sở dữ liệu khác nhau sang viết kiến ​​thức thông qua các thao tác kéo dài và giải phóng, đáp ứng nhu cầu quản lý quy định cá nhân của doanh nghiệp bạn. Bạn có thể sử dụng các nguồn dữ liệu và công cụ có sẵn trong phần mềm của chúng tôi.",
    message2: 'Phương pháp xử lý mới sẽ được áp dụng cho tất cả các tài liệu được nhập sau đó.',
    tip: 'Lưu ý: Việc chuyển đổi không thể hoàn thành.',
    confirm:
      'Bạn có chắc chắn muốn chuyển đổi sang cơ sở quy trình làm việc không? Không thể hoàn thành thao tác này. Hãy tiến hành cẩn thận.',
  },
}
