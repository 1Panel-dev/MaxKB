export default {
  node: 'Node',
  nodeName: 'Tên nút',
  baseComponent: 'Basic',
  nodeSetting: 'Cài đặt nút',
  workflow: 'Workflow',
  knowledgeWorkflow: 'Quy trình làm việc kiến ​​thức',
  info: {
    previewVersion: 'Phiên bản xem trước:',
    saveTime: 'Đã lưu lần cuối:',
  },
  operation: {
    toImportDoc: 'Chuyển đến Chứng từ nhập khẩu',
    importWorkflow: 'Nhập quy trình làm việc',
    exportWorkflow: 'Xuất quy trình công việc',
  },
  setting: {
    restoreVersion: 'Khôi phục phiên bản trước"',
    restoreCurrentVersion: 'Khôi phục về phiên bản này',
    addComponent: 'Add',
    releaseHistory: 'Lịch sử phát hành',
    autoSave: 'Tự động lưu',
    latestRelease: 'Bản phát hành mới nhất',
    copyParam: 'Sao chép thông số',
    debug: 'Run',
    exit: 'Exit',
    exitSave: 'Lưu & Thoát',
    templateCenter: 'Trung tâm mẫu',
  },
  tip: {
    noData: 'Không tìm thấy kết quả liên quan',
    nameMessage: 'Tên không được để trống!',
    onlyRight: 'Kết nối chỉ có thể được thực hiện từ neo bên phải',
    notRecyclable: 'Kết nối vòng lặp không được phép',
    onlyLeft: 'Chỉ có thể thực hiện kết nối với neo bên trái',
    applicationNodeError: 'Đại lý này không có sẵn',
    toolNodeError: 'Nút công cụ này không có sẵn',
    repeatedNodeError: 'Một nút có tên này đã tồn tại',
    cannotCopy: 'Không thể sao chép',
    copyError: 'Nút đã được sao chép',
    paramErrorMessage: 'Tham số đã tồn tại:',
    saveMessage: 'Những thay đổi hiện tại chưa được lưu. Lưu trước khi thoát?',
    searchPlaceholder: 'Vui lòng nhập tên nút',
  },
  delete: {
    confirmTitle: 'Xác nhận xóa nút này?',
    deleteMessage: 'Nút này không thể bị xóa',
  },
  control: {
    zoomOut: 'Thu nhỏ',
    zoomIn: 'Phóng to',
    fitView: 'Vừa với màn hình',
    retract: 'Thu gọn tất cả',
    extend: 'Mở rộng tất cả',
    beautify: 'Auto-Arrange',
  },
  variable: {
    global: 'Biến toàn cục',
    chat: 'Biến trò chuyện',
    Referencing: 'Biến tham chiếu',
    ReferencingRequired: 'Biến tham chiếu là bắt buộc',
    ReferencingError: 'Biến tham chiếu không hợp lệ',
    NoReferencing: 'Biến tham chiếu không tồn tại',
    placeholder_key: 'Nhập phím',
    placeholder: 'Vui lòng chọn một biến',
    inputPlaceholder: 'Vui lòng nhập biến',
    loop: 'Biến vòng lặp',
  },
  condition: {
    title: 'Điều kiện thực hiện',
    front: 'Precondition',
    AND: 'All',
    OR: 'Any',
    text: 'Sau khi nút được kết nối được thực thi, hãy thực thi nút hiện tại',
  },
  validate: {
    startNodeRequired: 'Nút bắt đầu là bắt buộc',
    startNodeOnly: 'Chỉ cho phép một nút bắt đầu',
    baseNodeRequired: 'Nút thông tin cơ sở là bắt buộc',
    baseNodeOnly: 'Chỉ cho phép một nút thông tin cơ sở',
    notInWorkFlowNode: 'Nút không có trong quy trình làm việc',
    noNextNode: 'Nút tiếp theo không tồn tại',
    nodeUnavailable: 'Nút không có sẵn',
    needConnect1: 'Nhánh của nút cần được kết nối',
    cannotEndNode: 'Nút này không thể được sử dụng làm nút cuối',
    loopNodeBreakNodeRequired: 'Vòng lặp không dây phải có nút Break',
  },
  nodes: {
    knowledgeWriteNode: {
      label: 'Kiến thức viết',
      text: 'Viết danh sách đoạn đầu vào vào cơ sở kiến ​​thức hiện tại và hoàn thành quá trình vector hóa',
    },
    dataSourceWebNode: {
      label: 'Trang web',
      text: 'Nhập URL gốc để tự động thu thập dữ liệu web (liên kết đơn tương ứng với một tài liệu), xuất danh sách các tài liệu có nội dung',
      field_label: 'Danh sách tài liệu',
    },
    dataSourceLocalNode: {
      label: 'Tệp cục bộ',
      text: 'Tải lên các tài liệu cục bộ, danh sách tài liệu đầu ra (nội dung chưa được phân tích cú pháp, cần được sử dụng với nút "Trích xuất nội dung tài liệu" để phân tích cú pháp)',
      fileList: 'Danh sách tập tin',
      fileFormat: {
        label: 'Định dạng tệp được hỗ trợ',
        requiredMessage: 'Vui lòng chọn định dạng tệp',
      },
      maxFileNumber: {
        label: 'Số lượng tệp tối đa cho mỗi lần tải lên',
      },
      maxFileCountNumber: {
        label: 'Kích thước tối đa cho mỗi tệp (MB)',
      },
    },
    classify: {
      aiCapability: 'Khả năng AI',
      businessLogic: 'Logic kinh doanh',
      other: 'Other',
      dataProcessing: 'Xử lý dữ liệu',
    },
    startNode: {
      label: 'Start',
      question: 'Câu hỏi của người dùng',
      currentTime: 'Thời gian hiện tại',
    },
    baseNode: {
      fileUpload: {
        label: 'Tải lên tệp',
        tooltip: 'Khi được bật, trang Hỏi đáp sẽ hiển thị nút tải tệp lên.',
      },
      FileUploadSetting: {
        title: 'Cài đặt tải lên tệp',
        maxFiles: 'Số lượng tệp tối đa cho mỗi lần tải lên',
        fileLimit: 'Kích thước tối đa cho mỗi tệp (MB)',
        fileUploadType: {
          label: 'Các loại tệp được phép tải lên',
          documentText: 'Yêu cầu nút "Trích xuất nội dung tài liệu" để phân tích nội dung tài liệu',
          imageText: 'Yêu cầu nút "Hiểu hình ảnh" để phân tích nội dung hình ảnh',
          videoText: 'Yêu cầu nút "Hiểu video" để phân tích nội dung video',
          audioText: 'Yêu cầu nút "Chuyển giọng nói thành văn bản" để phân tích nội dung âm thanh',
          uploadMethod: 'Phương pháp tải lên',
        },
      },
    },
    KnowledgeBaseNode: {
      DocumentSetting: 'Cài đặt xử lý tài liệu',
    },
    aiChatNode: {
      label: 'Trò chuyện AI',
      text: 'Trò chuyện với mô hình AI',
      answer: 'Nội dung AI',
      returnContent: {
        label: 'Trả lại nội dung',
        tooltip: `If turned off, the content of this node will not be output to the user.
                  If you want the user to see the output of this node, please turn on the switch.`,
      },
      defaultPrompt: 'Thông tin đã biết',
      think: 'Quá trình tư duy',
      historyMessage: 'Bản ghi trò chuyện lịch sử',
    },
    searchKnowledgeNode: {
      label: 'Truy xuất kiến ​​thức',
      text: 'Cho phép bạn truy vấn nội dung văn bản liên quan đến câu hỏi của người dùng từ Kiến thức',
      paragraph_list: 'Danh sách các phân đoạn được truy xuất',
      is_hit_handling_method_list: 'Danh sách các phân khúc đáp ứng tiêu chí phản hồi trực tiếp',
      result: 'Kết quả tìm kiếm',
      directly_return: 'Nội dung của các phân đoạn đáp ứng tiêu chí phản hồi trực tiếp',
      searchParam: 'Tham số truy xuất',
      showKnowledge: {
        label: 'Kết quả được hiển thị trong nguồn kiến ​​thức',
        requiredMessage: 'Hãy đặt thông số',
      },
      searchQuestion: {
        label: 'Question',
        placeholder: 'Vui lòng chọn câu hỏi tìm kiếm',
        requiredMessage: 'Vui lòng chọn câu hỏi tìm kiếm',
      },
    },
    searchDocumentNode: {
      label: 'Truy xuất thẻ tài liệu',
      text: 'Tìm kiếm tài liệu đáp ứng điều kiện dựa trên nhãn tài liệu trong phạm vi tìm kiếm được chỉ định',
      selectKnowledge: 'Phạm vi tìm kiếm',
      searchSetting: 'Cài đặt tìm kiếm',
      custom: 'Manual',
      customTooltip: 'Đặt điều kiện lọc thẻ theo cách thủ công',
      auto: 'Automatic',
      autoTooltip: 'Tự động lọc điều kiện cài đặt thẻ dựa trên câu hỏi tìm kiếm',
      documentList: 'Danh sách tài liệu',
      knowledgeList: 'Danh sách cơ sở kiến ​​thức',
      result: 'Kết quả tìm kiếm',
      searchParam: 'Thông số tìm kiếm',
      select_variable: 'Chọn biến',
      valueMessage: `Value or name `,

      searchQuestion: {
        label: 'Tìm kiếm câu hỏi',
        placeholder: 'Vui lòng chọn câu hỏi tìm kiếm',
        requiredMessage: 'Vui lòng chọn câu hỏi tìm kiếm',
      },
    },
    questionNode: {
      label: 'Tối ưu hóa câu hỏi',
      text: 'Tối ưu hóa và cải thiện câu hỏi hiện tại dựa trên bản ghi trò chuyện lịch sử để phù hợp hơn với các phân đoạn kiến ​​thức',
      result: 'Kết quả câu hỏi được tối ưu hóa',
      systemDefault: `#Role
You are a master of problem optimization, adept at accurately inferring user intentions based on context and optimizing the questions raised by users.

##Skills
###Skill 1: Optimizing Problems
2. Receive user input questions.
3. Carefully analyze the meaning of the problem based on the context.
4. Output optimized problems.

##Limitations:
-Only return the optimized problem without any additional explanation or clarification.
-Ensure that the optimized problem accurately reflects the original problem intent and does not alter the original intention.`,
    },
    conditionNode: {
      label: 'Chi nhánh có điều kiện',
      text: 'Kích hoạt các nút khác nhau dựa trên điều kiện',
      branch_name: 'Tên chi nhánh',
      conditions: {
        label: 'Conditions',
        info: 'Đáp ứng những điều sau đây',
        requiredMessage: 'Hãy chọn điều kiện',
      },
      valueMessage: 'Vui lòng nhập một giá trị',
      addCondition: 'Thêm điều kiện',
      addBranch: 'Thêm chi nhánh',
    },
    replyNode: {
      label: 'Trả lời được chỉ định',
      text: 'Chỉ định nội dung trả lời, các biến tham chiếu sẽ được chuyển đổi thành chuỗi cho đầu ra',
      replyContent: 'Trả lời nội dung',
    },
    rerankerNode: {
      label: 'Thu hồi đa đường',
      text: 'Sử dụng mô hình xếp hạng lại để tinh chỉnh kết quả truy xuất từ ​​nhiều nguồn kiến ​​thức',
      result_list: 'Danh sách kết quả được xếp hạng lại',
      result: 'Kết quả xếp hạng lại',
      rerankerContent: {
        label: 'Xếp hạng lại nội dung',
        requiredMessage: 'Vui lòng chọn nội dung sắp xếp lại',
      },
      higher: 'Higher',
      ScoreTooltip: 'Điểm càng cao thì mức độ liên quan càng mạnh.',
      max_paragraph_char_number: 'Ký tự tối đa',
      reranker_model: {
        label: 'Rerank',
        placeholder: 'Vui lòng chọn thứ hạng lại',
      },
    },
    formNode: {
      label: 'Nhập biểu mẫu',
      text: 'Thu thập ý kiến ​​đóng góp của người dùng trong quá trình hỏi đáp và sử dụng nó trong các quy trình tiếp theo',
      form_content_format1: 'Xin chào, vui lòng điền vào mẫu dưới đây:',
      form_content_format2: 'Nhấp vào nút [Gửi] sau khi điền xong.',
      form_data: 'Tất cả nội dung biểu mẫu',
      formContent: {
        label: 'Nội dung đầu ra của biểu mẫu',
        requiredMessage:
          'Vui lòng đặt nội dung đầu ra của nút này, { form } là phần giữ chỗ cho biểu mẫu.',
        tooltip: 'Xác định nội dung đầu ra của nút này. { form } là trình giữ chỗ cho biểu mẫu',
      },
      formAllContent: 'Tất cả nội dung biểu mẫu',
      formSetting: 'Cấu hình biểu mẫu',
    },
    documentExtractNode: {
      label: 'Trích xuất nội dung tài liệu',
      text: 'Phân tích tài liệu đầu vào để xuất nội dung tài liệu có cấu trúc',
      content: 'Nội dung tài liệu',
    },
    documentSplitNode: {
      label: 'Tách tài liệu',
      text: 'Phân chia nội dung tài liệu đầu vào theo chiến lược phân đoạn, xuất ra danh sách các văn bản được phân đoạn',
      paragraphList: 'Danh sách các phân đoạn được chia',
      splitStrategy: {
        label: 'Chiến lược chia tách',
        placeholder: 'Vui lòng chọn chiến lược chia tách',
        requiredMessage: 'Vui lòng chọn chiến lược chia tách',
      },
      chunk_length: {
        label: 'Chiều dài đoạn',
        tooltip1: 'Mục tiêu cốt lõi là cân bằng độ chính xác truy xuất và hiệu quả truy xuất',
        tooltip2:
          'Tránh phân đoạn quá ngắn: Một phân đoạn duy nhất <50 ký tự có thể dẫn đến phân mảnh ngữ nghĩa, có khả năng không khớp với mục đích truy vấn trong quá trình truy xuất do thiếu ngữ cảnh.',
        tooltip3:
          'Tránh phân đoạn quá mức: Một khối đơn vượt quá 500 ký tự sẽ làm tăng thông tin dư thừa, giảm độ chính xác khi truy xuất và tiêu tốn nhiều tài nguyên lưu trữ và tính toán hơn.',
      },
      title1: 'Tiêu đề phân đoạn được đặt làm câu hỏi liên quan của phân đoạn',
      title2: 'Tên tài liệu được đặt làm câu hỏi liên quan của phân đoạn',
    },
    imageUnderstandNode: {
      label: 'Hiểu hình ảnh',
      text: 'Phân tích hình ảnh để xác định đồ vật, cảnh vật và đưa ra câu trả lời',
      answer: 'Nội dung AI',
      model: {
        label: 'Mô hình tầm nhìn',
        requiredMessage: 'Vui lòng chọn một mô hình tầm nhìn',
      },
      image: {
        label: 'Chọn hình ảnh',
        requiredMessage: 'Vui lòng chọn một hình ảnh',
      },
    },
    videoUnderstandNode: {
      label: 'Hiểu video',
      text: 'Xác định các đối tượng, cảnh và thông tin khác trong video để trả lời câu hỏi của người dùng',
      answer: 'Nội dung phản hồi AI',
      model: {
        label: 'Mô hình tầm nhìn',
        requiredMessage: 'Vui lòng chọn một mô hình tầm nhìn',
      },
      video: {
        label: 'Chọn Video',
        requiredMessage: 'Vui lòng chọn một video',
      },
    },
    variableAssignNode: {
      label: 'Gán biến',
      text: 'Cập nhật giá trị của biến toàn cục',
      assign: 'Đặt giá trị',
    },
    variableAggregationNode: {
      label: 'Tập hợp biến',
      text: 'Các biến tổng hợp của từng nhóm theo chiến lược tổng hợp',
      Strategy: 'Chiến lược tổng hợp',
      placeholder: 'Trả về giá trị không null đầu tiên của mỗi nhóm',
      placeholder1: 'Trả về mảng biến cho mỗi nhóm',
      placeholder2: 'Trả về chính tả của các biến cho mỗi nhóm',
      group: {
        noneError: 'Tên không thể trống',
        dupError: 'Tên không thể trùng lặp',
      },
      addGroup: 'Thêm nhóm',
      editGroup: 'Chỉnh sửa nhóm',
    },
    mcpNode: {
      label: 'Cuộc gọi MCP',
      text: 'Gọi các dịch vụ MCP bên ngoài để xử lý dữ liệu',
      getToolsSuccess: 'Đã tìm nạp công cụ thành công',
      getTool: 'Công cụ tìm nạp',
      toolParam: 'Thông số công cụ',
      mcpServerTip: 'Vui lòng nhập cấu hình máy chủ MCP ở định dạng JSON',
      mcpToolTip: 'Vui lòng chọn một công cụ',
      configLabel: 'Cấu hình máy chủ MCP (Chỉ hỗ trợ các cuộc gọi HTTP SSE/Streamable)',
      reference: 'MCP tham khảo',
    },
    imageGenerateNode: {
      label: 'Tạo hình ảnh',
      text: 'Tạo hình ảnh dựa trên nội dung văn bản được cung cấp',
      answer: 'Nội dung AI',
      model: {
        label: 'Mô hình tạo hình ảnh',
        requiredMessage: 'Vui lòng chọn mô hình tạo hình ảnh',
      },
      prompt: {
        label: 'Lời nhắc tích cực',
        tooltip: 'Mô tả các yếu tố và đặc điểm hình ảnh bạn muốn trong hình ảnh được tạo',
      },
      negative_prompt: {
        label: 'Lời nhắc tiêu cực',
        tooltip: 'Mô tả các yếu tố bạn muốn loại trừ khỏi hình ảnh được tạo',
        placeholder:
          'Vui lòng mô tả nội dung bạn không muốn tạo, chẳng hạn như màu sắc, nội dung đẫm máu',
      },
    },
    textToVideoGenerate: {
      label: 'Text-to-Video',
      text: 'Tạo video dựa trên nội dung văn bản được cung cấp',
      answer: 'Nội dung phản hồi AI',
      model: {
        label: 'Mô hình chuyển văn bản thành video',
        requiredMessage: 'Vui lòng chọn kiểu chuyển văn bản thành video',
      },
      prompt: {
        label: 'Nhắc nhở (Tích cực)',
        tooltip:
          'Lời nhắc tích cực, dùng để mô tả các yếu tố và đặc điểm hình ảnh mong đợi trong video được tạo',
      },
      negative_prompt: {
        label: 'Lời nhắc (Tiêu cực)',
        tooltip:
          "Lời nhắc tiêu cực, dùng để mô tả nội dung bạn không muốn xem trong video, điều này có thể hạn chế việc tạo video",
        placeholder:
          "Vui lòng mô tả nội dung video mà bạn không muốn tạo, chẳng hạn như: màu sắc, nội dung đẫm máu",
      },
    },
    imageToVideoGenerate: {
      label: 'Image-to-Video',
      text: 'Tạo video dựa trên hình ảnh được cung cấp',
      answer: 'Nội dung phản hồi AI',
      model: {
        label: 'Mô hình chuyển hình ảnh thành video',
        requiredMessage: 'Vui lòng chọn mô hình chuyển hình ảnh sang video',
      },
      prompt: {
        label: 'Nhắc nhở (Tích cực)',
        tooltip:
          'Lời nhắc tích cực, dùng để mô tả các yếu tố và đặc điểm hình ảnh mong đợi trong video được tạo',
      },
      negative_prompt: {
        label: 'Lời nhắc (Tiêu cực)',
        tooltip:
          "Lời nhắc tiêu cực, dùng để mô tả nội dung bạn không muốn xem trong video, điều này có thể hạn chế việc tạo video",
        placeholder:
          "Vui lòng mô tả nội dung video mà bạn không muốn tạo, chẳng hạn như: màu sắc, nội dung đẫm máu",
      },
      first_frame: {
        label: 'Hình ảnh khung đầu tiên',
        requiredMessage: 'Vui lòng chọn hình ảnh khung đầu tiên',
      },
      last_frame: {
        label: 'Hình ảnh khung cuối cùng',
        requiredMessage: 'Hãy chọn ảnh khung cuối cùng',
      },
    },
    speechToTextNode: {
      label: 'Speech2Text',
      text: 'Chuyển đổi âm thanh thành văn bản thông qua mô hình nhận dạng giọng nói',
      stt_model: {
        label: 'Mô hình nhận dạng giọng nói',
      },
      audio: {
        label: 'Chọn tệp âm thanh',
        placeholder: 'Vui lòng chọn một tập tin âm thanh',
      },
    },
    textToSpeechNode: {
      label: 'TTS',
      text: 'Chuyển đổi văn bản thành âm thanh thông qua mô hình tổng hợp giọng nói',
      tts_model: {
        label: 'Mô hình tổng hợp giọng nói',
      },
      content: {
        label: 'Chọn nội dung văn bản',
      },
    },
    toolNode: {
      label: 'Công cụ tùy chỉnh',
      text: 'Thực thi các tập lệnh tùy chỉnh để xử lý dữ liệu',
    },
    intentNode: {
      label: 'IntentNode',
      text: 'Ghép các câu hỏi của người dùng với phân loại mục đích do người dùng xác định',
      other: 'other',
      error2: 'Ý định lặp đi lặp lại',
      placeholder: 'Vui lòng chọn một tùy chọn phân loại',
      classify: {
        label: 'Phân loại ý định',
      },
      input: {
        label: 'Input',
      },
    },
    applicationNode: {
      label: 'Nút đại lý',
    },
    loopNode: {
      label: 'Loop',
      text: 'Lặp lại một loạt tác vụ bằng cách thiết lập số vòng lặp và logic',
      loopType: {
        label: 'Loại vòng lặp',
        requiredMessage: 'Vui lòng chọn loại vòng lặp',
        arrayLoop: 'Vòng lặp mảng',
        numberLoop: 'Vòng lặp cho thời gian được chỉ định',
        infiniteLoop: 'Vòng lặp vô hạn',
      },
      loopNumber: {
        label: 'Số vòng lặp',
        requiredMessage: 'Vui lòng nhập số vòng lặp',
      },
      loopArray: {
        label: 'Mảng tròn',
        requiredMessage: 'Mảng tròn là bắt buộc',
        placeholder: 'Vui lòng chọn một mảng hình tròn',
      },
      loopSetting: 'Cài đặt vòng lặp',
      loopDetail: 'Chi tiết vòng lặp',
    },
    loopStartNode: {
      label: 'Bắt đầu vòng lặp',
      loopIndex: 'Index',
      loopItem: 'Phần tử vòng lặp',
    },
    loopBodyNode: {
      label: 'Thân vòng',
      text: 'Thân vòng',
    },
    loopContinueNode: {
      label: 'Continue',
      text: 'Được sử dụng để kết thúc vòng lặp hiện tại và chuyển sang vòng lặp tiếp theo.',
      isContinue: 'Continue',
    },
    loopBreakNode: {
      label: 'Break',
      text: 'Chấm dứt vòng lặp hiện tại và thoát khỏi thân vòng lặp',
      isBreak: 'Break',
    },
    variableSplittingNode: {
      label: 'Tách biến',
      text: 'Bằng cách định cấu hình biểu thức Đường dẫn JSON, phân tích cú pháp và phân chia biến định dạng JSON đầu vào',
      result: 'Result',
      splitVariables: 'Chia biến',
      inputVariables: 'Biến đầu vào',
      addVariables: 'Thêm biến',
      editVariables: 'Chỉnh sửa biến',
      variableListPlaceholder: 'Vui lòng thêm các biến phân chia',
      expression: {
        label: 'Expression',
        placeholder: 'Vui lòng nhập biểu thức',
        tooltip: 'Vui lòng sử dụng biểu thức Đường dẫn JSON để phân tách các biến, ví dụ: $.store.book <a href="https://pypi.org/project/jsonpath-ng/1.8.0/" target="_blank" class="biểu thức_tip">Nhấp để biết chi tiết ➜ pypi.org</a>',
      },
    },
    parameterExtractionNode: {
      label: 'Trích xuất tham số',
      text: 'Sử dụng mô hình AI để trích xuất các tham số có cấu trúc',
      extractParameters: {
        label: 'Trích xuất tham số',
        variableListPlaceholder: 'Vui lòng thêm thông số trích xuất',
        parameterType: 'Loại tham số',
      },
    },
  },
  compare: {
    is_null: 'Không có giá trị',
    is_not_null: 'Không phải là rỗng',
    contain: 'Contains',
    not_contain: 'Không chứa',
    eq: 'bằng với',
    not_eq: 'Không bằng',
    ge: 'Lớn hơn hoặc bằng',
    gt: 'Lớn hơn',
    le: 'Nhỏ hơn hoặc bằng',
    lt: 'Ít hơn',
    len_eq: 'Chiều dài bằng',
    len_ge: 'Độ dài lớn hơn hoặc bằng',
    len_gt: 'Chiều dài lớn hơn',
    len_le: 'Độ dài nhỏ hơn hoặc bằng',
    len_lt: 'Chiều dài nhỏ hơn',
    is_true: 'là đúng',
    is_not_true: 'Không đúng sự thật',
  },
  SystemPromptPlaceholder: 'Dấu nhắc hệ thống, có thể tham chiếu các biến trong hệ thống, chẳng hạn như',
  UserPromptPlaceholder: 'Lời nhắc của người dùng, có thể tham chiếu các biến trong hệ thống, chẳng hạn như',
  initiator: 'Iniiator',
  abnormalInformation: 'Thông tin bất thường',
}
