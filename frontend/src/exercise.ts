import {get, post} from './api'

/** The three ways to take part in an exercise, one code each. */
export type Role = 'dispatch' | 'vehicle' | 'unit_leader'

/** What the backend says about a code someone wants to join with. */
export interface JoinAnswer {
    role: Role
    /** Whether a vehicle of that name is online already. */
    name_taken: boolean
}

/** Names and codes of an exercise, as the dispatch view shows them. */
export interface DispatchInfo {
    name: string
    vehicle_code: string
    staffelfuehrer_code: string
}

/**
 * Creates an exercise with its dispatch centre.
 *
 * @param name the dispatch centre's name, used in the generated radio messages
 * @returns the code of the dispatch centre
 */
export async function createExercise(name: string): Promise<string> {
    const answer = await post<{ admin_code: string }>('/api/leitstelle', {name})
    return answer.admin_code
}

/**
 * Asks which role a code stands for.
 *
 * @param code the code
 * @param name the call sign to join with
 * @returns the role and whether the call sign is free
 */
export function roleOf(code: string, name: string): Promise<JoinAnswer> {
    return get<JoinAnswer>(`/api/join/${encodeURIComponent(code)}`, {name})
}

/**
 * The address of a role's view.
 *
 * @param role the role
 * @param code the code to join with
 * @param name the call sign
 * @returns the path with its query
 */
export function joinPath(role: Role, code: string, name: string): string {
    const query = new URLSearchParams({code, name})
    switch (role) {
        case 'dispatch':
            return `/leitstelle/${encodeURIComponent(code)}`
        case 'unit_leader':
            return `/staffelfuehrer/${encodeURIComponent(code)}?${new URLSearchParams({name})}`
        case 'vehicle':
            return `/status?${query}`
    }
}

/**
 * Loads names and codes of an exercise.
 *
 * @param adminCode the dispatch centre's code
 * @returns names and codes
 */
export function dispatchInfo(adminCode: string): Promise<DispatchInfo> {
    return get<DispatchInfo>(`/api/leitstelle_info/${encodeURIComponent(adminCode)}`)
}

/**
 * Loads the dispatch centre's name for the unit leader's code.
 *
 * @param code the unit leader code
 * @returns the dispatch centre's name
 */
export async function unitLeaderInfo(code: string): Promise<string> {
    const answer = await get<{ name: string }>(`/api/staffelfuehrer_info/${encodeURIComponent(code)}`)
    return answer.name
}

/**
 * Loads the dispatch centre's name for a vehicle.
 *
 * @param code the vehicle code
 * @param name the vehicle's call sign
 * @returns the dispatch centre's name
 */
export async function vehicleInfo(code: string, name: string): Promise<string> {
    const answer = await get<{ leitstelle_name: string }>('/api/status_info', {code, name})
    return answer.leitstelle_name
}

/**
 * The base path of the actions on vehicles and messages. The backend serves them for the dispatch
 * code and, partly, for the unit leader code.
 *
 * @param code the dispatch or unit leader code
 * @returns the path
 */
export function exercisePath(code: string): string {
    return `/api/leitstelle/${encodeURIComponent(code)}`
}

/**
 * The base path of the unit leader's own actions.
 *
 * @param code the unit leader code
 * @returns the path
 */
export function unitLeaderPath(code: string): string {
    return `/api/staffelfuehrer/${encodeURIComponent(code)}`
}

/**
 * Sends an action of a vehicle: a status, a short status message, a confirmation or a channel.
 *
 * @param code the vehicle code
 * @param name the vehicle's call sign
 * @param action the action
 * @param value its value, if any
 */
export async function vehicleAction(code: string, name: string, action: string, value?: string): Promise<void> {
    await post(`/api/vehicle/${encodeURIComponent(code)}/action`, {name, action, value})
}
