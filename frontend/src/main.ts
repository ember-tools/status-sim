import {cleanUpStorage, createToolApp, emberboxUi} from '@emberbox/ui'
import App from './App.vue'
import {browserNavigation} from './navigation'
import './style.css'

cleanUpStorage({remove: ['ls_name_*', 'ls_channel_*', 'ls_combine_*', 'sf_name_*', 'radio_channel_*', 'theme']})
createToolApp(App).use(browserNavigation()).use(emberboxUi).mount('#app')
