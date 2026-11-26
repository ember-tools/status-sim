/** A request the server refused or could not answer. */
export class ApiError extends Error {
}

/**
 * Sends a request to the backend and returns its JSON answer. The backend reports refusals as
 * `{"status": "error", "message": …}` with HTTP 200; those count as failures too.
 *
 * @param method the HTTP method
 * @param path the path below the backend's root
 * @param body the JSON body, if any
 * @returns the answer
 */
async function request<T>(method: 'GET' | 'POST', path: string, body?: unknown): Promise<T> {
    const response = await fetch(path, {
        method,
        headers: body === undefined ? undefined : {'Content-Type': 'application/json'},
        body: body === undefined ? undefined : JSON.stringify(body),
    })
    if (!response.ok) throw new ApiError(`HTTP ${response.status}`)
    const data = await response.json() as T & { status?: string, message?: string }
    if (data.status === 'error') throw new ApiError(data.message ?? 'Unknown error')
    return data
}

/**
 * Reads from the backend.
 *
 * @param path the path below the backend's root
 * @param params the query parameters
 * @returns the answer
 */
export function get<T>(path: string, params: Record<string, string> = {}): Promise<T> {
    const query = new URLSearchParams(params).toString()
    return request<T>('GET', query ? `${path}?${query}` : path)
}

/**
 * Sends a change to the backend.
 *
 * @param path the path below the backend's root
 * @param body the JSON body
 * @returns the answer
 */
export function post<T = unknown>(path: string, body: unknown = {}): Promise<T> {
    return request<T>('POST', path, body)
}
