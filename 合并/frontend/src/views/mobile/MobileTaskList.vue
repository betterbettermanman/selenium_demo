<template>
  <div class="mobile-tasks">
    <div class="mobile-tasks__toolbar">
      <a-input-search
        v-model:value="keyword"
        placeholder="搜索姓名/账号/网站/课程"
        allow-clear
        enter-button="搜索"
        size="large"
        @search="handleMobileSearch"
      />
      <div class="status-tabs">
        <button
          v-for="item in statusTabs"
          :key="item.value"
          type="button"
          class="status-tab"
          :class="{ 'status-tab--active': statusFilter === item.value }"
          @click="setStatusFilter(item.value)"
        >
          {{ item.label }}
        </button>
      </div>
    </div>

    <a-spin :spinning="loading && pagination.current === 1">
      <div v-if="dataList.length" class="task-cards">
        <article
          v-for="record in dataList"
          :key="record.id"
          class="task-card"
          :class="{ 'task-card--expanded': expandedId === record.id }"
        >
          <div class="task-card__head" @click="toggleExpand(record.id)">
            <div class="task-card__main">
              <div class="task-card__title">{{ record.website_name || '-' }}</div>
              <div class="task-card__subtitle">{{ record.course_name || '-' }}</div>
            </div>
            <div class="task-card__tags">
              <span
                class="tag"
                :class="record.status === '2' ? 'tag--success' : 'tag--warning'"
              >
                {{ record.status === '2' ? '完成' : '未完成' }}
              </span>
              <span v-if="record.waiting_sms" class="tag tag--sms">待验证码</span>
              <span v-else-if="record.is_running" class="tag tag--running">
                <LoadingOutlined spin />
                执行中
              </span>
            </div>
          </div>

          <div class="task-card__body">
            <div class="info-row">
              <span class="info-label">姓名</span>
              <span class="info-value">{{ record.nick_name || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">账号</span>
              <span class="info-value">{{ record.username || '-' }}</span>
            </div>
            <template v-if="expandedId === record.id">
              <div class="info-row">
                <span class="info-label">单位</span>
                <span class="info-value">{{ record.organ_name || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">密码</span>
                <span class="info-value">{{ record.password || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">收费</span>
                <span class="info-value">
                  {{ record.is_charged === '1' ? '是' : '否' }}
                  <template v-if="record.is_charged === '1' && record.price != null">
                    · ¥{{ record.price }}
                  </template>
                </span>
              </div>
              <div class="info-row">
                <span class="info-label">模式</span>
                <span class="info-value">{{ record.is_head === '1' ? '无头' : '有头' }}</span>
              </div>
              <div v-if="record.remark" class="info-row">
                <span class="info-label">备注</span>
                <span class="info-value">{{ record.remark }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">创建</span>
                <span class="info-value">{{ record.create_time || '-' }}</span>
              </div>
            </template>
            <div class="expand-hint" @click="toggleExpand(record.id)">
              {{ expandedId === record.id ? '收起详情' : '展开详情' }}
            </div>
          </div>

          <div class="task-card__actions">
            <a-button
              type="primary"
              size="small"
              block
              :loading="startingTaskId === record.id"
              :disabled="record.is_running && !record.waiting_sms"
              @click="handleStart(record)"
            >
              {{ record.waiting_sms ? '输入验证码' : '启动' }}
            </a-button>
            <a-button
              size="small"
              block
              :loading="stoppingTaskId === record.id"
              :disabled="!record.is_running"
              @click="confirmStop(record.id)"
            >
              关闭
            </a-button>
            <a-button size="small" block @click="openFormDrawer(record)">编辑</a-button>
            <a-button size="small" block danger @click="confirmDelete(record.id)">删除</a-button>
          </div>
        </article>
      </div>

      <a-empty v-else-if="!loading" description="暂无任务" class="empty-block" />
    </a-spin>

    <div v-if="dataList.length" class="load-more">
      <a-button
        v-if="hasMore()"
        block
        size="large"
        :loading="loading"
        @click="loadMore"
      >
        加载更多（{{ dataList.length }}/{{ pagination.total }}）
      </a-button>
      <div v-else class="load-more__done">已加载全部 {{ pagination.total }} 条</div>
    </div>

    <a-float-button
      type="primary"
      :style="{ right: '20px', bottom: 'calc(24px + env(safe-area-inset-bottom, 0))' }"
      @click="openFormDrawer()"
    >
      <template #icon>
        <PlusOutlined />
      </template>
    </a-float-button>

    <a-drawer
      v-model:open="formDrawerVisible"
      :title="editingId ? '编辑任务' : '新增任务'"
      placement="bottom"
      height="88%"
      :destroy-on-close="true"
      class="mobile-form-drawer"
    >
      <a-form :model="form" layout="vertical" class="mobile-form">
        <a-form-item label="网站" required>
          <a-select
            v-model:value="form.website_id"
            placeholder="请选择网站"
            show-search
            option-filter-prop="label"
            size="large"
            @change="handleWebsiteChange"
          >
            <a-select-option
              v-for="item in websiteOptions"
              :key="item.id"
              :value="item.id"
              :label="item.name"
            >
              {{ item.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="课程" required>
          <a-select
            v-model:value="form.course_id"
            placeholder="请选择课程"
            show-search
            option-filter-prop="label"
            size="large"
            :disabled="!form.website_id"
            :loading="courseLoading"
          >
            <a-select-option
              v-for="item in courseOptions"
              :key="item.id"
              :value="item.id"
              :label="item.name"
            >
              {{ item.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="姓名">
          <a-input v-model:value="form.nick_name" placeholder="可选" size="large" />
        </a-form-item>
        <a-form-item label="账号" required>
          <a-input v-model:value="form.username" placeholder="请输入账号" size="large" />
        </a-form-item>
        <a-form-item label="密码" required>
          <a-input-password v-model:value="form.password" placeholder="请输入密码" size="large" />
        </a-form-item>
        <a-form-item label="是否收费">
          <a-select v-model:value="form.is_charged" size="large">
            <a-select-option value="0">否</a-select-option>
            <a-select-option value="1">是</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="价格">
          <a-input-number
            v-model:value="form.price"
            :min="0"
            :precision="0"
            :step="1"
            style="width: 100%"
            placeholder="可选"
            size="large"
          />
        </a-form-item>
        <a-form-item label="浏览器模式">
          <a-select v-model:value="form.is_head" size="large">
            <a-select-option value="1">无头模式</a-select-option>
            <a-select-option value="0">有头模式</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="备注">
          <a-input v-model:value="form.remark" placeholder="可选" size="large" />
        </a-form-item>
      </a-form>
      <template #footer>
        <a-button block size="large" type="primary" :loading="submitting" @click="submitForm">
          保存
        </a-button>
      </template>
    </a-drawer>

    <a-modal
      v-model:open="smsModalVisible"
      title="手机验证码"
      :confirm-loading="smsSubmitting"
      ok-text="确认"
      cancel-text="取消"
      centered
      @ok="handleSubmitSms"
      @cancel="smsCode = ''"
    >
      <a-alert
        message="请输入手机短信验证码后继续执行任务"
        type="info"
        show-icon
        style="margin-bottom: 16px"
      />
      <a-form layout="vertical">
        <a-form-item label="验证码" required>
          <a-input
            v-model:value="smsCode"
            placeholder="请输入验证码"
            maxlength="8"
            size="large"
            inputmode="numeric"
            @press-enter="handleSubmitSms"
          />
        </a-form-item>
        <a-button type="link" :loading="smsResending" @click="handleResendSms">
          重发验证码
        </a-button>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { LoadingOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { Modal } from 'ant-design-vue'
import { useTaskManager } from '../../composables/useTaskManager'

const statusTabs = [
  { label: '全部', value: undefined },
  { label: '未完成', value: '1' },
  { label: '完成', value: '2' },
]

const {
  loading,
  submitting,
  courseLoading,
  dataList,
  keyword,
  statusFilter,
  editingId,
  websiteOptions,
  courseOptions,
  startingTaskId,
  stoppingTaskId,
  smsModalVisible,
  smsSubmitting,
  smsResending,
  smsCode,
  form,
  pagination,
  handleWebsiteChange,
  handleSearch,
  openModal,
  handleSubmit,
  handleStop,
  handleDelete,
  handleStart,
  handleSubmitSms,
  handleResendSms,
  loadMore,
  hasMore,
} = useTaskManager()

const expandedId = ref(null)
const formDrawerVisible = ref(false)

const toggleExpand = (id) => {
  expandedId.value = expandedId.value === id ? null : id
}

const setStatusFilter = (value) => {
  statusFilter.value = value
  handleSearch()
}

const handleMobileSearch = () => {
  handleSearch()
}

const openFormDrawer = async (record = null) => {
  await openModal(record)
  formDrawerVisible.value = true
}

const submitForm = async () => {
  const ok = await handleSubmit()
  if (ok) {
    formDrawerVisible.value = false
  }
}

const confirmStop = (id) => {
  Modal.confirm({
    title: '关闭任务',
    content: '确定关闭该任务吗？将关闭对应浏览器并停止执行。',
    okText: '关闭',
    cancelText: '取消',
    centered: true,
    onOk: () => handleStop(id),
  })
}

const confirmDelete = (id) => {
  Modal.confirm({
    title: '删除任务',
    content: '确定删除该任务吗？此操作不可恢复。',
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    centered: true,
    onOk: () => handleDelete(id),
  })
}
</script>

<style scoped>
.mobile-tasks {
  padding: 12px 12px calc(80px + env(safe-area-inset-bottom, 0));
}

.mobile-tasks__toolbar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: #f5f6f8;
  padding-bottom: 8px;
}

.status-tabs {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.status-tab {
  flex: 1;
  height: 36px;
  border: none;
  border-radius: 18px;
  background: #fff;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.status-tab--active {
  background: #1677ff;
  color: #fff;
  font-weight: 500;
}

.task-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.task-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.task-card__head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 14px 10px;
  cursor: pointer;
}

.task-card__title {
  font-size: 16px;
  font-weight: 600;
  color: #1f1f1f;
  line-height: 1.4;
}

.task-card__subtitle {
  margin-top: 4px;
  font-size: 13px;
  color: #888;
  line-height: 1.4;
}

.task-card__tags {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  flex-shrink: 0;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
}

.tag--success {
  color: #389e0d;
  background: #f6ffed;
}

.tag--warning {
  color: #d48806;
  background: #fffbe6;
}

.tag--sms {
  color: #d46b08;
  background: #fff7e6;
}

.tag--running {
  color: #1677ff;
  background: #e6f4ff;
}

.task-card__body {
  padding: 0 14px 10px;
  border-top: 1px solid #f0f0f0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 0;
  font-size: 14px;
  line-height: 1.5;
}

.info-label {
  color: #999;
  flex-shrink: 0;
}

.info-value {
  color: #333;
  text-align: right;
  word-break: break-all;
}

.expand-hint {
  text-align: center;
  padding: 6px 0 2px;
  font-size: 13px;
  color: #1677ff;
  cursor: pointer;
}

.task-card__actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 10px 14px 14px;
  background: #fafafa;
  border-top: 1px solid #f0f0f0;
}

.empty-block {
  margin-top: 80px;
}

.load-more {
  margin-top: 16px;
}

.load-more__done {
  text-align: center;
  color: #999;
  font-size: 13px;
  padding: 8px 0;
}

.mobile-form {
  padding-bottom: 16px;
}
</style>

<style>
.mobile-form-drawer .ant-drawer-body {
  padding-bottom: 8px;
}

.mobile-form-drawer .ant-drawer-footer {
  padding: 12px 16px calc(12px + env(safe-area-inset-bottom, 0));
}
</style>
