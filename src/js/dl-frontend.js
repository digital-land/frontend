import BackToTop from './dl-components/back-to-top'
import FilterCheckboxes from './dl-components/filter-checkboxes'
import SelectedCounter from './dl-components/selected-counter'
import ScrollableTables from './dl-components/scrollable-table'
import LinkableTable from './dl-components/linkable-table'
import FilterList from './dl-components/filter-list'
import FilterHistorical from './dl-components/filter-historical'
import InputCopy from './dl-components/input-copy'
import FilterTimelineByDate from './dl-components/filter-timeline-by-date'
import AppTabs from './dl-components/app-tabs'
import SubNavTabs from './dl-components/sub-nav-tabs'

import utils from './helpers/utils.js'

function polyfill (options) {
  // polyfill for browsers without NodeList forEach method
  if (window.NodeList && !window.NodeList.prototype.forEach) {
    window.NodeList.prototype.forEach = window.Array.prototype.forEach
  }
}

export {
  polyfill,
  BackToTop,
  FilterCheckboxes,
  SelectedCounter,
  ScrollableTables,
  LinkableTable,
  FilterList,
  FilterHistorical,
  InputCopy,
  FilterTimelineByDate,
  AppTabs,
  SubNavTabs,
  utils
}
