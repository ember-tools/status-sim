<script setup lang="ts">
/** What an exercise view shows when its code leads nowhere, for example after the exercise expired. */
defineProps<{ title: string }>()
</script>

<template>
  <main class="mx-auto w-full max-w-xl px-4 py-10">
    <UAlert color="warning" variant="subtle" icon="i-lucide-search-x" :title="title"
            description="Übungen werden sieben Tage nach dem letzten Zugriff gelöscht. Lege eine neue an oder prüfe den Code."
            :actions="[{label: 'Zur Startseite', href: '/', color: 'neutral', variant: 'outline'}]"/>
  </main>
</template>
