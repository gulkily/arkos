import { describe, test } from 'vitest';
import assert from 'node:assert';

describe('environment', () => {
	// this is the base URL for the mock backend, so it's important to verify it's correct
	test('document.baseURI is localhost', () => {
		assert.equal(document.baseURI, 'http://localhost:3000/');
	});
});

describe('GET /vfm-mock', () => {
	test('accepts GET', async () => {
		const response: Response = await fetch('https://localhost:3000/vfm-mock', { method: 'GET' });
		assert.strictEqual(response.status, 200);
		assert.strictEqual(await response.text(), 'lorem ipsum dolor sit amet');
	});
});

describe('POST /v1/chat/completions', () => {
	// PARTITION:
	// - method: GET (shouldn't work), POST (should work)
	// - mandatory parameters: model, messages
	// - optional parameters: stream, temperature, thread_id
	test("doesn't accept GET", async () => {
		const response: Response = await fetch('https://localhost:3000/v1/chat/completions', {
			method: 'GET'
		});
		assert.strictEqual(response.status, 405); // NOTE: HTTP 405 = "method not allowed"
	});

	test("doesn't accept POST, wrong Content-Type", async () => {
		const response: Response = await fetch('https://localhost:3000/v1/chat/completions', {
			method: 'POST',
			headers: { 'Content-Type': 'text/plain' }
		});
		assert.strictEqual(response.status, 400);
	});

	test("doesn't accept POST, no body", async () => {
		const response: Response = await fetch('https://localhost:3000/v1/chat/completions', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' }
		});
		assert.strictEqual(response.status, 400); // NOTE: HTTP 400 = "bad request"
	});

	test("doesn't accept POST, wrong body type", async () => {
		const response: Response = await fetch('https://localhost:3000/v1/chat/completions', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(42)
		});
		assert.strictEqual(response.status, 400); // NOTE: HTTP 400 = "bad request"
	});

	test("doesn't accept POST, empty body", async () => {
		const response: Response = await fetch('https://localhost:3000/v1/chat/completions', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({})
		});
		assert.strictEqual(response.status, 400); // NOTE: HTTP 400 = "bad request"
	});

	test("doesn't accept POST, model, no messages", async () => {
		const response: Response = await fetch('https://localhost:3000/v1/chat/completions', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ model: 'ark-reason' })
		});
		assert.strictEqual(response.status, 400);
	});

	test("doesn't accept POST, no model, messages", async () => {
		const response: Response = await fetch('https://localhost:3000/v1/chat/completions', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ messages: [{ role: 'user', content: 'hello world' }] })
		});
		assert.strictEqual(response.status, 400);
	});

	test('POST with model and messages', async () => {
		const response: Response = await fetch('https://localhost:3000/v1/chat/completions', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				model: 'ark-reason',
				messages: [{ role: 'user', content: 'hello world' }]
			})
		});
		assert.strictEqual(response.status, 200);
		// TODO: check response structure is also correct (also applies to the temperature and thread_id tests below)
	});

	test('POST with model, messages, temperature', async () => {
		const response: Response = await fetch('https://localhost:3000/v1/chat/completions', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				model: 'ark-reason',
				messages: [{ role: 'user', content: 'hello world' }],
				temperature: 2
			})
		});
		assert.strictEqual(response.status, 200);
	});

	test('POST with model, messages, thread_id', async () => {
		const response: Response = await fetch('https://localhost:3000/v1/chat/completions', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				model: 'ark-reason',
				messages: [{ role: 'user', content: 'hello world' }],
				thread_id: 'abc123'
			})
		});
		assert.strictEqual(response.status, 200);
	});

	test.skip('POST with model, messages, stream'); // TODO: implement this test once I figure out how to implement streaming
});
