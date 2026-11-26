import type {VehicleStatus} from './types'

/**
 * A vehicle as the help shows it in its replicas of the interface. Timestamps are 0, so a
 * prerendered page shows the same as the browser.
 *
 * @param change what differs from a vehicle at the station
 * @returns the vehicle
 */
export function exampleVehicle(change: Partial<VehicleStatus>): VehicleStatus {
    return {
        name: 'LHF 2300/1',
        status: '2',
        special: null,
        kurzstatus: null,
        last_update: 0,
        last_status_update: 0,
        last_blitz_update: null,
        last_sprechwunsch_update: null,
        is_staffelfuehrer: false,
        note: '',
        sf_note: '',
        is_online: true,
        talking_to_sf: false,
        talking_to_sf_since: null,
        radio_channel: null,
        claimed_by: null,
        ls_claimed_by: null,
        ls_radio_channel: null,
        sf_radio_channel: null,
        active_scenario: null,
        next_todo: null,
        last_activity: 0,
        checklist_state: null,
        ...change,
    }
}
