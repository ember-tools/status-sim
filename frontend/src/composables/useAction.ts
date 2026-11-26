/** What the user reads when an action did not reach the server. */
const FAILURE = 'Das hat nicht geklappt. Bitte prüfe die Verbindung und versuche es erneut.'

/**
 * Runs actions against the server and says so in a toast when one fails, instead of leaving an
 * unhandled rejection and a button that seemingly does nothing.
 *
 * @returns `attempt`, which runs an action and tells whether it succeeded
 */
export function useAction() {
    const toast = useToast()

    async function attempt(action: () => Promise<unknown>): Promise<boolean> {
        try {
            await action()
            return true
        } catch {
            toast.add({title: FAILURE, color: 'error', icon: 'i-lucide-circle-alert'})
            return false
        }
    }

    return {attempt}
}
