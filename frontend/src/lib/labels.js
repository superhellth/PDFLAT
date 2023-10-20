/*
tailwind please do not purge:
bg-pink-200
bg-red-200
bg-green-200
bg-blue-200
bg-purple-200
bg-orange-200
bg-yellow-200
bg-sky-200
bg-lime-200
bg-gray-200

border-pink-400
border-red-400
border-green-400
border-blue-400
border-purple-400
border-orange-400
border-yellow-400
border-sky-400
border-lime-400
border-gray-400
*/

export const LABELS = {
  text: {
    id: 0,
    color: 'blue'
  },
  title: {
    id: 1,
    color: 'red'
  },
  table: {
    id: 2,
    color: 'green'
  },
  figure: {
    id: 3,
    color: 'purple'
  },
  list: {
    id: 4,
    color: 'orange'
  },
  caption: {
    id: 5,
    color: 'yellow'
  },
  page_nr: {
    id: 6,
    color: 'sky'
  },
  footnote: {
    id: 7,
    color: 'lime'
  },
  none: {
    id: -1,
    color: 'gray'
  }
};

export function getLabelColorByID(id) {
  const label = Object.values(LABELS).find(label => label.id === id);
  return label ? label.color : null;
}
