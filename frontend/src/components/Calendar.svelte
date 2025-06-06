<script lang="ts">
	import { Calendar, TimeGrid, DayGrid, Interaction } from '@event-calendar/core';

	const plugins: Array<object> = [TimeGrid, DayGrid, Interaction];

	// TODO: customize the options as needed
	// TODO: can we type the `options` variable with something more precise?
	let options: object = $state({
		view: 'dayGridMonth',
		events: []
	});

	// TODO: connect to backend and allow creating, modifying, or deleting events to be reflected there
</script>

<div class="calendar-container" data-testid="calendar-container">
	<!-- TODO: mock the Calendar component itself during testing -->
	<Calendar {plugins} {options} />
</div>
