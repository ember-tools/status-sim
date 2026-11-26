import {emberbox, helpPaths} from '@emberbox/ui/vite'
import vue from '@vitejs/plugin-vue'
import {defineConfig} from 'vite'
import {HELP_TOPICS} from './src/helpTopics'

const backend = process.env.BACKEND_URL ?? 'http://localhost:8000'

export default defineConfig({
    plugins: [
        vue(),
        emberbox({
            url: 'https://statussim.emberbox.app',
            logo: 'statussim',
            app: {name: 'Status Sim', description: 'Funkverkehr und Fahrzeugstatus üben.'},
            router: false,
            prerender: {entry: 'src/prerender.ts', paths: ['/', ...helpPaths(HELP_TOPICS)]},
        }),
    ],
    server: {
        host: true,
        proxy: {
            '/api': backend,
        },
    },
})
