import html2Canvas from 'html2canvas'
import jsPDF from 'jspdf'

export const exportToPDF = async (elementId: string, filename = 'document.pdf') => {
  const element = document.getElementById(elementId)
  if (!element) return
  await html2Canvas(element, {
    useCORS: true,
    allowTaint: true,
    logging: false,
    scale: 2,
    backgroundColor: '#fff',
  }).then((canvas: any) => {
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageWidth = 190 // 保留边距后的有效宽度
    const pageHeight = 277 // 保留边距后的有效高度 //A4大小，210mm x 297mm，四边各保留10mm的边距，显示区域190x277
    const imgHeight = (pageHeight * canvas.width) / pageWidth

    let renderedHeight = 0
    while (renderedHeight < canvas.height) {
      const pageCanvas = document.createElement('canvas')
      pageCanvas.width = canvas.width
      pageCanvas.height = Math.min(imgHeight, canvas.height - renderedHeight)

      pageCanvas
        .getContext('2d')!
        .putImageData(
          canvas
            .getContext('2d')!
            .getImageData(
              0,
              renderedHeight,
              canvas.width,
              Math.min(imgHeight, canvas.height - renderedHeight),
            ),
          0,
          0,
        )

      pdf.addImage(
        pageCanvas.toDataURL('image/jpeg', 1.0),
        'JPEG',
        10,
        10, // 左边距和上边距
        pageWidth,
        Math.min(pageHeight, (pageWidth * pageCanvas.height) / pageCanvas.width),
      )

      renderedHeight += imgHeight
      if (renderedHeight < canvas.height) {
        pdf.addPage()
      }
    }
    pdf.save(filename)
  })
}
