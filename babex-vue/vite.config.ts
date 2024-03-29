import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import {exec} from 'child_process'

// https://vitejs.dev/config/
export default defineConfig({
    base: '/static/',
    build: {
        outDir: 'dist',
        manifest: true,
        rollupOptions: {
            input: 'src/main.ts'
        }
    },
    plugins: [
        vue(),

        // a custom plugin that copies the built app into the static folder of both
        // the lab and parent apps
        {
            name: 'duplicate-output',
            closeBundle: async () => {
                exec("bash -c 'rm -rf ../lab/main/static/vue; rm -rf ../parent/parent/static/vue'",
                     (error, stdout, stderr) => {
                         console.log(stdout);
                         console.log(stderr);
                         if (error) console.log('error:', error);
                     });
                console.log('copying assets');
                exec("bash -c 'cp -vR dist ../lab/main/static/vue && cp -vR dist ../parent/parent/static/vue'",
                     (error, stdout, stderr) => {
                         console.log(stdout);
                         console.log(stderr);
                         if (error) console.log('error:', error);
                     });
            }
        }
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    }
})
