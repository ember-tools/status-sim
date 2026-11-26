/** The theme colours a vehicle status can take. */
export type StatusColor = 'info' | 'success' | 'warning' | 'error' | 'neutral'

/**
 * The colour of a vehicle status: blue on air (1), green at the station (2), amber en route (3), red
 * on scene or out of service (4, 6), grey otherwise.
 *
 * @param status the status digit
 * @returns its colour
 */
export function statusColor(status: string): StatusColor {
    switch (status) {
        case '1':
            return 'info'
        case '2':
            return 'success'
        case '3':
            return 'warning'
        case '4':
        case '6':
            return 'error'
        default:
            return 'neutral'
    }
}

/** The left border of a vehicle card in the colour of its status, as literal classes for Tailwind. */
const STATUS_BORDER: Record<StatusColor, string> = {
    info: 'border-l-info',
    success: 'border-l-success',
    warning: 'border-l-warning',
    error: 'border-l-error',
    neutral: 'border-l-accented',
}

/**
 * The left border class of a vehicle card.
 *
 * @param status the vehicle's status digit
 * @returns the class
 */
export function statusBorder(status: string): string {
    return STATUS_BORDER[statusColor(status)]
}

/**
 * When a vehicle raised its current special status: the flash (0) or the request to talk (5).
 *
 * @param vehicle the vehicle's special status and its two timestamps
 * @returns the timestamp in seconds, or 0 without a special status
 */
export function specialSince(vehicle: { special: string | null, last_blitz_update: number | null, last_sprechwunsch_update: number | null }): number {
    return (vehicle.special === '0' ? vehicle.last_blitz_update : vehicle.last_sprechwunsch_update) ?? 0
}
