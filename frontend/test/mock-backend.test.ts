import { describe, test } from 'vitest';
/*import assert from 'node:assert';*/

describe('GET /vfm-mock', () => {
	test.skip('accepts GET');

	test.skip("doesn't accept POST");
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
