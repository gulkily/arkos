import '@testing-library/jest-dom/vitest';
import { vi } from 'vitest';
import createFetchMock from 'vitest-fetch-mock';
import { FetchMock } from 'vitest-fetch-mock';

// required for svelte5 + jsdom as jsdom does not support matchMedia
Object.defineProperty(window, 'matchMedia', {
	writable: true,
	enumerable: true,
	value: vi.fn().mockImplementation((query) => ({
		matches: false,
		media: query,
		onchange: null,
		addEventListener: vi.fn(),
		removeEventListener: vi.fn(),
		dispatchEvent: vi.fn()
	}))
});

// use vitest-fetch-mock
// TODO: add mock routes
const fetchMocker: FetchMock = createFetchMock(vi);
fetchMocker.enableMocks();
