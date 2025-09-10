<!-- TODO: test after replacing static content -->
<script lang="ts">
	import Navbar from '../../components/navbar.svelte';
</script>

<Navbar />
<div class="app-container" data-testid="app-container">
	<section>
		<h1>ARK 2.0</h1>
	</section>

	<section>
		<h2>Happy night, [username]!</h2>
		<!-- TODO: replace with dynamic content -->
		<time>[date]</time>
		<address>[city]</address>
	</section>

	<section>
		<h2 id="events">🗓️ Events</h2>
		<ul>
			<li>[event 1]</li>
			<li>[event 2]</li>
		</ul>
		<p><small>(View all!)</small></p>
	</section>

	<section>
		<h2 id="chats">💬 Chats</h2>
		<ul>
			<li>[Chat 1]</li>
			<li>[Chat 2]</li>
		</ul>
		<p><small>(View all!)</small></p>
	</section>
</div>
