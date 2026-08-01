import { ref } from 'vue'
import { userAccountApi } from '../api'

/**
 * 按「姓名 + 网站」在用户管理中联想账号，供任务表单选择填入。
 * @param {import('vue').Reactive} form 需包含 website_id / nick_name / username / password
 */
export function useUserAccountSuggest(form) {
  const userSuggestOptions = ref([])
  const userSuggestLoading = ref(false)
  let searchTimer = null
  let searchSeq = 0

  const clearUserSuggest = () => {
    userSuggestOptions.value = []
  }

  const buildOption = (user) => {
    const name = user.nick_name || '-'
    const account = user.username || '-'
    const organ = (user.organ_name || '').trim()
    const label = organ ? `${name}｜${account}｜${organ}` : `${name}｜${account}`
    return {
      value: `user-${user.id}`,
      label,
      user,
    }
  }

  const doSearchUserAccounts = async () => {
    const name = (form.nick_name || '').trim()
    if (!form.website_id || !name) {
      clearUserSuggest()
      return
    }

    const seq = ++searchSeq
    userSuggestLoading.value = true
    try {
      const res = await userAccountApi.list({
        page: 1,
        page_size: 20,
        keyword: name,
        website_id: form.website_id,
      })
      if (seq !== searchSeq) return

      const list = res.data?.list || []
      // 优先展示姓名命中；若无则保留接口结果（可能按账号模糊命中）
      const byName = list.filter((item) => (item.nick_name || '').includes(name))
      const matched = byName.length ? byName : list
      userSuggestOptions.value = matched.map(buildOption)
    } catch {
      if (seq === searchSeq) clearUserSuggest()
    } finally {
      if (seq === searchSeq) userSuggestLoading.value = false
    }
  }

  const searchUserAccounts = () => {
    if (searchTimer) clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
      doSearchUserAccounts()
    }, 300)
  }

  const handleSelectUserAccount = (_value, option) => {
    const user = option?.user
    if (!user) return
    form.nick_name = user.nick_name || ''
    form.username = user.username || ''
    form.password = user.password || ''
    clearUserSuggest()
  }

  const onNickNameInput = (value) => {
    // 与 v-model 同事件时，用入参同步，避免读到旧值
    if (typeof value === 'string') {
      form.nick_name = value
    } else if (value == null) {
      form.nick_name = ''
    }
    searchUserAccounts()
  }

  const onWebsiteChangeForSuggest = () => {
    clearUserSuggest()
    if ((form.nick_name || '').trim()) {
      searchUserAccounts()
    }
  }

  return {
    userSuggestOptions,
    userSuggestLoading,
    searchUserAccounts,
    handleSelectUserAccount,
    clearUserSuggest,
    onNickNameInput,
    onWebsiteChangeForSuggest,
  }
}
