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
// NOTE: replace `localhost:3000` by actual domain name once we get one
fetchMocker.mockResponse((req: Request) => {
	// TODO: move this code into its own file
	if (req.url === 'https://localhost:3000/vfm-mock') {
		return new Response('lorem ipsum dolor sit amet', { status: 200 });
	} else if (req.url === 'https://localhost:3000/v1/chat/completions') {
		if (req.method !== 'POST') {
			return new Response('wrong HTTP method!', { status: 405 });
		}
		// TODO: input validation
		return new Response('TODO', { status: 501 }); // NOTE: HTTP 501 = "not implemented"
	} else {
		return new Response('not found', { status: 404 });
	}
});
// TODO: mock POST /v1/chat/completions

// enable mocking
fetchMocker.enableMocks();
