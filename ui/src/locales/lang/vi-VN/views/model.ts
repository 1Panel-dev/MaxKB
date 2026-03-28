export default {
  title: 'Model',
  provider: 'Provider',
  providerPlaceholder: 'Choose cung cấp nhà',
  addModel: 'Add model',

  delete: {
    confirmTitle: 'Xóa mô hình:',
    confirmMessage:
      'Việc xóa mô hình sẽ ảnh hưởng đến tài nguyên hiện đang sử dụng mô hình đó. Hãy tiến hành cẩn thận.',
    resourceCountMessage: 'Mô hình này được liên kết với tài nguyên {count} và sẽ không khả dụng sau khi xóa. Hãy tiến hành cẩn thận.',
  },
  tip: {
    createSuccessMessage: 'Đã tạo thành công mô hình',
    createErrorMessage: 'Có sai sót trong cơ sở thông tin',
    errorMessage: 'Biến đã tồn tại:',
    emptyMessage1: 'Vui lòng chọn loại mô hình và cơ sở mô hình trong cơ sở thông tin trước đó',
    emptyMessage2: 'Cài đặt thông số đã chọn mô hình không được hỗ trợ',
    updateSuccessMessage: 'Đã cập nhật mô hình thành công',
    saveSuccessMessage: 'Đã lưu thành công mô hình số',
    downloadError: 'Tải xuống không thành công',
    noModel: 'Mẫu người không tồn tại ở Ollama',
  },
  modelType: {
    allModel: 'Tất cả các mẫu',
    publicModel: 'Cộng mẫu của người dùng',
    privateModel: 'Riêng mẫu của người dùng',
    LLM: 'LLM',
    EMBEDDING: 'Nhúng mô hình',
    RERANKER: 'Rerank',
    STT: 'Speech2Text',
    TTS: 'TTS',
    IMAGE: 'Tầm nhìn mô hình',
    TTI: 'Tạo hình ảnh',
    TTV: 'Text-to-Video',
    ITV: 'Image-to-Video',
  },
  modelForm: {
    title: {
      baseInfo: 'Cơ sở thông tin',
      advancedInfo: 'Cài đặt nâng cao',
      modelParams: 'Model information',
      paramSetting: 'Cài đặt thông số màn hình',
      apiParamPassing: 'Giao diện thông số',
    },
    modeName: {
      label: 'Mẫu tên',
      placeholder: 'Đặt tên cho cơ sở dữ liệu',
      tooltip: 'Tùy chỉnh mô hình tên trong MaxKB',
      requiredMessage: 'Mẫu tên không thể để trống',
    },
    permissionType: {
      label: 'Permission',
      privateDesc: 'Chỉ có sẵn cho người dùng hiện tại',
      publicDesc: 'Có sẵn cho tất cả người dùng',
      requiredMessage: 'Quyền không được để trống',
    },
    model_type: {
      label: 'Model Type',
      placeholder: 'Choose model type',
      tooltip1: 'LLM: Mô hình suy luận cho các cuộc trò chuyện AI trong tác nhân.',
      tooltip2: 'Mô hình nhúng: Mô hình vector hóa nội dung tài liệu theo kiến ​​trúc.',
      tooltip3: 'Speech2Text: Một mô hình được sử dụng để nhận dạng giọng nói trong tác nhân.',
      tooltip4: 'TTS: Một mô hình được sử dụng cho TTS trong đại lý.',
      tooltip5:
        'Xếp hạng lại: Một mô hình được sử dụng để sắp xếp lại các thành viên ứng dụng phân đoạn khi sử dụng tính năng thu hồi đa tuyến trong tác nhân điều phối nâng cao.',
      tooltip6:
        'Mô hình Tầm nhìn: Một mô hình trực quan được sử dụng để hiểu hình ảnh trong tác nhân điều phối nâng cao.',
      tooltip7:
        'Tạo hình ảnh: Một mô hình trực tiếp được sử dụng để tạo hình ảnh trong tác nhân điều phối nâng cao.',
      tooltip8:
        'Chuyển văn bản thành video: Một mô hình trực quan được sử dụng để chuyển văn bản thành video trong tác nhân.',
      tooltip9:
        'Hình ảnh thành video: Một mô hình trực tiếp được sử dụng cho hình ảnh thành video trong tác nhân.',
      requiredMessage: 'Loại mô hình không thể để trống',
    },
    base_model: {
      label: 'Cơ sở cấu hình mô hình',
      tooltip: 'Đối với các model không được liệt kê, hãy nhập tên model và nhấn Enter',
      placeholder: 'Nhập cơ sở mẫu tên và nhấn Enter để thêm',
      requiredMessage: 'Cơ sở dữ liệu mô hình không thể trống',
    },
  },
  download: {
    downloading: 'Downloading...',
    cancelDownload: 'Hủy tải xuống',
  },
}
