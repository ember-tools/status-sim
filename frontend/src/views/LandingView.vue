<script setup lang="ts">
import {TextField, usePage, webApplicationData} from '@emberbox/ui'
import {onMounted, ref} from 'vue'
import {createExercise, joinPath, roleOf} from '../exercise'
import {useNavigation} from '../navigation'

const DESCRIPTION = 'Funkverkehr und Fahrzeugstatus üben: Leitstelle, Staffelführer und Fahrzeuge spielen eine Übung gemeinsam, jede Rolle am eigenen Gerät.'

usePage({
  title: 'Status Sim – Funk und Fahrzeugstatus üben',
  description: DESCRIPTION,
  path: '/',
  structuredData: [webApplicationData({name: 'Status Sim', description: DESCRIPTION})],
})

/** What the landing page names as the parts of an exercise. */
const FEATURES = [
  {
    icon: 'i-lucide-radio',
    title: 'Status wie im Fahrzeug',
    text: 'Ein Statusfeld mit Status 1 bis 8, Sprechwunsch, Blitz und Kurzlagemeldungen.',
  },
  {
    icon: 'i-lucide-headset',
    title: 'Leitstelle mit mehreren Plätzen',
    text: 'Disponenten teilen sich die Fahrzeuge, Sprechwünsche stehen nach Wartezeit sortiert oben.',
  },
  {
    icon: 'i-lucide-list-checks',
    title: 'Szenarien zum Abhaken',
    text: 'Vorbereitete Einsätze erzeugen die Funksprüche für Leitstelle, Staffelführer und Fahrzeug.',
  },
] as const

const {navigate} = useNavigation()
const dispatchName = ref('Florian Berlin')
const code = ref('')
const callSign = ref('')
const error = ref('')

/**
 * A call sign of the kind `LHF 2300/1`, so a trainee can join without thinking one up.
 *
 * @returns the call sign
 */
function randomCallSign(): string {
  let number: number
  do {
    number = Math.floor(Math.random() * 56) + 10
  } while (number % 10 === 0)
  return `LHF ${number}00/1`
}

onMounted(() => {
  callSign.value = randomCallSign()
  code.value = new URLSearchParams(window.location.search).get('code') ?? ''
})

async function create(): Promise<void> {
  error.value = ''
  if (!dispatchName.value.trim()) return
  try {
    const adminCode = await createExercise(dispatchName.value.trim())
    navigate(`/leitstelle/${adminCode}`)
  } catch {
    error.value = 'Die Leitstelle konnte nicht angelegt werden.'
  }
}

async function join(): Promise<void> {
  error.value = ''
  const joinCode = code.value.trim().toUpperCase()
  const name = callSign.value.trim()
  if (!joinCode || !name) return
  try {
    const answer = await roleOf(joinCode, name)
    if (answer.name_taken) {
      callSign.value = randomCallSign()
      error.value = 'Der Funkrufname ist schon vergeben. Ein neuer wurde vorgeschlagen.'
      return
    }
    navigate(joinPath(answer.role, joinCode, name))
  } catch {
    error.value = 'Zu diesem Code gibt es keine Übung.'
  }
}
</script>

<template>
  <main class="mx-auto flex w-full max-w-4xl flex-col gap-8 px-4 py-10 md:px-6">
    <div class="flex flex-col gap-2">
      <p class="eyebrow m-0">Funkübung für Feuerwehren</p>
      <h1 class="headline m-0 text-4xl">Funkverkehr und Fahrzeugstatus üben</h1>
      <p class="m-0 max-w-2xl text-muted">
        Status Sim spielt eine Funkübung zwischen Leitstelle, Staffelführer und Fahrzeugen. Jede Rolle nutzt ihr
        eigenes Gerät: Fahrzeuge setzen ihren Status über ein Statusfeld, die Leitstelle sieht alle Meldungen und
        gibt Einsätze aus vorbereiteten Szenarien heraus.
      </p>
    </div>
    <div class="grid gap-4 sm:grid-cols-2">
      <form class="flex flex-col gap-3 rounded-sm border border-default bg-default p-5" @submit.prevent="create">
        <h2 class="section-title m-0">Neue Übung anlegen</h2>
        <p class="m-0 text-sm text-muted">
          Du übernimmst die Leitstelle und bekommst die Codes für Fahrzeuge und Staffelführer.
        </p>
        <TextField v-model="dispatchName" label="Name der Leitstelle"/>
        <UButton type="submit" class="mt-auto justify-center" size="lg">Leitstelle erstellen</UButton>
      </form>
      <form class="flex flex-col gap-3 rounded-sm border border-default bg-default p-5" @submit.prevent="join">
        <h2 class="section-title m-0">Einer Übung beitreten</h2>
        <p class="m-0 text-sm text-muted">
          Mit einem Code der Leitstelle trittst du als Fahrzeug oder als Staffelführer bei.
        </p>
        <TextField v-model="code" label="Code"/>
        <TextField v-model="callSign" label="Funkrufname"/>
        <UButton type="submit" class="justify-center" size="lg" variant="outline">Beitreten</UButton>
      </form>
    </div>
    <p v-if="error" role="alert" class="m-0 font-semibold text-error">{{ error }}</p>
    <ul class="m-0 grid list-none gap-4 p-0 sm:grid-cols-3">
      <li v-for="feature in FEATURES" :key="feature.title" class="flex flex-col gap-1.5">
        <UIcon :name="feature.icon" class="size-5 text-signal" aria-hidden="true"/>
        <h2 class="m-0 text-base font-semibold text-highlighted">{{ feature.title }}</h2>
        <p class="m-0 text-sm text-muted">{{ feature.text }}</p>
      </li>
    </ul>
    <p class="m-0 text-center text-sm text-muted">
      Eine Übung wird sieben Tage nach dem letzten Zugriff gelöscht.
      <a href="/hilfe" class="font-semibold text-default underline">So funktioniert Status Sim</a>
    </p>
  </main>
</template>
