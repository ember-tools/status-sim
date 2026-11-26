/**
 * What the script linters read: the frontend, its configs, the backend and its tests, and for the
 * em dash also the styles, the page shell, the scenarios, the build and CI files and the README.
 * Paths are relative to the repository root.
 */
export default {
    root: '..',
    sources: [
        {path: 'frontend/src', extensions: ['.ts', '.vue', '.js', '.mjs']},
        {path: 'frontend/eslint.config.mjs', extensions: null},
        {path: 'frontend/emberbox-lint.config.mjs', extensions: null},
        {path: 'frontend/vite.config.ts', extensions: null},
        {path: 'src', extensions: ['.py']},
        {path: 'tests', extensions: ['.py']},
    ],
    text: [
        {path: 'frontend/src', extensions: ['.css']},
        {path: 'frontend/index.html', extensions: null},
        {path: 'src/static/scenarios', extensions: ['.json']},
        {path: 'Dockerfile', extensions: null},
        {path: 'compose.yml', extensions: null},
        {path: 'compose.prod.yml', extensions: null},
        {path: '.github', extensions: ['.yml']},
        {path: 'toolchain.sh', extensions: null},
        {path: 'README.md', extensions: null},
    ],
    browserStorage: {catalogue: 'frontend/browser-storage.json', sources: 'frontend/src'},
    duplication: '.jscpd.json',
}
