import {type InjectionKey, onBeforeUnmount, onMounted, ref} from 'vue'
import {get} from '../api'
import type {StatusUpdate} from '../types'

/** Lets components deep in a view ask for an immediate poll after a change. */
export const REFRESH_KEY = Symbol('refresh') as InjectionKey<() => void>

/**
 * Polls the state of an exercise every two seconds. Each poll is also the heartbeat by which the
 * backend shows the caller as online, so unlike `usePolling` from `@emberbox/ui` it keeps polling
 * while the tab is hidden: a vehicle that stops polling for five minutes is removed with its status.
 * Never more than one request runs at a time.
 *
 * @param code the code the caller joined with
 * @param name the caller's name, which the backend registers as connection
 * @param intervalMs the delay between two polls
 * @returns the latest state, whether the last poll succeeded, and `refresh`, which polls at once
 */
export function useExercisePoll(code: string, name: () => string | undefined, intervalMs = 2000) {
    const state = ref<StatusUpdate | null>(null)
    const connected = ref(false)
    let timer: ReturnType<typeof setInterval> | undefined
    let running = false

    async function poll(): Promise<void> {
        if (running) return
        running = true
        try {
            const callerName = name()
            const update = await get<StatusUpdate>(`/api/poll/${encodeURIComponent(code)}`, callerName ? {name: callerName} : {})
            if (update.type === 'status_update') {
                state.value = update
                connected.value = true
            }
        } catch {
            connected.value = false
        } finally {
            running = false
        }
    }

    function refresh(): void {
        void poll()
    }

    onMounted(() => {
        void poll()
        timer = setInterval(() => void poll(), intervalMs)
    })

    onBeforeUnmount(() => clearInterval(timer))

    return {state, connected, refresh}
}
