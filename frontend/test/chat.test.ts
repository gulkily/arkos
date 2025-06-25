import { describe, expect, test, vi } from 'vitest';
import assert from 'node:assert';
import { render, screen } from '@testing-library/svelte';
import Chat from '../src/components/chat.svelte';
import { handleChatCompletions } from './mock-backend.ts';
import { userEvent, UserEvent } from '@testing-library/user-event';

vi.mock('./mock-backend.ts', { spy: true }); // c.f. https://vitest.dev/api/vi.html#vi-mock

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

	/* TODO: write these tests after I figure out how @testing-library/user-event works */
	test('sending message should result in POST /v1/chat/completions call', async () => {
		render(Chat);
		const user: UserEvent = userEvent.setup();
		// type a placeholder message and click the button
		await user.type(screen.getByRole('textbox'), 'lorem ipsum'); // randomize?
		await user.click(screen.getByRole('button'));
		// expect handleChatCompletions to have been called
		expect(handleChatCompletions).toHaveBeenCalled();
	});

	test('sending message should result in new message appearing on screen', async () => {
		render(Chat);
		const user: UserEvent = userEvent.setup();
		await user.type(screen.getByRole('textbox'), 'lorem ipsum'); // randomize? )a;sp 
		await user.click(screen.getByRole('button'));
		// look for the new message
		const newMessage: HTMLElement = screen.getByTestId('message1');
		assert.strictEqual(newMessage.tagName, 'DIV');
	});

	test('sending message should result in reply message appearing on screen', async () => {
		render(Chat);
		const user: UserEvent = userEvent.setup();
		await user.type(screen.getByRole('textbox'), 'lorem ipsum');
		await user.click(screen.getByRole('button'));
		// await the reply message (don't look for it immediately, because it could take time)
		const newMessage: HTMLElement = await screen.findByTestId('message2');
		assert.strictEqual(newMessage.tagName, 'DIV');
	});

	test('sending message should clear original input field', async () => {
		render(Chat);
		const user: UserEvent = userEvent.setup();
		const myTextBox: HTMLElement = screen.getByRole('textbox');
		assert(myTextBox instanceof HTMLInputElement);
		await user.type(myTextBox, 'lorem ipsum');
		await user.click(screen.getByRole('button'));
		assert.strictEqual(myTextBox.value, '');
	});

	/* NOTE: these tests are somewhat redundant since the enter key and submit button shuold share the same handler, but I'm doing them anyways */
	test('enter key should result in POST /v1/chat/completions request', async () => {
		render(Chat);
		const user: UserEvent = userEvent.setup();
		await user.type(screen.getByRole('textbox'), 'lorem ipsum\n');
		expect(handleChatCompletions).toHaveBeenCalled();
	});

	test('enter key should result in new message appearing on screen', async () => {
		render(Chat);
		const user: UserEvent = userEvent.setup();
		await user.type(screen.getByRole('textbox'), 'lorem ipsum\n');
		expect(handleChatCompletions).toHaveBeenCalled();
		const newMessage: HTMLElement = screen.getByTestId('message1');
		assert.strictEqual(newMessage.tagName, 'DIV');
	});

	test('enter key should result in reply message appearing on screen', async () => {
		render(Chat);
		const user: UserEvent = userEvent.setup();
		await user.type(screen.getByRole('textbox'), 'lorem ipsum\n');
		expect(handleChatCompletions).toHaveBeenCalled();
		const newMessage: HTMLElement = await screen.findByTestId('message1');
		assert.strictEqual(newMessage.tagName, 'DIV');
	});

	test('sending message should clear original input field', async () => {
		render(Chat);
		const user: UserEvent = userEvent.setup();
		const myTextBox: HTMLElement = screen.getByRole('textbox');
		assert(myTextBox instanceof HTMLInputElement);
		await user.type(myTextBox, 'lorem ipsum\n');
		assert.strictEqual(myTextBox.value, '');
	});

	test('should support sending multiple rounds of messages', async () => {
		render(Chat);
		const user: UserEvent = userEvent.setup();
		const myTextBox: HTMLElement = screen.getByRole('textbox');
		assert(myTextBox instanceof HTMLInputElement);
		const testMessages: Array<string> = ['lorem', 'ipsum', 'dolor']; // randomize?
		for (const [i, message] of testMessages.entries()) {
			await user.type(myTextBox, `${message}\n`);
			// look for the message and its reply
			screen.getByTestId(`message${2*i + 1}`);
			screen.getByTestId(`message${2*i + 2}`);
		}
	});
});
