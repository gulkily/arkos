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
const fetchMocker: FetchMock = createFetchMock(vi);

// a silly route for sanity-checking
// TODO: replace `localhost:3000` by actual domain name once we get one
fetchMocker.doMockIf('https://localhost:3000/vfm-mock', 'lorem ipsum dolor sit amet'); // no need to check HTTP method for now
// TODO: mock POST /v1/chat/completions

// enable mocking
fetchMocker.enableMocks();
