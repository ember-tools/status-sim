import type {HelpTopicInfo} from '@emberbox/ui/vite'

/** The topics of the help center, in reading order; `vite.config.ts` prerenders a page for each. */
export const HELP_TOPICS = [
    {
        slug: 'uebung-anlegen',
        title: 'Übung anlegen und beitreten',
        description: 'Wie die Leitstelle eine Funkübung anlegt, die Codes für Fahrzeuge und Staffelführer verteilt und wie alle beitreten.',
    },
    {
        slug: 'fahrzeug',
        title: 'Als Fahrzeug',
        description: 'Status setzen, Sprechwunsch melden, Kurzlagemeldungen senden und mit dem Staffelführer sprechen.',
    },
    {
        slug: 'status',
        title: 'Die Status im Überblick',
        description: 'Was die Status 1 bis 8, der Sprechwunsch (5) und der dringende Sprechwunsch (0) bedeuten und welcher Wechsel erlaubt ist.',
    },
    {
        slug: 'leitstelle',
        title: 'In der Leitstelle',
        description: 'Mit mehreren Disponenten arbeiten, Fahrzeuge übernehmen, Sprechwünsche abarbeiten und Einsätze erstellen.',
    },
    {
        slug: 'staffelfuehrer',
        title: 'Als Staffelführer',
        description: 'Fahrzeuge übernehmen, auf den eigenen Funkkanal holen und die Checkliste des Szenarios mitführen.',
    },
    {
        slug: 'szenarien',
        title: 'Szenarien und Checklisten',
        description: 'Wie Status Sim aus einem Szenario die Funksprüche eines Einsatzes erzeugt und wer welchen Spruch abhakt.',
    },
    {
        slug: 'verbindung-und-speicher',
        title: 'Verbindung, Speicher und Löschfristen',
        description: 'Wann ein Fahrzeug als getrennt gilt, was der Browser speichert und wann eine Übung gelöscht wird.',
    },
] as const satisfies readonly HelpTopicInfo[]

/** The slug of a help topic. */
export type HelpSlug = (typeof HELP_TOPICS)[number]['slug']
