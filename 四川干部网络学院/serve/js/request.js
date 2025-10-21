const baseUrl = `/api`

export function request(method, url, data = null, headers = {}) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()

    // GET 请求拼接参数
    if (method.toUpperCase() === 'GET' && data) {
      const query = Object.entries(data)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
        .join('&')
      url += (url.includes('?') ? '&' : '?') + query
    }

    xhr.open(method.toUpperCase(), `${baseUrl}${url}`, true)

    // 设置请求头
    if (method.toUpperCase() === 'POST') {
      xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8')
    }
    for (const key in headers) {
      xhr.setRequestHeader(key, headers[key])
    }

    xhr.onreadystatechange = () => {
      if (xhr.readyState === 4) {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            resolve(JSON.parse(xhr.responseText))
          } catch (err) {
            resolve(xhr.responseText)
          }
        } else {
          reject({ status: xhr.status, statusText: xhr.statusText })
          $toast(xhr.statusText, 3000, 'top', 'error')
        }
      }
    }

    xhr.onerror = () => reject({ status: xhr.status, statusText: xhr.statusText })

    xhr.send(method.toUpperCase() === 'POST' ? JSON.stringify(data) : null)
  })
}

// 使用示例
// GET
// request('GET', 'https://jsonplaceholder.typicode.com/posts', { userId: 1 })
//   .then(res => console.log('GET:', res))
//   .catch(err => console.error('GET Error:', err))
//
// // POST
// request('POST', 'https://jsonplaceholder.typicode.com/posts', { title: 'foo', body: 'bar', userId: 1 })
//   .then(res => console.log('POST:', res))
//   .catch(err => console.error('POST Error:', err))
