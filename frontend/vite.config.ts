import {emberbox} from '@emberbox/ui/vite'
import vue from '@vitejs/plugin-vue'
import {defineConfig} from 'vite'

const backend = process.env.BACKEND_URL ?? 'http://localhost:8000'

export default defineConfig({
    plugins: [
        vue(),
        emberbox({
            url: 'https://statussim.emberbox.app',
            logo: 'statussim',
            router: false,
        }),
    ],
    server: {
        host: true,
        proxy: {
            '/api': backend,
        },
    },
})
