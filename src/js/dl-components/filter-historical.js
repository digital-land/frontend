import '../../../node_modules/govuk-frontend/govuk/vendor/polyfills/Function/prototype/bind'

function convertNodeListToArray (nl) {
  return Array.prototype.slice.call(nl)
}

function toBool (s) {
  if (typeof s === 'boolean') {
    return s
  }
  const truey = ['t', 'True', 'true', 'T']
  const falsey = ['f', 'false', 'False', 'F']
  if (falsey.includes(s)) {
    return false
  }
  if (truey.includes(s)) {
    return true
  }
  return undefined
}

// Back to top module as seen in govuk-design-system
// https://github.com/alphagov/collections/blob/e1f3c74facd889426d24ac730ed0057aa64e2801/app/assets/javascripts/organisation-list-filter.js
function FilterHistorical ($form) {
  this.$form = $form
  this.$chkbx = $form.querySelector('input')
}

FilterHistorical.prototype.init = function (params) {
  this.setupOptions(params)
  const $chkbx = this.$chkbx
  // start with box checked
  $chkbx.checked = true

  // get all items
  this.itemsToToggle = convertNodeListToArray(document.querySelectorAll('[data-historical-item="true"]'))
  this.listsToFilter = convertNodeListToArray(document.querySelectorAll('[data-historical="list"]'))

  if (this.itemsToToggle.length > 0) {
    // form starts off hidden
    this.$form.classList.remove('js-hidden')
    var boundFilterList = this.filterList.bind(this)
    this.$chkbx.addEventListener('change', boundFilterList)
  }

  // should we show counts for each list
  if (this.showCountsWhenShowingAll) {
    this.toggleAllCountElements(true)
  }

  // TODO: not sure this is needed now
  const boundHide = this.hide.bind(this)
  if (params.triggerEvents) {
    // listen for custom events
    this.listsToFilter.forEach(function (lst) {
      lst.addEventListener(params.triggerEvents, function (e) {
        // only need to do something if 'show historical' checkbox is NOT checked
        if (!$chkbx.checked) {
          boundHide(lst)
        }
      })
    })
  }
}

FilterHistorical.prototype.filterList = function (e) {
  const listsToFilter = this.listsToFilter
  const that = this

  if (this.$chkbx.checked) {
    this.show()
  } else {
    listsToFilter.forEach(function (lst) {
      that.hide(lst)
    })
  }
}

FilterHistorical.prototype.show = function () {
  this.itemsToToggle.forEach(function (item) {
    item.classList.remove('js-hidden--historical')
  })
  this.countAllVisible()
  // only hide the counts if this option set to true
  if (!this.showCountsWhenShowingAll) {
    this.toggleAllCountElements(false)
  }
}

FilterHistorical.prototype.hide = function (lst) {
  const itemsToHide = convertNodeListToArray(lst.querySelectorAll('[data-historical-item="true"]'))
  itemsToHide.forEach(function (item) {
    item.classList.add('js-hidden--historical')
  })
  this.countVisible(lst)
  this.toggleAllCountElements(true)
}

FilterHistorical.prototype.countVisible = function (lst) {
  const items = convertNodeListToArray(lst.querySelectorAll('[data-historical-item]'))
  let count = 0
  function isHidden (el) {
    var style = window.getComputedStyle(el)
    return ((style.display === 'none') || (style.visibility === 'hidden'))
  }
  items.forEach(function (el) {
    if (!isHidden(el)) {
      count = count + 1
    }
  })
  this.updateCount(lst, count)

  return count
}

FilterHistorical.prototype.countAllVisible = function () {
  const lists = this.listsToFilter
  const that = this
  let count = 0
  lists.forEach(function (lst) {
    count = count + that.countVisible(lst)
  })
}

FilterHistorical.prototype.getCountWrapper = function (lst) {
  const listWrapperSelector = this.listWrapperSelector
  const countWrapperSelector = this.countWrapperSelector
  const listWrapper = lst.closest(listWrapperSelector)
  if (!listWrapper) {
    console.log(lst, 'has no count element')
  }
  const countWrapper = listWrapper.querySelector(countWrapperSelector)
  return countWrapper
}

FilterHistorical.prototype.updateCount = function (lst, count) {
  const listWrapperSelector = this.listWrapperSelector
  const countWrapperSelector = this.countWrapperSelector
  var listWrapper = lst.closest(listWrapperSelector)
  var countWrapper = listWrapper.querySelector(countWrapperSelector)

  // if this list has it's own count
  if (countWrapper) {
    // display it
    this.updateCountText(countWrapper, count)
  }
}

FilterHistorical.prototype.updateCountText = function (countWrapper, count) {
  var listCount = countWrapper.querySelector('.js-list-count')
  var accessibleListCount = countWrapper.querySelector('.js-accessible-list-count')
  listCount.textContent = count
  if (accessibleListCount) {
    accessibleListCount.textContent = count
  }
}

FilterHistorical.prototype.toggleAllCountElements = function (show) {
  const that = this
  this.listsToFilter.forEach(function (lst) {
    that.toggleCountElement(lst, show)
  })
}

FilterHistorical.prototype.toggleCountElement = function (lst, show) {
  const countWrapper = this.getCountWrapper(lst)
  if (countWrapper) {
    if (show) {
      countWrapper.classList.remove('govuk-visually-hidden')
    } else {
      countWrapper.classList.add('govuk-visually-hidden')
    }
  }
}

FilterHistorical.prototype.setupOptions = function (params) {
  params = params || {}
  this.listWrapperSelector = params.listWrapperSelector || '.list-wrapper'
  this.countWrapperSelector = params.countWrapperSelector || '.count-wrapper'
  this.showCountsWhenShowingAll = (typeof (params.showCountsWhenShowingAll) !== 'undefined') ? toBool(params.showCountsWhenShowingAll) : false
}

export default FilterHistorical
