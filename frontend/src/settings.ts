/** What a dispatcher or unit leader keeps per exercise in the browser. */
export interface ExerciseSettings {
    name?: string
    channel?: string
    /** Dispatch only: whether flashes and requests to talk are listed as one group. */
    combine?: boolean
    /** When the entry was last written, in milliseconds since the epoch. */
    savedAt?: number
}

/** Whose settings: the dispatch centre's or the unit leader's. */
export type SettingsRole = 'dispatch' | 'unitLeader'

const DISPATCH_KEY = 'statussim.dispatch'
const UNIT_LEADER_KEY = 'statussim.unit-leader'

/** Exercises are deleted seven days after their last use, so their settings are dropped after that too. */
const KEEP_MS = 7 * 24 * 60 * 60 * 1000

function readRaw(role: SettingsRole): string | null {
    return role === 'dispatch' ? localStorage.getItem(DISPATCH_KEY) : localStorage.getItem(UNIT_LEADER_KEY)
}

function writeRaw(role: SettingsRole, value: string): void {
    if (role === 'dispatch') localStorage.setItem(DISPATCH_KEY, value)
    else localStorage.setItem(UNIT_LEADER_KEY, value)
}

/**
 * All exercises' settings of a role. A browser that refuses storage, or an entry that is not valid
 * JSON, yields none.
 */
function readAll(role: SettingsRole): Record<string, ExerciseSettings> {
    try {
        const parsed: unknown = JSON.parse(readRaw(role) ?? '{}')
        return typeof parsed === 'object' && parsed !== null ? parsed as Record<string, ExerciseSettings> : {}
    } catch {
        return {}
    }
}

/** Keys earlier versions kept per exercise, as prefixes followed by the code. */
const RETIRED_PREFIXES = ['ls_name_', 'ls_channel_', 'ls_combine_', 'sf_name_', 'radio_channel_']

/** Keys earlier versions kept once per browser; `theme` was the old colour mode. */
const RETIRED_KEYS = ['theme']

let retiredRemoved = false

/**
 * Removes what earlier versions left in the browser, once per page load. Those keys carry the
 * exercise code in their name, so they are found by scanning the storage for the retired prefixes
 * and removed through a `Storage` reference: the browser storage catalogue lists only the keys
 * Status Sim keeps and accepts literal keys only, which a scan over retired keys cannot give.
 */
function removeRetiredKeys(): void {
    if (retiredRemoved) return
    retiredRemoved = true
    try {
        const storage: Storage = localStorage
        const retired = Array.from({length: storage.length}, (_, index) => storage.key(index))
            .filter((key): key is string => key !== null)
            .filter(key => RETIRED_KEYS.includes(key) || RETIRED_PREFIXES.some(prefix => key.startsWith(prefix)))
        retired.forEach(key => storage.removeItem(key))
    } catch {
        return
    }
}

/**
 * The settings saved for an exercise. Loading counts as use, so an exercise opened every day keeps
 * its settings; old keys of earlier versions are cleared on the first load.
 *
 * @param role whose settings
 * @param code the exercise's code of that role
 * @returns the settings, empty when nothing was saved
 */
export function loadSettings(role: SettingsRole, code: string): ExerciseSettings {
    removeRetiredKeys()
    const settings = readAll(role)[code]
    if (!settings) return {}
    saveSettings(role, code, {})
    return settings
}

/**
 * Saves settings for an exercise, keeping what is not changed. Entries not written for longer than
 * an exercise lives are dropped on the way.
 *
 * @param role whose settings
 * @param code the exercise's code of that role
 * @param change the settings to change
 */
export function saveSettings(role: SettingsRole, code: string, change: ExerciseSettings): void {
    const now = Date.now()
    const all = Object.fromEntries(Object.entries(readAll(role)).filter(([, entry]) => now - (entry.savedAt ?? 0) < KEEP_MS))
    all[code] = {...all[code], ...change, savedAt: now}
    try {
        writeRaw(role, JSON.stringify(all))
    } catch {
        return
    }
}

/**
 * Puts name and channel into the address, so a reload or a shared link keeps them.
 *
 * @param name the dispatcher's or unit leader's name
 * @param channel the radio channel, left out when empty
 */
export function writeSettingsToAddress(name: string, channel: string): void {
    const url = new URL(window.location.href)
    url.searchParams.set('name', name)
    if (channel) url.searchParams.set('channel', channel)
    else url.searchParams.delete('channel')
    window.history.replaceState({}, '', url.toString())
}

/**
 * The address that opens the landing page with a code filled in.
 *
 * @param code the code to join with
 * @returns the absolute address
 */
export function joinLink(code: string): string {
    return `${window.location.origin}/?${new URLSearchParams({code})}`
}
