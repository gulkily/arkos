import { describe, test } from 'vitest';
import assert from 'node:assert';
import { render, screen } from '@testing-library/svelte';
import Page from '../../src/routes/calendar/+page.svelte';
import ResizeObserver from 'resize-observer-polyfill';

// c.f. https://stackoverflow.com/questions/64558062/how-to-mock-resizeobserver-to-work-in-unit-tests-using-react-testing-library
global.ResizeObserver = ResizeObserver;

describe('chat route', () => {
	test('renders navbar', () => {
		render(Page);
		assert.ok(screen.getByTestId('navbar'));
	});

	test('renders calendar view', () => {
		render(Page);
		assert.ok(screen.getByTestId('calendar-container'));
	});
});
