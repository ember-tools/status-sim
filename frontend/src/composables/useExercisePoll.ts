import {type InjectionKey, onBeforeUnmount, onMounted, ref} from 'vue'
import {get} from '../api'
import type {StatusUpdate} from '../types'

/** Lets components deep in a view ask for an immediate poll after a change. */
export const REFRESH_KEY = Symbol('refresh') as InjectionKey<() => void>

/** The longest wait between two polls while the server cannot be reached. */
const MAX_INTERVAL_MS = 10_000

/**
 * Polls the state of an exercise every two seconds. Each poll is also the heartbeat by which the
 * backend shows the caller as online, so unlike `usePolling` from `@emberbox/ui` it keeps polling
 * while the tab is hidden: a vehicle that stops polling for five minutes is removed with its status.
 *
 * Never more than one request runs at a time; a `refresh` during a running request queues exactly
 * one more after it, so a change is never shown late. While the server cannot be reached, the wait
 * doubles up to ten seconds; the first answer brings it back to the interval.
 *
 * @param code the code the caller joined with
 * @param name the caller's name, which the backend registers as connection
 * @param intervalMs the delay between two polls
 * @returns the latest state, whether the last poll succeeded, and `refresh`, which polls at once
 */
export function useExercisePoll(code: string, name: () => string | undefined, intervalMs = 2000) {
    const state = ref<StatusUpdate | null>(null)
    const connected = ref(false)
    let timer: ReturnType<typeof setTimeout> | undefined
    let delay = intervalMs
    let active = false
    let running = false
    let again = false

    async function request(): Promise<void> {
        const callerName = name()
        const update = await get<StatusUpdate>(`/api/poll/${encodeURIComponent(code)}`, callerName ? {name: callerName} : {})
        if (update.type === 'status_update') state.value = update
    }

    async function poll(): Promise<void> {
        if (running) {
            again = true
            return
        }
        running = true
        clearTimeout(timer)
        try {
            await request()
            connected.value = true
            delay = intervalMs
        } catch {
            connected.value = false
            delay = Math.min(delay * 2, MAX_INTERVAL_MS)
        } finally {
            running = false
        }
        if (!active) return
        if (again) {
            again = false
            void poll()
            return
        }
        timer = setTimeout(() => void poll(), delay)
    }

    function refresh(): void {
        void poll()
    }

    onMounted(() => {
        active = true
        void poll()
    })

    onBeforeUnmount(() => {
        active = false
        again = false
        clearTimeout(timer)
    })

    return {state, connected, refresh}
}
