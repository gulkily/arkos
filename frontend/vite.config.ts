import { svelteTesting } from '@testing-library/svelte/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
// NOTE: this line is necessary to keep vite.config.ts happy
import { type ViteUserConfig } from 'vitest/config';

export default defineConfig({
	plugins: [sveltekit()],
	// c.f. https://stackoverflow.com/questions/74902697/error-the-request-url-is-outside-of-vite-serving-allow-list-after-git-init
	server: {
		fs: {
			allow: ['static/']
		}
	},
	test: {
		workspace: [
			{
				extends: './vite.config.ts',
				plugins: [svelteTesting()],
				test: {
					name: 'client',
					environment: 'jsdom',
					clearMocks: true,
					include: ['test/**/*.test.{js,ts}'], // NOTE: all test files should be migrated into the `test` folder
					setupFiles: ['./vitest-setup-client.ts']
				}
			}
		]
	}
});
