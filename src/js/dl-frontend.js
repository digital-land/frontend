import ScrollableTables from './dl-components/scrollable-table'

function polyfill (options) {
  // polyfill for browsers without NodeList forEach method
  if (window.NodeList && !window.NodeList.prototype.forEach) {
    window.NodeList.prototype.forEach = window.Array.prototype.forEach
  }
}

export {
  polyfill,
  ScrollableTables
}
