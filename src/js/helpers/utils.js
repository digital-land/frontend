var utils = {}

function camelCaseReplacer (match, s) {
  return s.toUpperCase()
}

utils.curie_to_url_part = function (curie) {
  return curie.replace(':', '/')
}

utils.toCamelCase = function (s) {
  return s.toLowerCase().replace(/[^a-zA-Z0-9]+(.)/g, camelCaseReplacer)
}

utils.truncate = function (s, len) {
  return s.slice(0, len) + '...'
}

export default utils
