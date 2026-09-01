<template>
  <div class="stats-page">
    <div class="toolbar">
      <a-space wrap>
        <a-range-picker
          v-model:value="dateRange"
          format="YYYY-MM-DD"
          :allow-clear="false"
          @change="handleRangeChange"
        />
        <a-button :type="activePreset === 0 ? 'primary' : 'default'" @click="applyPreset(0)">今日</a-button>
        <a-button :type="activePreset === 6 ? 'primary' : 'default'" @click="applyPreset(6)">近7天</a-button>
        <a-button :type="activePreset === 29 ? 'primary' : 'default'" @click="applyPreset(29)">近30天</a-button>
      </a-space>
    </div>

    <a-spin :spinning="loading">
      <a-row :gutter="[16, 16]">
        <a-col v-for="item in kpiItems" :key="item.title" :xs="24" :sm="12" :md="8" :lg="4">
          <div class="kpi-card">
            <a-statistic :title="item.title" :value="item.value" :prefix="item.prefix" />
          </div>
        </a-col>
      </a-row>

      <section class="stats-section">
        <h3 class="stats-section__title">按网站分类统计</h3>
        <p class="stats-section__hint">区间内各站接单金额，按金额从高到低</p>
        <a-empty
          v-if="!loading && !byWebsite.length"
          description="该区间暂无接单数据"
        />
        <template v-else>
          <a-row :gutter="[16, 16]" class="site-grid">
            <a-col
              v-for="site in byWebsite"
              :key="site.website_code || '__uncategorized__'"
              :xs="24"
              :sm="12"
              :md="8"
              :lg="6"
            >
              <div class="site-card">
                <div class="site-card__name">{{ websiteLabel(site) }}</div>
                <div class="site-card__revenue">{{ formatMoney(site.revenue) }}</div>
                <div class="site-card__meta">
                  区间接单 {{ site.order_count }} · 累计金额 {{ formatMoney(site.total_revenue) }}
                </div>
              </div>
            </a-col>
          </a-row>
        </template>
      </section>

      <section class="stats-section">
        <h3 class="stats-section__title">每日明细</h3>
        <p class="stats-section__hint">按创建日汇总接单数量对应的金额，无单日期按 ¥0 计</p>
        <VChart class="daily-chart" :option="dailyChartOption" :autoresize="{ throttle: 100 }" />
      </section>
    </a-spin>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import dayjs from 'dayjs'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { statsApi } from '../api'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

const defaultRange = () => [dayjs().subtract(29, 'day'), dayjs()]

const loading = ref(false)
const dateRange = ref(defaultRange())
const overview = ref({
  today: { order_count: 0, revenue: 0 },
  total: { order_count: 0, revenue: 0 },
  range: { order_count: 0, revenue: 0, charged_count: 0, free_count: 0 },
  daily: [],
  by_website: [],
})

const formatMoney = (value) => `¥${value ?? 0}`
const websiteLabel = (site) => site.website_name || site.website_code || '未分类'

const kpiItems = computed(() => [
  { title: '今日接单', value: overview.value.today.order_count },
  { title: '今日金额', value: overview.value.today.revenue, prefix: '¥' },
  { title: '区间接单', value: overview.value.range.order_count },
  { title: '区间金额', value: overview.value.range.revenue, prefix: '¥' },
  { title: '累计接单', value: overview.value.total.order_count },
  { title: '累计金额', value: overview.value.total.revenue, prefix: '¥' },
])

const byWebsite = computed(() => overview.value.by_website || [])

const dailyChartOption = computed(() => {
  const [start, end] = dateRange.value || []
  const dates = []
  const revenues = []
  if (start && end) {
    const byDate = Object.fromEntries((overview.value.daily || []).map((row) => [row.date, row]))
    let cursor = start.startOf('day')
    const last = end.startOf('day')
    while (!cursor.isAfter(last, 'day')) {
      const key = cursor.format('YYYY-MM-DD')
      dates.push(key.slice(5))
      revenues.push(byDate[key]?.revenue ?? 0)
      cursor = cursor.add(1, 'day')
    }
  }
  return {
    color: ['#1677ff'],
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const item = Array.isArray(params) ? params[0] : params
        if (!item) return ''
        return `${item.axisValue}<br/>${item.marker}接单金额：¥${item.value}`
      },
    },
    grid: {
      left: 24,
      right: 24,
      top: 36,
      bottom: 28,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
    },
    yAxis: {
      type: 'value',
      name: '金额(¥)',
      minInterval: 1,
      splitLine: { lineStyle: { type: 'dashed' } },
    },
    series: [
      {
        name: '接单金额',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        areaStyle: { opacity: 0.08 },
        data: revenues,
      },
    ],
  }
})

const activePreset = computed(() => {
  const [start, end] = dateRange.value || []
  if (!start || !end || !end.isSame(dayjs(), 'day')) return null
  const diff = end.diff(start, 'day')
  if (diff === 0 || diff === 6 || diff === 29) return diff
  return null
})

const fetchOverview = async () => {
  const [start, end] = dateRange.value || []
  if (!start || !end) return
  loading.value = true
  try {
    const res = await statsApi.overview({
      start: start.format('YYYY-MM-DD'),
      end: end.format('YYYY-MM-DD'),
    })
    overview.value = res.data
  } finally {
    loading.value = false
  }
}

const handleRangeChange = (dates) => {
  if (dates?.[0] && dates?.[1]) {
    fetchOverview()
  }
}

const applyPreset = (daysAgo) => {
  dateRange.value = [dayjs().subtract(daysAgo, 'day'), dayjs()]
  fetchOverview()
}

onMounted(fetchOverview)
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.kpi-card {
  background: #f7f8fa;
  border-radius: 8px;
  padding: 16px 18px;
}

.kpi-card :deep(.ant-statistic-content-value) {
  font-variant-numeric: tabular-nums;
}

.stats-section {
  margin-top: 28px;
}

.stats-section__title {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
}

.stats-section__hint {
  margin: 0 0 16px;
  color: rgba(0, 0, 0, 0.45);
  font-size: 13px;
}

.site-grid {
  margin-bottom: 0;
}

.site-card {
  height: 100%;
  padding: 16px 18px;
  border: 1px solid #f0f0f0;
  border-left: 3px solid #1677ff;
  border-radius: 8px;
  background: #fff;
}

.site-card__name {
  color: rgba(0, 0, 0, 0.65);
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.site-card__revenue {
  margin: 8px 0 6px;
  color: #1677ff;
  font-size: 24px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}

.site-card__meta {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
}

.daily-chart {
  width: 100%;
  height: 360px;
}
</style>
