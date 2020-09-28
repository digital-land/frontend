'use strict'

const gulp = require('gulp')
const sass = require('gulp-sass')
const sassLint = require('gulp-sass-lint')
const clean = require('gulp-clean')
const rollup = require('gulp-better-rollup')

// set paths
const config = {
  scssPath: 'src/scss',
  cssDestPath: 'digital-land-frontend/static/stylesheets',
  jsDestPath: 'digital-land-frontend/static/javascripts'
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

// check .scss files against .sass-lint.yml config
const lintSCSS = () =>
  gulp
    .src('src/scss/**/*.s+(a|c)ss')
    .pipe(
      sassLint({
        files: { ignore: '' },
        configFile: '.sass-lint.yml'
      })
    )
    .pipe(sassLint.format())
    .pipe(sassLint.failOnError())
lintSCSS.description = 'Check files follow GOVUK style'

// Compile application.js
// ======================
gulp.task('js:compile', () => {
  return gulp
    .src(['src/js/dl-frontend.js'])
    .pipe(
      rollup({
        // set the 'window' global
        name: 'DLFrontend',
        // Legacy mode is required for IE8 support
        legacy: true,
        // UMD allows the published bundle to work in CommonJS and in the browser.
        format: 'umd'
      })
    )
    .pipe(gulp.dest(`${config.jsDestPath}`))
})

// Tasks to expose to CLI
// ======================
const latestStylesheets = gulp.series(
  cleanCSS,
  lintSCSS,
  compileStylesheets
)
latestStylesheets.description = 'Generate the latest stylesheets'
exports.default = latestStylesheets
exports.stylesheets = latestStylesheets
