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
const del = require('del')
const postcss = require('gulp-postcss')
const autoprefixer = require('autoprefixer')
const sourcemaps = require('gulp-sourcemaps')
const plumber = require('gulp-plumber')
const babel = require('gulp-babel')

// set paths
const config = {
  scssPath: 'src/scss',
  destPath: 'digital_land_frontend/static',
  cssDestPath: 'digital_land_frontend/static/stylesheets',
  jsDestPath: 'digital_land_frontend/static/javascripts',
  govukPath: 'node_modules/govuk-frontend/govuk/',
  govukAssetDestPath: 'digital_land_frontend/static/govuk/assets'
}

const isDist = true

const cleanAll = () =>
  del(`${config.destPath}/**/*`)
cleanAll.description = 'Empty static dir'

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
    .pipe(sourcemaps.init())
    .pipe(
      sass({ outputStyle: 'expanded', includePaths: ['src/scss', 'node_modules/govuk-frontend/govuk'] })
    )
    .on('error', sass.logError)
    .pipe(postcss([autoprefixer({ grid: 'autoplace' })]))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest(config.cssDestPath))

// check .scss files against .sass-lint.yml config
const lintSCSS = () =>
  gulp
    .src('src/scss/**/*.s+(a|c)ss')
    .pipe(
      sassLint({
        files: { ignore: 'src/scss/styleguide/_highlight-style.scss' },
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
    .pipe(plumber())
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
    .pipe(
      babel({
        presets: [
          [
            '@babel/env',
            {
              modules: false
            }
          ]
        ]
      })
    )
    .pipe(eol())
    .pipe(gulp.dest(`${config.jsDestPath}`))
})

gulp.task('js-map:compile', () => {
  return gulp
    .src(['src/js/dl-maps.js', 'src/js/dl-maps/Leaflet.recentre.js'])
    .pipe(plumber())
    .pipe(
      rollup({
        // set the 'window' global
        name: 'DLMaps',
        // Legacy mode is required for IE8 support
        legacy: true,
        // UMD allows the published bundle to work in CommonJS and in the browser.
        format: 'umd'
      })
    )
    .pipe(
      babel({
        presets: [
          [
            '@babel/env',
            {
              modules: false
            }
          ]
        ]
      })
    )
    .pipe(eol())
    .pipe(gulp.dest(`${config.jsDestPath}`))
})

// Compile latest govuk-frontend.min.js
// ====================================
gulp.task('govukjs:minify', () => {
  return gulp.src(config.govukPath + 'all.js')
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
    .pipe(gulp.dest(`${config.jsDestPath}/govuk`))
})

// Tasks for copying assets to application
// ======================================
const copyVendorStylesheets = () =>
  gulp.src('src/stylesheets/**/*').pipe(gulp.dest(config.cssDestPath))

const copyGovukAssets = () =>
  gulp.src('node_modules/govuk-frontend/govuk/assets/**/*').pipe(gulp.dest(config.govukAssetDestPath))

const copyVendorJS = () =>
  gulp.src('src/js/vendor/*.js').pipe(gulp.dest(`${config.jsDestPath}/vendor`))

const copyCookieJS = () =>
  gulp.src('src/js/dl-cookies.js').pipe(gulp.dest(`${config.jsDestPath}/`))

// need to replace this with task to run js through Babel
const copyNationalMapJS = () =>
  gulp.src('src/js/dl-national-map-controller.js').pipe(gulp.dest(`${config.jsDestPath}/`))

const copyImagesForStylesheets = () =>
  gulp.src('src/images/**/*').pipe(gulp.dest(config.cssDestPath))

// Tasks to expose to CLI
// ======================
const latestVendorAssets = gulp.parallel(
  copyVendorStylesheets,
  copyGovukAssets,
  copyVendorJS,
  'govukjs:minify'
)
latestVendorAssets.description = 'Copy all govuk and vendor assets to package'

const latestStylesheets = gulp.series(
  cleanCSS,
  lintSCSS,
  compileStylesheets,
  copyVendorStylesheets,
  copyImagesForStylesheets
)
latestStylesheets.description = 'Generate the latest stylesheets'

const latestJS = gulp.parallel(
  copyCookieJS,
  copyNationalMapJS,
  'js:compile',
  'js-map:compile'
)
latestJS.description = 'Compile and copy latest digital land javascripts'

exports.stylesheets = latestStylesheets
exports.assets = latestVendorAssets
exports.js = latestJS
exports.clean = cleanAll

// set of tasks when $ gulp command is run
exports.default = gulp.series(cleanAll, gulp.parallel(latestStylesheets, latestJS), latestVendorAssets)
