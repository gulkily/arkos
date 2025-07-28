import { describe, test } from 'vitest';
import assert from 'node:assert';
import { render, screen } from '@testing-library/svelte';
import Page from '../src/routes/dashboard/+page.svelte';
import ResizeObserver from 'resize-observer-polyfill';

// c.f. https://stackoverflow.com/questions/64558062/how-to-mock-resizeobserver-to-work-in-unit-tests-using-react-testing-library
global.ResizeObserver = ResizeObserver;

describe('/+page.svelte', () => {
	test('should render app-container div', () => {
		render(Page);
		const appContainer: HTMLElement = screen.getByTestId('app-container');
		assert.ok(appContainer);
		assert.strictEqual(appContainer.tagName, 'DIV');
	});

	test('should render calendar-container div', () => {
		render(Page);
		const calendarContainer: HTMLElement = screen.getByTestId('calendar-container');
		assert.ok(calendarContainer);
		assert.strictEqual(calendarContainer.tagName, 'DIV');
	});

	test('should render chat-container div', () => {
		render(Page);
		const chatContainer: HTMLElement = screen.getByTestId('chat-container');
		assert.ok(chatContainer);
		assert.strictEqual(chatContainer.tagName, 'DIV');
	});
});
