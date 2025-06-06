import { describe, test } from 'vitest';
import assert from 'node:assert';
import { render, screen } from '@testing-library/svelte';
import Chat from '../src/components/chat.svelte';

describe('Chat', () => {
	test('should render chat-container div', () => {
		render(Chat);
		const chatcontainer: HTMLElement = screen.getByTestId('chat-container');
		assert.ok(chatcontainer);
		assert.strictEqual(chatcontainer.tagName, 'DIV');
	});

	test('should render chat-messages div', () => {
		render(Chat);
		const chatmessages: HTMLElement = screen.getByTestId('chat-messages');
		assert.ok(chatmessages);
		assert.strictEqual(chatmessages.tagName, 'DIV');
	});

	test.skip('should render default message', () => {
		render(Chat);

		/* NOTE: we might change the default message text or the message HTML markup later on */
		const defaultMessage: string = "Hello! I'm your calendar assistant. How can I help you today?";
		const defaultMessageDiv: HTMLElement = screen.getByText(defaultMessage);
		assert.ok(defaultMessageDiv);
		assert.strictEqual(defaultMessageDiv.tagName, 'DIV');
	});

	test.skip('should render chat-input-container', () => {
		render(Chat);
		const chatcontainer: HTMLElement = screen.getByTestId('chat-input-container');
		assert.ok(chatcontainer);
		assert.strictEqual(chatcontainer.tagName, 'DIV');
	});

	test.skip('should render chat-input field', () => {
		render(Chat);
		assert.ok(screen.getByRole('input'));
	});

	test.skip('should render send button', () => {
		render(Chat);
		assert.ok(screen.getByRole('button'));
	});

	/* TODO: write these tests after I figure out how to mock the backend */
	test.skip('loading should result in GET /api/chat/suggestions call');

	test.skip('sending message should result in POST /api/chat/messages call');

	test.skip('sending message should result in new message appearing on screen');

	test.skip('sending message should result in reply message appearing on screen');

	test.skip('sending message should clear original input field');

	test.skip('enter key should result in sending message');

	test.skip('should support sending multiple rounds of messages');
});
