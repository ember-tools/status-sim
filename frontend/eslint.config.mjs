import {emberboxEslint} from '@emberbox/lint'

/** Which layer may not reach which: composables stand on no component or view, components on no view. */
const LAYERS = [
    {layer: 'composables', above: ['views', 'components']},
    {layer: 'components', above: ['views']},
]

export default await emberboxEslint({layers: LAYERS})
