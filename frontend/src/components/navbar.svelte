<!-- c.f. https://www.w3schools.com/howto/howto_css_dropdown_navbar.asp -->
<!-- This is static for now, so it doesn't need to be tested -->
<nav class="navbar">
	<!-- NOTE: this CSS class is necessary, otherwise it conflicts with the navbar in the calendar view -->
	<!-- svelte-ignore a11y_invalid_attribute-->
	<a href="/">Home</a>
	<!-- TODO: replace these links -->
	<a href="https://example.com">About</a>
	<div class="dropdown">
		<button class="dropbtn">Features </button>
		<div class="dropdown-content">
			<a href="https://example.com">Link 1</a>
			<a href="https://example.com">Link 2</a>
			<a href="https://example.com">Link 3</a>
		</div>
	</div>
	<a href="https://github.com/SGIARK/ARK2.0">Source code</a>
</nav>
