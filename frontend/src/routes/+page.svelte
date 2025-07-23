<!-- NOTE: do NOT transclude the stylesheet here! This WILL break the test cases! -->

<script lang="ts">
	import Calendar from '../components/Calendar.svelte';
	import Chat from '../components/chat.svelte';
	import Navbar from '../components/navbar.svelte';
</script>

<Navbar />
<div class="app-container" data-testid="app-container">
	<Calendar />
	<Chat />
</div>
