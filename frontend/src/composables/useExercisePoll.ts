import {usePolling} from '@emberbox/ui'
import {type InjectionKey, ref} from 'vue'
import {get} from '../api'
import type {StatusUpdate} from '../types'

/** Lets components deep in a view ask for an immediate poll after a change. */
export const REFRESH_KEY = Symbol('refresh') as InjectionKey<() => void>

/** The longest wait between two polls while the server cannot be reached. */
const MAX_INTERVAL_MS = 10_000

/**
 * The wait between two polls while the tab is hidden. Each poll is the heartbeat by which the
 * backend shows the caller as online for fifteen seconds and removes a caller silent for five
 * minutes, so a hidden tab keeps polling, below the fifteen seconds; browsers stretch this to about
 * a minute in tabs hidden for long.
 */
const HIDDEN_INTERVAL_MS = 10_000

/**
 * Polls the state of an exercise every two seconds, and every ten while the tab is hidden. While
 * the server cannot be reached, the wait doubles up to ten seconds; the first answer brings it back
 * to the interval. One poll runs at a time; a `refresh` during a running poll queues one more.
 *
 * @param code the code the caller joined with
 * @param name the caller's name, which the backend registers as connection
 * @param intervalMs the delay between two polls
 * @returns the latest state, whether the last poll succeeded, and `refresh`, which polls at once
 */
export function useExercisePoll(code: string, name: () => string | undefined, intervalMs = 2000) {
    const state = ref<StatusUpdate | null>(null)
    const {connected, refresh} = usePolling(async () => {
        const callerName = name()
        const update = await get<StatusUpdate>(`/api/poll/${encodeURIComponent(code)}`, callerName ? {name: callerName} : {})
        if (update.type === 'status_update') state.value = update
    }, {intervalMs, maxIntervalMs: MAX_INTERVAL_MS, hiddenIntervalMs: HIDDEN_INTERVAL_MS})
    return {state, connected, refresh}
}
