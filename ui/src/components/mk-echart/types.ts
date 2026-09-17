import type { LineSeriesOption } from 'echarts/charts'

/** 折线系列，默认开启面积填充，area: false 可关闭。 */
export type MkLineChartSeries = Omit<LineSeriesOption, 'type'> & { area?: boolean }

/** 折线图的横轴和系列配置。 */
export interface MkLineChartOption {
  xData: string[]
  yData: MkLineChartSeries[]
}
