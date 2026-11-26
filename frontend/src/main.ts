import {createToolApp, emberboxUi} from '@emberbox/ui'
import App from './App.vue'
import {browserNavigation} from './navigation'
import './style.css'

createToolApp(App).use(browserNavigation()).use(emberboxUi).mount('#app')
