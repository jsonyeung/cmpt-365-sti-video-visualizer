const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin');
const GoogleFontsPlugin = require('@beyonk/google-fonts-webpack-plugin')
const { sass } = require('svelte-preprocess-sass')

const mode = process.env.NODE_ENV || 'development'
const prod = mode === 'production'

module.exports = {
  entry: './src/renderer/main.js',
  module: {
    rules: [
      {
        test: /\.svelte$/i,
        use: [{
          loader: 'svelte-loader',
          options: {
            preprocess: {
              style: sass()
            }
          }
        }]
      },
      {
        test: /\.scss$/i,
        use: [
          'style-loader',
          'css-loader',
          'sass-loader',
        ],
      },
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './src/renderer/index.html'
    }),
    new GoogleFontsPlugin({
      fonts: [
          // { family: 'Inter', variants: ['500', '700'] }
      ]
    })
  ],
  devServer: {
    contentBase: './dist',
    port: 8080,
    hot: true,
  },

  resolve: {
		alias: { svelte: path.resolve('node_modules', 'svelte') },
		extensions: ['.mjs', '.js', '.svelte'],
		mainFields: ['svelte', 'browser', 'module', 'main']
  },
  devtool: prod ? false: 'source-map'
}