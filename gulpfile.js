'use strict'

const gulp = require('gulp')
const sass = require('gulp-sass')
const sassLint = require('gulp-sass-lint')
const clean = require('gulp-clean')
const rollup = require('gulp-better-rollup')
const eol = require('gulp-eol')
const gulpif = require('gulp-if')
const rename = require('gulp-rename')
const uglify = require('gulp-uglify')

// set paths
const config = {
  scssPath: 'src/scss',
  cssDestPath: 'digital_land_frontend/static/stylesheets',
  jsDestPath: 'digital_land_frontend/static/javascripts',
  govukPath: 'node_modules/govuk-frontend/govuk/',
  govukAssetDestPath: 'digital_land_frontend/static/govuk/assets'
}

const isDist = true

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

// Compile dl-frontend.js
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
    .pipe(eol())
    .pipe(gulp.dest(`${config.jsDestPath}`))
})

// build latest govuk-frontend.min.js
gulp.task('govukjs:compile', () => {
  // for dist/ folder we only want compiled 'all.js' file
  const srcFiles = config.govukPath + 'all.js'

  return gulp.src([
    srcFiles
  ])
    .pipe(rollup({
      // Used to set the `window` global and UMD/AMD export name.
      name: 'GOVUKFrontend',
      // Legacy mode is required for IE8 support
      legacy: true,
      // UMD allows the published bundle to work in CommonJS and in the browser.
      format: 'umd'
    }))
    .pipe(gulpif(isDist, uglify({
      ie8: true
    })))
    .pipe(gulpif(isDist,
      rename({
        basename: 'govuk-frontend',
        extname: '.min.js'
      })
    ))
    .pipe(eol())
    .pipe(gulp.dest(`${config.jsDestPath}`))
})

// Tasks for copying assets to application
// ======================================
const copyVendorStylesheets = () =>
  gulp.src('src/stylesheets/**/*').pipe(gulp.dest(config.cssDestPath))

const copyGovukAssets = () =>
  gulp.src('node_modules/govuk-frontend/govuk/assets/**/*').pipe(gulp.dest(config.govukAssetDestPath))

const copyVendorJS = () =>
  gulp.src('src/js/vendor/*.js').pipe(gulp.dest(`${config.jsDestPath}/vendor`))

// Tasks to expose to CLI
// ======================
const latestVendorAssets = gulp.parallel(
  copyVendorStylesheets,
  copyGovukAssets,
  copyVendorJS,
  'govukjs:compile'
)
latestVendorAssets.description = 'Copy all govuk and vendor assets to package';

const latestStylesheets = gulp.series(
  cleanCSS,
  lintSCSS,
  compileStylesheets
)
latestStylesheets.description = 'Generate the latest stylesheets'

exports.default = latestStylesheets
exports.stylesheets = latestStylesheets
exports.assets = latestVendorAssets
