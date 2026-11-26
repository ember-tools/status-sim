import {type App, inject, type InjectionKey, type Ref, ref} from 'vue'

/** The part of the address the app routes by. */
export interface Location {
    path: string
    query: URLSearchParams
}

/**
 * The app's own routing, deliberately without vue-router: the current address and a way to move to
 * another one with `pushState`.
 */
export interface Navigation {
    location: Ref<Location>
    navigate: (url: string) => void
}

/** What the address shows: one of the public pages or one of the three exercise roles. */
export type Page =
    | { view: 'landing' }
    | { view: 'help' }
    | { view: 'dispatch', code: string }
    | { view: 'unitLeader', code: string }
    | { view: 'vehicle', code: string, name: string }

const NAVIGATION: InjectionKey<Navigation> = Symbol('navigation')

/**
 * Splits an address into path and query. Relative addresses are read against a placeholder origin,
 * since only path and query matter.
 *
 * @param url the address, absolute or relative
 * @returns its path and query
 */
export function parseLocation(url: string): Location {
    const parsed = new URL(url, 'http://localhost')
    return {path: parsed.pathname, query: parsed.searchParams}
}

/**
 * Decides which page an address shows. `/leitstelle/<code>` and `/staffelfuehrer/<code>` open the
 * dispatch and unit leader views, `/status?code=…&name=…` the vehicle; anything unknown shows the
 * landing page. Trailing slashes do not count, so `/hilfe/` is the help as the backend serves it.
 *
 * @param location the address
 * @returns the page
 */
export function resolvePage(location: Location): Page {
    const path = location.path.replace(/\/+$/, '') || '/'
    const [, section, code, rest] = path.split('/')
    if (path === '/hilfe') return {view: 'help'}
    if (section === 'leitstelle' && code && rest === undefined) return {view: 'dispatch', code}
    if (section === 'staffelfuehrer' && code && rest === undefined) return {view: 'unitLeader', code}
    const vehicleCode = location.query.get('code')
    const name = location.query.get('name')
    if (path === '/status' && vehicleCode && name) return {view: 'vehicle', code: vehicleCode, name}
    return {view: 'landing'}
}

/**
 * Navigation in the browser: starts at the address bar, follows `pushState` and the back and
 * forward buttons.
 */
export function browserNavigation() {
    return {
        install(app: App) {
            const location = ref(parseLocation(window.location.href))
            window.addEventListener('popstate', () => {
                location.value = parseLocation(window.location.href)
            })
            app.provide(NAVIGATION, {
                location,
                navigate(url: string) {
                    window.history.pushState({}, '', url)
                    location.value = parseLocation(url)
                },
            })
        },
    }
}

/**
 * Navigation fixed to one address, for prerendering a public page at build time.
 *
 * @param path the page's path
 */
export function staticNavigation(path: string) {
    return {
        install(app: App) {
            app.provide(NAVIGATION, {
                location: ref(parseLocation(path)),
                navigate() {
                    throw new Error('A prerendered page cannot navigate.')
                },
            })
        },
    }
}

/** The navigation the app was installed with. */
export function useNavigation(): Navigation {
    const navigation = inject(NAVIGATION)
    if (!navigation) throw new Error('No navigation installed.')
    return navigation
}
