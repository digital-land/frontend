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

/**
 * Create an organisation mapper. Maps organisation ids to names
 * @param  {Array} orgsObj Array of organisation objs. Must contain .id and .name propterties
 */
utils.createOrgMapper = function (orgsObj) {
  const mapper = {}
  orgsObj.forEach(function (o) {
    mapper[o.id] = o.name
  })
  return mapper
}

export default utils
