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

	const requestKeys: Set<string> = new Set(Object.keys(reqJSON));
	console.log(`requestKeys = ${[...requestKeys]}`);
	const requiredKeys: Array<string> = ['model', 'messages'];
	const allSupportedKeys: Set<string> = new Set([
		'model',
		'messages',
		'stream',
		'temperature',
		'thread_id'
	]);
	// c.f. https://www.30secondsofcode.org/js/s/superset-subset-of-array/
	if (!requiredKeys.every((v) => requestKeys.has(v))) {
		return new Response('missing required keys', { status: 400 });
	}
	if (![...requestKeys].every((v) => allSupportedKeys.has(v))) {
		return new Response('unknown keys', { status: 400 });
	}

	if (requestKeys.has('stream')) {
		// TODO: implement streaming later
		return new Response('no streaming yet', { status: 501 });
	}

	return new Response(
		JSON.stringify({
			id: 'abcdefghijklmnopqrstuvwxyz', // randomize?
			object: 'chat.completion',
			created: ~~(Date.now() / 1000), // round so schema's correct; c.f. https://stackoverflow.com/questions/4228356/how-to-perform-an-integer-division-and-separately-get-the-remainder-in-javascr
			model: 'example',
			choices: [
				{
					index: 0,
					message: {
						role: 'assistant',
						content: 'lorem ipsum' // randomize?
					},
					finish_reason: null
				}
			]
		}),
		{ status: 200 }
	);
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
