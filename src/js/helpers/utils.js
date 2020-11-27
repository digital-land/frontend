var utils = {}

function camelCaseReplacer (match, s) {
  return s.toUpperCase()
}

utils.toCamelCase = function (s) {
  return s.toLowerCase().replace(/[^a-zA-Z0-9]+(.)/g, camelCaseReplacer)
}

export default utils
