import { defineComponent, h, type PropType } from 'vue'

type Shape = ['path', string] | ['circle', number, number, number] | ['rect', number, number, number, number, number]

// Line icons on a 24px grid, drawn with currentColor so they follow the text colour.
const ICONS = {
  lens: [['circle', 10.5, 10.5, 7], ['path', 'm15.5 15.5 5 5'], ['path', 'm7.5 10.5 2 2 4-4']],
  moon: [['path', 'M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z']],
  sun: [['circle', 12, 12, 4], ['path', 'M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4']],
  external: [['path', 'M15 3h6v6'], ['path', 'M10 14 21 3'], ['path', 'M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6']],
  shield: [['path', 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z']],
  target: [['circle', 12, 12, 10], ['circle', 12, 12, 6], ['circle', 12, 12, 2]],
  layout: [['rect', 3, 3, 18, 18, 2], ['path', 'M3 9h18'], ['path', 'M9 21V9']],
  upload: [['path', 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'], ['path', 'm17 8-5-5-5 5'], ['path', 'M12 3v12']],
  download: [['path', 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'], ['path', 'm7 10 5 5 5-5'], ['path', 'M12 15V3']],
  arrowRight: [['path', 'M5 12h14'], ['path', 'm12 5 7 7-7 7']],
  chevronRight: [['path', 'm9 18 6-6-6-6']],
  chevronDown: [['path', 'm6 9 6 6 6-6']],
  lock: [['rect', 3, 11, 18, 11, 2], ['path', 'M7 11V7a5 5 0 0 1 10 0v4']],
  file: [['path', 'M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z'], ['path', 'M14 3v5h5']],
  plus: [['path', 'M12 5v14'], ['path', 'M5 12h14']],
  gauge: [['path', 'M12 14l4-4'], ['path', 'M3.3 19a10 10 0 1 1 17.4 0']],
  list: [['path', 'M9 6h11'], ['path', 'M9 12h11'], ['path', 'M9 18h11'], ['path', 'M4 6h.01'], ['path', 'M4 12h.01'], ['path', 'M4 18h.01']],
  tag: [['path', 'M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z'], ['circle', 7.5, 7.5, 1.5]],
  briefcase: [['rect', 2, 7, 20, 14, 2], ['path', 'M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2']],
  bulb: [['path', 'M9 18h6'], ['path', 'M10 22h4'], ['path', 'M12 2a7 7 0 0 0-4 12.7V16h8v-1.3A7 7 0 0 0 12 2z']],
  alert: [['path', 'M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z'], ['path', 'M12 9v4'], ['path', 'M12 17h.01']],
  checkCircle: [['path', 'M22 11.1V12a10 10 0 1 1-5.9-9.1'], ['path', 'm9 11 3 3L22 4']],
  check: [['path', 'm5 12 5 5L20 7']],
  x: [['path', 'M18 6 6 18'], ['path', 'm6 6 12 12']],
  menu: [['path', 'M4 6h16'], ['path', 'M4 12h16'], ['path', 'M4 18h16']],
  copy: [['rect', 9, 9, 13, 13, 2], ['path', 'M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1']],
} satisfies Record<string, Shape[]>

export type IconName = keyof typeof ICONS

export default defineComponent({
  name: 'AppIcon',
  props: {
    name: { type: String as PropType<IconName>, required: true },
    size: { type: [Number, String], default: 18 },
    strokeWidth: { type: [Number, String], default: 2 },
    label: { type: String, default: '' },
  },
  setup(props) {
    return () =>
      h(
        'svg',
        {
          width: props.size,
          height: props.size,
          viewBox: '0 0 24 24',
          fill: 'none',
          stroke: 'currentColor',
          'stroke-width': props.strokeWidth,
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          ...(props.label ? { role: 'img', 'aria-label': props.label } : { 'aria-hidden': 'true' }),
          focusable: 'false',
        },
        (ICONS[props.name] as Shape[]).map((shape) => {
          if (shape[0] === 'path') return h('path', { d: shape[1] })
          if (shape[0] === 'circle') return h('circle', { cx: shape[1], cy: shape[2], r: shape[3] })
          return h('rect', { x: shape[1], y: shape[2], width: shape[3], height: shape[4], rx: shape[5] })
        }),
      )
  },
})
