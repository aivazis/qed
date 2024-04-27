// -*- javascript -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external dependencies
const path = require('path')
const webpack = require('webpack')
const HtmlWebpackPlugin = require('html-webpack-plugin');

// local geography
const rootDir = __dirname
const sourceDir = path.join(rootDir, 'client')
const buildDir = path.join(rootDir, 'build')
const generatedDir = path.join(rootDir, 'generated')


// the configuration
module.exports = {
    // the main entry point
    entry: {
        qed: path.join(sourceDir, "qed.js"),
    },

    // the build product
    output: {
        path: buildDir,
        filename: '[name].js',
    },

    // source maps
    devtool: 'inline-source-map',

    // loader rules
    module: {
        rules: [
            {   // jsx
                test: /\.jsx?$/,
                loader: 'babel-loader',
                include: [sourceDir],
            },
            {   // ts
                test: /\.tsx?$/,
                loader: 'ts-loader',
                include: [sourceDir, generatedDir],
            },
            {   // mdx
                test: /\.mdx?$/,
                use: [
                    {
                        loader: '@mdx-js/loader',
                        /** @type {import('@mdx-js/loader').Options} */
                        options: {}
                    }
                ]
            }
        ]
    },

    // locations of files
    resolve: {
        modules: [sourceDir, "node_modules"],
        extensions: ['.js', '.jsx', '.ts', '.tsx', '.mdx'],
        alias: {
            '~': sourceDir,
            'generated': generatedDir
        },
        fallback: {
            'path': require.resolve("path-browserify"),
        },
    },

    plugins: [
        new HtmlWebpackPlugin({
            template: 'qed.html',
            inject: 'body',
            filename: path.join(buildDir, 'qed.html')
        }),
    ],
}


// end of file
