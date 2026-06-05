const path = require('path');

const whichFile = "component";

module.exports = {
    mode: 'production',
    entry: {
        app : {
            "component" : './script/component.js',
            "pink-trombone" : './script/audio/nodes/pinkTrombone/processors/WorkletProcessor.js',
        }[whichFile]
        
        // app: './script/component.js'
        // app: './script/audio/nodes/pinkTrombone/processors/WorkletProcessor.js'
    },
    output: {
        path: path.resolve(__dirname, 'build'),
        globalObject: 'globalThis',
        filename : {
            "component" : 'pink-trombone.min.js',
            "pink-trombone" : 'pink-trombone-worklet-processor.min.js',
        }[whichFile]

        // filename: 'pink-trombone.min.js'
        // filename: 'pink-trombone-worklet-processor.min.js'

    },
    module: {
        rules: [{
            test: /\.js?$/,
            exclude: /node_modules/,
            loader: 'babel-loader',
            options: {
                presets: ['@babel/preset-env']
            }
        }]
    }
}