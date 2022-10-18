const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
    transpileDependencies: true,
    outputDir: '../main/static/vue',
    publicPath: 'http://localhost:8081/',

    devServer: {
        headers: {
            "Access-Control-Allow-Origin": "*"
        },
    },
})
