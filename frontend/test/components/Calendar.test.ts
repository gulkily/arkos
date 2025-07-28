import { describe, test } from 'vitest';
import assert from 'node:assert';
import { render, screen } from '@testing-library/svelte';
import Calendar from '../src/components/Calendar.svelte';
import ResizeObserver from 'resize-observer-polyfill';

// c.f. https://stackoverflow.com/questions/64558062/how-to-mock-resizeobserver-to-work-in-unit-tests-using-react-testing-library
// (This could be removed if @event-calendar/core was mocked)
global.ResizeObserver = ResizeObserver;

describe('Calendar', () => {
	test('should only render one top-level tag', () => {
		const { container } = render(Calendar);
		assert.strictEqual(container.children.length, 1);
	});

	test('should render calendar-container div', () => {
		render(Calendar);
		const myCalendarContainer: HTMLElement = screen.getByTestId('calendar-container');
		assert.ok(myCalendarContainer);
		assert.strictEqual(myCalendarContainer.tagName, 'DIV');
	});

	// TODO: make this test *much* less flaky by mocking @event-calendar/core instead!
	test('should transclude @event-calendar/core', () => {
		render(Calendar);
		const myCalendar: HTMLElement = screen.getByRole('table');
		assert.ok(myCalendar);
		assert.strictEqual(myCalendar.tagName, 'DIV');
	});

	// TODO: implement these tests after figuring out how to mock the backend and/or @event-calendar/core
	test.skip('page load should result in GET /api/events call');

	test.skip('events from /api/events should appear on page');

	test.skip('creating event should result in POST /api/events call');

	test.skip('modifying event should result in PUT /api/events/{event-id} call');

	test.skip('deleting event should result in DELETE /api/events/{event-id} call');
});
