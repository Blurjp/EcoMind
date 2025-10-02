import { defineConfig } from 'vite';
import { resolve } from 'path';
import { copyFileSync, mkdirSync, existsSync } from 'fs';

export default defineConfig({
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        'bg/service-worker': resolve(__dirname, 'src/bg/service-worker.ts'),
        'ui/popup': resolve(__dirname, 'src/ui/popup.ts'),
        'ui/options': resolve(__dirname, 'src/ui/options.ts'),
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]',
      },
    },
    target: 'ES2020',
    minify: false,
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  plugins: [
    {
      name: 'copy-html-and-icons',
      writeBundle() {
        const distDir = resolve(__dirname, 'dist');
        const uiDir = resolve(distDir, 'ui');
        const iconsDir = resolve(distDir, 'icons');

        if (!existsSync(uiDir)) mkdirSync(uiDir, { recursive: true });
        if (!existsSync(iconsDir)) mkdirSync(iconsDir, { recursive: true });

        copyFileSync(
          resolve(__dirname, 'src/ui/popup.html'),
          resolve(uiDir, 'popup.html')
        );
        copyFileSync(
          resolve(__dirname, 'src/ui/options.html'),
          resolve(uiDir, 'options.html')
        );
        copyFileSync(
          resolve(__dirname, 'src/ui/popup.css'),
          resolve(uiDir, 'popup.css')
        );
        copyFileSync(
          resolve(__dirname, 'src/ui/options.css'),
          resolve(uiDir, 'options.css')
        );

        try {
          copyFileSync(
            resolve(__dirname, 'src/icons/icon16.png'),
            resolve(iconsDir, 'icon16.png')
          );
          copyFileSync(
            resolve(__dirname, 'src/icons/icon48.png'),
            resolve(iconsDir, 'icon48.png')
          );
          copyFileSync(
            resolve(__dirname, 'src/icons/icon128.png'),
            resolve(iconsDir, 'icon128.png')
          );
        } catch (err) {
          console.log('Icons not found, will need to be added manually');
        }
      },
    },
  ],
});