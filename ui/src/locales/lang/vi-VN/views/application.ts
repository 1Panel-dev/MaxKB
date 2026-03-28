export default {
  title: 'Agent',
  createApplication: 'Tạo tác nhân đơn giản',
  createWorkFlowApplication: 'Tạo tác nhân quy trình công việc',
  importApplication: 'Đại lý nhập khẩu',
  copyApplication: 'Đại lý sao chép',
  simple: 'SIMPLE',
  senior: 'WORKFLOW',
  simpleAgent: 'Đại lý đơn giản',
  AdvancedAgent: 'Đại lý nâng cao',
  simplePlaceholder: 'Nhanh chóng xây dựng các tác nhân thông minh với các chức năng cơ bản thông qua cài đặt biểu mẫu',
  advancedPlaceholder:
    'Sử dụng các phương pháp kéo và thả mã thấp, điều phối linh hoạt logic phức tạp và các tác nhân giàu tính năng',
  appTest: 'Xem trước gỡ lỗi',
  operation: {
    addModel: 'Thêm mô hình',
    toChat: 'Chat',
  },
  delete: {
    confirmTitle: 'Bạn có chắc chắn muốn xóa tác nhân này:',
    confirmMessage:
      'Việc xóa đại lý này sẽ không còn cung cấp dịch vụ của nó nữa. Hãy tiến hành thận trọng.',
    resourceCountMessage:
      'Tác nhân này được liên kết với tài nguyên {count} và sẽ không khả dụng sau khi xóa. Hãy tiến hành thận trọng.',
  },
  tip: {
    publishSuccess: 'Xuất bản thành công',
    ExportError: 'Xuất không thành công',
    professionalMessage:
      'Phiên bản cộng đồng hỗ trợ tối đa 5 đại lý. Nếu bạn cần thêm đại lý, vui lòng nâng cấp lên Phiên bản Chuyên nghiệp.',
    saveErrorMessage: 'Lưu không thành công, vui lòng kiểm tra thông tin bạn nhập hoặc thử lại sau',
    loadingErrorMessage: 'Không tải được cấu hình, vui lòng kiểm tra thông tin bạn nhập hoặc thử lại sau',
    noDocPermission: 'Không có quyền tạo tài liệu',
    confirmUse: 'Bạn có chắc chắn muốn sử dụng',
    overwrite: 'ghi đè quy trình công việc hiện tại',
  },

  form: {
    appName: {
      placeholder: 'Vui lòng nhập tên đại lý',
      requiredMessage: 'Tên đại lý là bắt buộc',
    },
    appDescription: {
      placeholder:
        'Mô tả kịch bản và cách sử dụng Tác nhân, ví dụ: Trợ lý XXX trả lời các câu hỏi của người dùng về việc sử dụng sản phẩm XXX',
    },
    appType: {
      simplePlaceholder: 'Thích hợp cho người mới bắt đầu tạo trợ lý.',
      workflowPlaceholder: 'Thích hợp cho người dùng nâng cao để tùy chỉnh quy trình làm việc của trợ lý',
    },
    appTemplate: {
      blankApp: {
        title: 'Đại lý trống',
      },
      assistantApp: {
        title: 'Trợ lý kiến ​​thức',
        description: 'Thích hợp cho người dùng nâng cao để tùy chỉnh quy trình làm việc của trợ lý',
      },
    },
    aiModel: {
      label: 'Mô hình AI',
      placeholder: 'Vui lòng chọn một mô hình AI',
    },
    roleSettings: {
      label: 'Lời nhắc hệ thống',
      placeholder:
        'Hệ thống nhắc nhở, bạn có thể tham chiếu các biến trong hệ thống: {data} là đoạn truy cập trong cơ sở kiến ​​thức; {question} là câu hỏi được người dùng đặt ra.',
      tooltip: 'Đặt vai trò hoặc hướng dẫn cho người mẫu tuân theo',
    },

    prompt: {
      label: 'Lời nhắc của người dùng',
      noReferences: '（Không có tài liệu tham khảo Kiến thức）',
      references: '(Kiến thức tham khảo)',
      placeholder:
        'Lời nhắc của người dùng, bạn có thể tham chiếu các biến trong hệ thống: {data} là đoạn truy cập trong cơ sở kiến ​​thức; {question} là câu hỏi được người dùng đặt ra',
      requiredMessage: 'Vui lòng nhập lời nhắc của người dùng',
      tooltip: 'Câu hỏi hoặc lệnh mà người dùng đặt ra cho mô hình',

      noReferencesTooltip:
        'Bằng cách điều chỉnh nội dung của lời nhắc, bạn có thể hướng dẫn hướng trò chuyện theo mô hình lớn. Lời nhắc này sẽ được cố định ở đầu ngữ cảnh. Các biến được sử dụng: {question} là câu hỏi do người dùng đặt ra.',
      referencesTooltip:
        'Bằng cách điều chỉnh nội dung của lời nhắc, bạn có thể hướng dẫn hướng trò chuyện theo mô hình lớn. Lời nhắc này sẽ được cố định ở đầu ngữ cảnh. Các biến được sử dụng: {data} mang thông tin đã biết từ kiến ​​thức; {question} là câu hỏi do người dùng đặt ra.',
      defaultPrompt: `Known information: {data}
        Question: {question}
         Response requirements:
         - Please use concise and professional language to answer the user's question.
         `,
    },
    historyRecord: {
      label: 'Lịch sử trò chuyện',
    },
    relatedKnowledge: {
      label: 'Kiến thức liên quan',
      placeholder: 'Những kiến ​​thức liên quan được hiển thị ở đây',
    },
    multipleRoundsDialogue: 'Đối thoại nhiều vòng',

    prologue: 'Prologue',
    defaultPrologue:
      'Hello, I am XXX Assistant. You can ask me questions about using XXX.\n- What are the main features of XXX?\n- Which LLM does XXX support?\n- What document types does XXX support?',
    problemOptimization: {
      label: 'Tối ưu hóa câu hỏi',
      tooltip:
        'Tối ưu hóa câu hỏi hiện tại dựa trên cuộc trò chuyện lịch sử để phù hợp hơn với các điểm kiến ​​thức.',
    },

    voiceInput: {
      label: 'Nhập bằng giọng nói',
      placeholder: 'Vui lòng chọn mô hình nhận dạng giọng nói',
      requiredMessage: 'Vui lòng chọn kiểu đầu vào giọng nói',
      autoSend: 'Gửi tự động',
    },
    voicePlay: {
      label: 'Phát lại giọng nói',
      placeholder: 'Vui lòng chọn mô hình tổng hợp giọng nói',
      requiredMessage: 'Vui lòng chọn kiểu phát lại giọng nói',
      autoPlay: 'Tự động phát lại',
      browser: 'Phát lại trình duyệt (miễn phí)',
      tts: 'Mô hình TTS',
      listeningTest: 'Preview',
    },
    reasoningContent: {
      label: 'Tư duy đầu ra',
      tooltip:
        "Hãy đặt nhãn tư duy dựa trên kết quả trả về của mô hình, nội dung ở giữa nhãn sẽ được ghi nhận là quá trình tư duy.",
      start: 'Start',
      end: 'End',
    },
    mcp_output_enable: 'Quá trình thực hiện đầu ra',
  },
  generateDialog: {
    label: 'Generate',
    generatePrompt: 'Tạo lời nhắc',
    placeholder: 'Vui lòng nhập chủ đề gợi ý',
    title: 'Lời nhắc được hiển thị ở đây',
    remake: 'Regenerate',
    stop: 'Dừng tạo',
    continue: 'Tiếp tục tạo',
    replace: 'Replace',
    exit: 'Bạn có chắc chắn muốn thoát và loại bỏ nội dung do AI tạo không?',
    loading: 'Generating...',
  },
  dialog: {
    addKnowledge: 'Thêm kiến ​​thức liên quan',
    addKnowledgePlaceholder: 'Kiến thức được chọn phải sử dụng cùng một mô hình nhúng',
    selectSearchMode: 'Chế độ truy xuất',
    vectorSearch: 'Tìm kiếm vectơ',
    vectorSearchTooltip:
      'Tìm kiếm vectơ là phương pháp truy xuất dựa trên tính toán khoảng cách vectơ, phù hợp với khối lượng dữ liệu lớn trong tri thức.',
    fullTextSearch: 'Tìm kiếm toàn văn',
    fullTextSearchTooltip:
      'Tìm kiếm toàn văn là phương pháp tra cứu dựa trên độ tương tự của văn bản, phù hợp với khối lượng dữ liệu nhỏ trong tri thức.',
    hybridSearch: 'Tìm kiếm kết hợp',
    hybridSearchTooltip:
      'Tìm kiếm kết hợp là phương pháp truy xuất dựa trên độ tương tự của cả vectơ và văn bản, phù hợp với khối lượng dữ liệu trung bình trong tri thức.',
    similarityThreshold: 'Độ tương tự cao hơn',
    similarityTooltip: 'Độ tương tự càng cao thì mối tương quan càng mạnh.',
    topReferences: 'Phân đoạn N hàng đầu',
    maxCharacters: 'Số ký tự tối đa trên mỗi tham chiếu',
    noReferencesAction: 'Khi không có tài liệu tham khảo kiến ​​thức',
    continueQuestioning: 'Tiếp tục đặt câu hỏi cho mẫu Al',
    provideAnswer: 'Chỉ định nội dung trả lời',
    designated_answer:
      'Xin chào, tôi là Trợ lý XXX. Kiến thức của tôi chỉ chứa thông tin liên quan đến sản phẩm XXX. Hãy viết lại câu hỏi của bạn.',
    defaultPrompt1:
      "Nội dung bên trong dấu ngoặc đơn () thể hiện câu hỏi của người dùng. Dựa vào ngữ cảnh, vui lòng suy đoán và hoàn thành câu hỏi của người dùng ({question}). Yêu cầu là xuất ra một câu hỏi hoàn chỉnh và đặt nó",
    defaultPrompt2: 'tag',
  },
  applicationAccess: {
    title: 'Quyền truy cập của bên thứ ba',
    wecom: 'WeCom',
    wecomTip: 'Tạo đại lý WeCom',
    wecomBot: 'Bot WeCom',
    wecomBotTip: 'Tạo Bot thông minh WeCom',
    dingtalk: 'DingTalk',
    dingtalkTip: 'Tạo đại lý DingTalk',
    wechat: 'WeChat',
    wechatTip: 'Tạo Đại lý WeChat',
    lark: 'Lark',
    larkTip: 'Tạo đại lý Lark',
    setting: 'Setting',
    callback: 'Địa chỉ gọi lại',
    callbackTip: 'Vui lòng điền địa chỉ gọi lại',
    wecomPlatform: 'Nền tảng mở WeCom',
    wechatPlatform: 'Nền tảng mở WeChat',
    dingtalkPlatform: 'Nền tảng mở DingTalk',
    larkPlatform: 'Nền tảng mở Lark',
    slack: 'Slack',
    slackTip: 'Tạo tác nhân Slack',
    wecomSetting: {
      title: 'Cấu hình WeCom',
      cropId: 'ID cắt',
      cropIdPlaceholder: 'Vui lòng nhập ID cây trồng',
      agentIdPlaceholder: 'Vui lòng nhập ID đại lý',
      secretPlaceholder: 'Vui lòng nhập bí mật',
      tokenPlaceholder: 'Vui lòng nhập mã thông báo',
      encodingAesKeyPlaceholder: 'Vui lòng nhập EncodingAESKey',
      authenticationSuccessful: 'Successful',
      urlInfo:
        '-Quản lý APP-Ứng dụng tự xây dựng-Nhận tin nhắn-Đặt "URL" mà API nhận được',
    },
    dingtalkSetting: {
      title: 'Cấu hình DingTalk',
      clientIdPlaceholder: 'Vui lòng nhập ID khách hàng',
      clientSecretPlaceholder: 'Vui lòng nhập bí mật của khách hàng',
      urlInfo:
        '-Trên trang robot, đặt "Chế độ nhận tin nhắn" thành chế độ HTTP và điền URL trên vào "Địa chỉ nhận tin nhắn"',
    },
    wechatSetting: {
      title: 'Cấu hình WeChat',
      appId: 'APP ID',
      appIdPlaceholder: 'Vui lòng nhập ID ứng dụng',
      appSecret: 'BÍ MẬT ỨNG DỤNG',
      appSecretPlaceholder: 'Vui lòng nhập BÍ MẬT ỨNG DỤNG',
      token: 'TOKEN',
      tokenPlaceholder: 'Vui lòng nhập TOKEN',
      aesKey: 'Khóa mã hóa tin nhắn',
      aesKeyPlaceholder: 'Vui lòng nhập khóa mã hóa tin nhắn',
      urlInfo:
        '-Cài đặt và Phát triển-Cấu hình cơ bản-"URL địa chỉ máy chủ" trong cấu hình máy chủ',
    },
    wecomBotSetting: {
      title: 'Cấu hình Bot WeCom',
      urlInfo: '-Công cụ quản lý-Smart Bot-Tạo Bot-API Chế độ Tạo "URL"',
    },
    larkSetting: {
      title: 'Cấu hình Lark',
      appIdPlaceholder: 'Vui lòng nhập ID ứng dụng',
      appSecretPlaceholder: 'Vui lòng nhập bí mật APP',
      verificationTokenPlaceholder: 'Vui lòng nhập mã thông báo xác minh',
      urlInfo:
        '-Sự kiện và cuộc gọi lại - cấu hình sự kiện - định cấu hình "địa chỉ yêu cầu" của phương thức đăng ký',
    },
    slackSetting: {
      title: 'Cấu hình lỏng lẻo',
      signingSecretPlaceholder: 'Vui lòng nhập bí mật ký',
      botUserTokenPlaceholder: 'Vui lòng nhập mã thông báo người dùng bot',
    },
    copyUrl: 'Sao chép liên kết và điền vào',
  },
  hitTest: {
    title: 'Kiểm tra truy xuất',
    text: 'Kiểm tra tác động của Kiến thức dựa trên văn bản truy vấn đã cho.',
    emptyMessage1: 'Kết quả kiểm tra truy xuất sẽ hiển thị ở đây',
    emptyMessage2: 'Không tìm thấy phần phù hợp',
  },
  publishTime: 'Thời gian xuất bản',
  publishStatus: 'Trạng thái xuất bản',
}
