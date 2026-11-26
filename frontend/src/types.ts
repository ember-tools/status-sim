/** Which entries of a scenario checklist are ticked and which parts are expanded. */
export interface ChecklistState {
  expanded_einsaetze: Record<string, boolean>
  expanded_schritte: Record<string, boolean>
  checked_entries: Record<string, boolean>
}

/** One radio message of a scenario and who says it: dispatch, unit leader or vehicle. */
export interface RadioEntry {
  actor: 'LS' | 'SF' | 'FZ'
  message: string | null
  status: string | null
}

/** A step of an incident, identified by its type. */
export interface ScenarioStep {
  typ: string
}

/** One incident of a scenario. */
export interface ScenarioIncident {
  stichwort: string
  adresse: string
  ortsteil: string
  schritte: ScenarioStep[]
}

/** A scenario running for a vehicle, with the radio messages generated for it. */
export interface ActiveScenario {
  name: string
  beschreibung: string
  einsaetze: ScenarioIncident[]
  generated_entries: RadioEntry[]
}

/** A vehicle as the dispatch and unit leader views see it. */
export interface VehicleStatus {
  name: string
  status: string
  special: string | null
  kurzstatus: string | null
  last_update: number
  last_status_update: number
  last_blitz_update: number | null
  last_sprechwunsch_update: number | null
  is_staffelfuehrer: boolean
  note: string
  sf_note: string
  is_online: boolean
  talking_to_sf: boolean
  talking_to_sf_since: number | null
  radio_channel: string | null
  claimed_by: string | null
  ls_claimed_by: string | null
  ls_radio_channel: string | null
  sf_radio_channel: string | null
  active_scenario: ActiveScenario | null
  next_todo: string | null
  last_activity: number
  checklist_state: ChecklistState | null
}

/** A request of the unit leader to a vehicle to switch channels, and whether it was confirmed. */
export interface Notice {
  text: string
  status: string
  confirmed_at?: number
}

/** A message between dispatch or unit leader and a vehicle. */
export interface ChatMessage {
  sender: string
  text: string
  timestamp: number
}

/** The answer of every poll. */
export interface StatusUpdate {
  type: string
  connections: VehicleStatus[]
  notices: Record<string, Notice>
  messages?: ChatMessage[]
}
