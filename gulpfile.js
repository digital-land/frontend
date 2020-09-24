'use strict'

const gulp = require('gulp')
const sass = require('gulp-sass')
const clean = require('gulp-clean')

// set paths
const config = {
  scssPath: 'src/scss',
  cssDestPath: 'digital-land-frontend/static/stylesheets'
}

// Tasks used to generate latest stylesheets
// =========================================
const cleanCSS = () =>
  gulp
    .src(`${config.cssDestPath}/**/*`, { read: false })
    .pipe(clean())
cleanCSS.description = 'Delete old stylesheets files'

// compile scss to CSS
const compileStylesheets = () =>
  gulp
    .src(config.scssPath + '/*.scss')
    .pipe(
      sass({ outputStyle: 'expanded', includePaths: ['src/scss', 'node_modules/govuk-frontend/govuk'] })
    )
    .on('error', sass.logError)
    .pipe(gulp.dest(config.cssDestPath))

// Tasks to expose to CLI
// ======================
const latestStylesheets = gulp.series(
  cleanCSS,
  compileStylesheets
)
latestStylesheets.description = 'Generate the latest stylesheets'
exports.default = latestStylesheets
exports.stylesheets = latestStylesheets
