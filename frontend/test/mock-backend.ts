// NOTE: replace `localhost:3000` by actual domain name once we get one
import assert from 'node:assert';
import { Validator, ValidatorResult } from 'jsonschema';
import request_schema from '../../schemas/chatcompletionrequest_schema.json';

const v: Validator = new Validator();

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
	const validationResults: ValidatorResult = v.validate(reqJSON, request_schema);
	if (!validationResults.valid) {
		return new Response(`malformed request: ${validationResults.errors}`, { status: 400 });
	}

	assert(reqJSON instanceof Object);
	if (reqJSON['stream'] === true) {
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
