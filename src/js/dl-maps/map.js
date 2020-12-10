import utils from '../helpers/utils.js'

/* global L, fetch */

// govuk consistent colours
var colours = {
  lightBlue: '#1d70b8',
  darkBlue: '#003078',
  brown: '#594d00',
  yellow_brown: '#a0964e',
  black: '#0b0c0c'
}

const boundaryStyle = {
  fillOpacity: 0.2,
  weight: 2,
  color: colours.darkBlue,
  fillColor: colours.lightBlue
}

const boundaryHoverStyle = {
  fillOpacity: 0.25,
  weight: 2,
  color: colours.black,
  fillColor: colours.darkBlue
}

function Map ($module) {
  this.$module = $module
  this.$wrapper = $module.closest('.dl-map__wrapper')
}

Map.prototype.init = function (params) {
  this.setupOptions(params)
  this.tiles = this.setTiles()
  this.map = this.createMap()
  this.featureGroups = {}
  this.styles = {
    defaultBoundaryStyle: boundaryStyle,
    defaultBoundaryHoverStyle: boundaryHoverStyle
  }
  this.$loader = this.$wrapper.querySelector('.dl-map__loader')

  this.geojsonUrls = params.geojsonURLs || []
  const geojsonOptions = params.geojsonOptions || {}
  this.geojsonUrls = this.extractURLS()
  // if pointers to geojson provided add to the default featureGroup (a featureGroup has getBounds() func)
  if (this.geojsonUrls.length) {
    this.createFeatureGroup('initBoundaries').addTo(this.map)
    this.plotBoundaries(this.geojsonUrls, geojsonOptions)
  }

  return this
}

Map.prototype.setTiles = function () {
  return L.tileLayer('https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png', {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  })
}

Map.prototype.addStyle = function (name, style) {
  this.styles[name] = style
}

/**
 * Add event listeners for hovering a layer
 * @param  {Object} layer A leaflet layer (e.g. a polygon)
 * @param  {Object} options Options for configuring hover interaction
 *    {Func} .check Check to decide whether styles+ should be performed
 *    {Object} .defaultStyle Leaflet style object to apply when not hovered
 *    {Object} .hoverStyle Leaflet style object to apply when hovered
 *    {Func} .cb Optional callback to trigger, accepts cb(layer <- leaflet layer, hovered <- boolean)
 */
Map.prototype.addLayerHoverState = function (layer, options) {
  const hasCheck = (options.check && isFunction(options.check))
  const defaultStyle = options.defaultStyle || this.styles.defaultBoundaryStyle
  const hoverStyle = options.hoverStyle || this.styles.defaultBoundaryHoverStyle
  layer.on('mouseover', function () {
    if ((hasCheck) ? options.check(layer) : true) {
      layer.setStyle(hoverStyle)
      if (options.cb && utils.isFunction(options.cb)) { options.cb(layer, true) }
    }
  })
  layer.on('mouseout', function () {
    if ((hasCheck) ? options.check(layer) : true) {
      layer.setStyle(defaultStyle)
      if (options.cb && utils.isFunction(options.cb)) { options.cb(layer, false) }
    }
  })
}

Map.prototype.createMap = function () {
  const opts = this.options
  var latLng = L.latLng(opts.default_pos[0], opts.default_pos[1])
  return L.map(this.mapId, {
    center: latLng,
    zoom: opts.default_zoom,
    minZoom: opts.minZoom,
    maxZoom: opts.maxZoom,
    layers: [this.tiles]
  })
}

Map.prototype.createFeatureGroup = function (name, options) {
  const _options = options || {}
  if (Object.prototype.hasOwnProperty.call(this.featureGroups, name)) {
    return this.featureGroups[name]
  }
  const fG = L.featureGroup([], _options)
  this.featureGroups[name] = fG
  return fG
}

Map.prototype.setMapHeight = function (height) {
  const h = height || (2 / 3)
  const $map = this.$module
  const width = $map.offsetWidth
  const v = (h < 1) ? width * h : h

  $map.style.height = v + 'px'
  this.map.invalidateSize()
}

Map.prototype.zoomToLayer = function (layer) {
  this.map.fitBounds(layer.getBounds())
}

Map.prototype.extractURLS = function () {
  var urlsStr = this.$module.dataset.geojsonUrls
  var urlList = this.geojsonUrls

  function isListed (value, arr) {
    return arr.indexOf(value) > -1
  }

  if (typeof urlsStr !== 'undefined') {
    urlsStr.split(';').forEach(function (url) {
      if (!isListed(url, urlList)) {
        urlList.push(url)
      }
    })
  }
  return urlList
}

Map.prototype.hideLoader = function () {
  if (this.$loader) {
    this.$loader.classList.add('js-hidden')
  }
}

Map.prototype.geojsonLayer = function (data, type, options) {
  const style = options.style || this.styles.defaultBoundaryStyle
  const onEachFeature = options.onEachFeature || function () {}
  if (type === 'point') {
    return L.geoJSON(data, {
      pointToLayer: options.pointToLayer,
      onEachFeature: onEachFeature
    })
  }
  return L.geoJSON(data, {
    style: style,
    onEachFeature: onEachFeature
  })
}

Map.prototype.plotBoundaries = function (urls, options) {
  const that = this
  const map = this.map
  const defaultFG = this.featureGroups.initBoundaries
  const _type = options.type || 'polygon'
  var count = 0
  urls.forEach(function (url) {
    fetch(url)
      .then((response) => {
        return response.json()
      })
      .then((data) => {
        const layer = options.geojsonDataToLayer(data, options) || that.geojsonLayer(data, _type, options)
        layer.addTo(defaultFG)
        count++
        // only pan map once all boundaries have loaded
        if (count === urls.length) {
          map.fitBounds(defaultFG.getBounds())
        }
      })
  })
}

Map.prototype.setupOptions = function (params) {
  params = params || {}
  this.options = {
    default_pos: params.default_pos || [52.561928, -1.464854],
    default_zoom: params.minZoom || 6,
    minZoom: params.minZoom || 6,
    maxZoom: params.maxZoom || 16
  }
  this.mapId = params.mapId || 'aMap'
}

export default Map
