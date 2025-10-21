import { setup } from './js/index.js'
import { LoadingDirective } from './js/loading.js'

const { createApp } = window.Vue

const app = createApp({
  setup,
})

app.directive('loading', LoadingDirective)
app.mount('#app')
