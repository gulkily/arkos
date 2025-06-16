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
	test.skip("doesn't accept GET");

	test.skip("doesn't accept POST, no model, no messages");

	test.skip("doesn't accept POST, model, no messages");

	test.skip("doesn't accept POST, no model, messages");

	test.skip('POST with model and messages');

	test.skip('POST with model, messages, stream');

	test.skip('POST with model, messages, temperature');

	test.skip('POST with model, messages, thread_id');
});
