/* global L, window, DLMaps */

import utils from '../helpers/utils.js'
import mapUtils from './map-utils.js'

function LayerControls ($module, leafletMap) {
  this.$module = $module
  this.map = leafletMap
}

LayerControls.prototype.init = function (params) {
  this.setupOptions(params)
  // returns a node list so convert to array
  var $controls = this.$module.querySelectorAll(this.layerControlSelector)
  this.$controls = Array.prototype.slice.call($controls)
  this.datasetNames = this.$controls.map($control => $control.dataset.layerControl)

  // setup default options for geojsonFeatureLayers
  const boundGetLayerStyleOption = this.getLayerStyleOption.bind(this)
  const boundPointToLayer = this.defaultPointToLayer.bind(this)
  const boundOnEachFeature = this.onEachFeature.bind(this)
  this.geoJsonLayerOptions = {
    style: boundGetLayerStyleOption,
    pointToLayer: function (feature, latlng) {
      console.log('running pointToLayer on', feature)
      boundPointToLayer(feature, latlng)
    },
    onEachFeature: boundOnEachFeature
  }
  // create mapping between dataset and layer, one per control item
  this.layerMap = this.createAllFeatureLayers()

  // listen for changes to URL
  var boundSetControls = this.setControls.bind(this)
  window.addEventListener('popstate', function (event) {
    console.log('URL has changed - back button')
    boundSetControls()
  })

  // initial set up of controls (default or urlParams)
  const urlParams = (new URL(document.location)).searchParams
  if (!urlParams.has('layer')) {
    // if not set then use default checked controls
    this.updateURL()
  } else {
    // use URL params if available
    this.setControls()
  }

  // listen for changes on each checkbox
  const boundControlChkbxChangeHandler = this.onControlChkbxChange.bind(this)
  this.$controls.forEach(function ($control) {
    console.log(this)
    $control.addEventListener('change', boundControlChkbxChangeHandler, true)
  }, this)

  return this
}

LayerControls.prototype.onControlChkbxChange = function (e) {
  console.log("I've been toggled", e.target, this)
  // get the control containing changed checkbox
  var $clickedControl = e.target.closest(this.layerControlSelector)

  // when a control is changed update the URL params
  this.updateURL()

  // run provided callback
  const enabled = this.getCheckbox($clickedControl).checked
  if (this.toggleControlCallback && utils.isFunction(this.toggleControlCallback)) {
    this.toggleControlCallback(this.map, this.getDatasetName($clickedControl), enabled)
  }
}

// should this return an array or a single control?
LayerControls.prototype.getControlByName = function (dataset) {
  for (let i = 0; i < this.$controls.length; i++) {
    const $control = this.$controls[i]
    if ($control.dataset.layerControl === dataset) {
      return $control
    }
  }
  return undefined
}

LayerControls.prototype.createFeatureLayer = function () {
  return L.geoJSON(false, this.geoJsonLayerOptions).addTo(this.map)
}

// function brownfieldGeojsonToLayer (geojson, options) {
//   return L.geoJSON(geojson, {
//     pointToLayer: plot,
//     onEachFeature: options.onEachFeature || bindBrownfieldPopup
//   })
// }

LayerControls.prototype.createAllFeatureLayers = function () {
  const layerToDatasetMap = {}
  const that = this
  this.$controls.forEach(function ($control) {
    const dataset = that.getDatasetName($control)
    let layer
    if (dataset === 'brownfield-land') {
      layer = DLMaps.brownfieldSites.geojsonToLayer(false, that.geoJsonLayerOptions).addTo(that.map)
    } else if (dataset === 'listed-building') {
      const boundPointToLayer = that.defaultPointToLayer.bind(that)
      const boundOnEachFeature = that.onEachFeature.bind(that)
      const options = {
        pointToLayer: function (feature, latlng) {
          console.log('running pointToLayer on', feature, feature.properties.hectare)
          return boundPointToLayer(feature, latlng)
        },
        onEachFeature: boundOnEachFeature
      }
      layer = L.geoJSON(false, options).addTo(that.map)
    } else {
      layer = that.createFeatureLayer()
    }
    layerToDatasetMap[dataset] = layer
  })
  return layerToDatasetMap
}

