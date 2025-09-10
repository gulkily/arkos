import { describe, test } from 'vitest';
import assert from 'node:assert';
import { render, screen } from '@testing-library/svelte';
import Page from '../../src/routes/chat/+page.svelte';

describe('chat route', () => {
	test('renders navbar', () => {
		render(Page);
		assert.ok(screen.getByTestId('navbar'));
	});

	test('renders chat view', () => {
		render(Page);
		assert.ok(screen.getByTestId('chat-container'));
	});
});
