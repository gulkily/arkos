// NOTE: replace `localhost:3000` by actual domain name once we get one
import assert from 'node:assert';

/**
 * Handles *only* requests to POST /v1/chat/completions
 * @param req the HTTP request to handle
 * @returns the HTTP response to send
 */
async function handleChatCompletions(req: Request): Promise<Response> {
	assert.strictEqual(req.url, 'https://localhost:3000/v1/chat/completions');
	// check HTTP method
	if (req.method !== 'POST') {
		return new Response('wrong HTTP method!', { status: 405 });
	}
	// check Content-Type
	if (req.headers.get('Content-Type') !== 'application/json') {
		return new Response('wrong Content-Type', { status: 400 });
	}
	// try to parse JSON
	let reqJSON: unknown;
	try {
		reqJSON = await req.json();
	} catch {
		return new Response('no or malformed body', { status: 400 });
	}
	// input validation for `reqJSON`
	// TODO: try using a library for this instead?
	if (!(reqJSON instanceof Object)) {
		return new Response('wrong body type', { status: 400 });
	}

	// TODO: more input validation
	return new Response('TODO', { status: 501 }); // NOTE: HTTP 501 = "not implemented"
}

/**
 * Handles all HTTP requests to the mock backend
 * @param req the HTTP request to handle
 * @returns the HTTP response to send
 */
async function handleMockBackendRequest(req: Request): Promise<Response> {
	if (req.url === 'https://localhost:3000/vfm-mock') {
		return new Response('lorem ipsum dolor sit amet', { status: 200 });
	} else if (req.url === 'https://localhost:3000/v1/chat/completions') {
		return await handleChatCompletions(req);
	} else {
		return new Response('not found', { status: 404 });
	}
}

export default handleMockBackendRequest;
