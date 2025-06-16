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
// TODO: replace `example.com` by actual domain name once we get one
fetchMocker.doMockIf('https://example.com/vfm-mock', (req: Request) => {
	return req.method == 'GET'
		? 'lorem ipsum dolor sit amet'
		: Promise.reject(new Error('wrong HTTP method'));
});
// TODO: mock POST /v1/chat/completions

// enable mocking
fetchMocker.enableMocks();
