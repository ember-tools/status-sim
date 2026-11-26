import {renderPage} from '@emberbox/ui/prerender'
import {createSSRApp} from 'vue'
import App from './App.vue'
import {staticNavigation} from './navigation'

/**
 * Prerenders one public page of the application. Without vue-router, the page is chosen by a
 * navigation fixed to the path.
 *
 * @param path the page's path
 * @param template the built `index.html`
 * @returns the page's HTML
 */
export async function render(path: string, template: string): Promise<string> {
    const app = createSSRApp(App).use(staticNavigation(path))
    return renderPage(app, template)
}