LayerControls.prototype.getLayerStyleOption = function (feature) {
  // gets the layer control and looks for style settings
  const colour = this.getStyle(this.getControlByName(feature.properties.type))
  if (typeof colour === 'undefined') {
    return { color: '#003078', weight: 2 }
  } else {
    return { color: colour, weight: 2 }
  }
}

LayerControls.prototype.enable = function ($control) {
  console.log('enable', this.getDatasetName($control))
  const $chkbx = $control.querySelector('input[type="checkbox"]')
  $chkbx.checked = true
  $control.dataset.layerControlActive = 'true'
  $control.classList.remove(this.layerControlDeactivatedClass)
}

LayerControls.prototype.disable = function ($control) {
  console.log('disable', this.getDatasetName($control))
  const $chkbx = $control.querySelector('input[type="checkbox"]')
  $chkbx.checked = false
  $control.dataset.layerControlActive = 'false'
  $control.classList.add(this.layerControlDeactivatedClass)
}

LayerControls.prototype.setControls = function () {
  const urlParams = (new URL(document.location)).searchParams

  if (urlParams.has('layer')) {
    // get the names of the enabled and disabled layers
    // only care about layers that exist
    const enabledLayerNames = urlParams.getAll('layer').filter(name => this.datasetNames.indexOf(name) > -1)
    console.log('Enable:', enabledLayerNames)

    const datasetNamesClone = [].concat(this.datasetNames)
    const disabledLayerNames = datasetNamesClone.filter(name => enabledLayerNames.indexOf(name) === -1)

    // map the names to the controls
    const toEnable = enabledLayerNames.map(name => this.getControlByName(name))
    const toDisable = disabledLayerNames.map(name => this.getControlByName(name))
    console.log(toEnable, toDisable)

    // pass correct this arg
    toEnable.forEach(this.enable, this)
    toDisable.forEach(this.disable, this)
  }
}

LayerControls.prototype.updateURL = function () {
  const urlParams = (new URL(document.location)).searchParams
  const enabledLayers = this.enabledLayers().map($control => this.getDatasetName($control))

  urlParams.delete('layer')
  enabledLayers.forEach(name => urlParams.append('layer', name))
  console.log(urlParams.toString())
  const newURL = window.location.pathname + '?' + urlParams.toString() + window.location.hash
  // add entry to history, does not fire event so need to call setControls
  window.history.pushState({}, '', newURL)
  this.setControls()
}

LayerControls.prototype.getCheckbox = function ($control) {
  return $control.querySelector('input[type="checkbox"]')
}

LayerControls.prototype.enabledLayers = function () {
  return this.$controls.filter($control => this.getCheckbox($control).checked)
}

LayerControls.prototype.disabledLayers = function () {
  return this.$controls.filter($control => !this.getCheckbox($control).checked)
}

LayerControls.prototype.getDatasetName = function ($control) {
  return $control.dataset.layerControl
}

LayerControls.prototype.getZoomRestriction = function ($control) {
  return $control.dataset.layerControlZoom
}

LayerControls.prototype.getStyle = function ($control) {
  return $control.dataset.layerColour
}

LayerControls.prototype.defaultOnEachFeature = function (feature, layer) {
  console.debug('onEachFeature run')
  if (feature.properties) {
    layer.bindPopup(`
      <h3>${feature.properties.name}</h3>
      ${feature.properties.type}<br>
      <a href=${this.baseUrl}${feature.properties.slug}>${feature.properties.slug}</a>
    `)
  }
}

LayerControls.prototype.defaultPointToLayer = function (feature, latlng) {
  console.log('plot circle marker')
  // gets the layer control and looks for style settings
  const colour = this.getStyle(this.getControlByName(feature.properties.type))
  const style = mapUtils.circleMarkerStyle(colour)
  var size = mapUtils.setCircleSize(feature.properties.hectares, 10)
  style.radius = size.toFixed(2)
  console.log(style, latlng)
  return L.circle(latlng, style)
}

LayerControls.prototype.setupOptions = function (params) {
  params = params || {}
  this.layerControlSelector = params.layerControlSelector || '[data-layer-control]'
  this.layerControlDeactivatedClass = params.layerControlDeactivatedClass || 'deactivated-control'
  this.toggleControlCallback = params.toggleControlCallback || undefined
  this.onEachFeature = params.onEachFeature || this.defaultOnEachFeature
  this.baseUrl = params.baseUrl || 'http://digital-land.github.io'
}

export default LayerControls
