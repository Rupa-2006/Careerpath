/** A friendly icon and colour for each area, so students can find their way at a glance. */
export const AREAS: Record<string, { icon: string; colour: string }> = {
  engineering: { icon: '⚙️', colour: '#2f6db5' },
  computer: { icon: '💻', colour: '#5b4bc4' },
  medical: { icon: '🩺', colour: '#c0392b' },
  science: { icon: '🔬', colour: '#14746f' },
  commerce: { icon: '📊', colour: '#b7791f' },
  arts: { icon: '📚', colour: '#8e44ad' },
  law: { icon: '⚖️', colour: '#34495e' },
  agriculture: { icon: '🌾', colour: '#3c8d2f' },
  pharmacy: { icon: '💊', colour: '#d35400' },
  management: { icon: '💼', colour: '#2c3e50' },
  design: { icon: '🎨', colour: '#c2185b' },
  hospitality: { icon: '🏨', colour: '#a0522d' },
  aviation: { icon: '✈️', colour: '#1f7a9c' },
  defence: { icon: '🎖️', colour: '#4b5d2a' },
  government: { icon: '🏛️', colour: '#5d4037' },
  diploma: { icon: '🛠️', colour: '#616161' },
  vocational: { icon: '🧰', colour: '#00796b' },
}

export function areaOf(slug: string) {
  return AREAS[slug] ?? { icon: '🧭', colour: '#14746f' }
}
