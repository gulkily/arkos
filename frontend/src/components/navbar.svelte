<!-- c.f. https://www.w3schools.com/howto/howto_css_dropdown_navbar.asp -->
<!-- This is static for now, so it doesn't need to be tested -->
<nav class="navbar">
	<!-- NOTE: this CSS class is necessary, otherwise it conflicts with the navbar in the calendar view -->
	<a href="/">Home</a>
	<a href="/about">About</a>
	<div class="dropdown">
		<button class="dropbtn">Features </button>
		<div class="dropdown-content">
			<a href="/dashboard">Dashboard</a>
			<a href="/chat">AI chat</a>
			<a href="/calendar">Calendar</a>
		</div>
	</div>
	<a href="https://github.com/SGIARK/ARK2.0">Source code</a>
</nav>
