<script lang="ts">
	/* TODO: add a script here */
</script>

<div class="chat-container" data-testid="chat-container">
	<div class="chat-messages" data-testid="chat-messages">
		<!-- NOTE: for testing purposes, messages are numbered in `data-testid` using zero-indexing -->
		<div class="message system" data-testid="message0">
			<p>Hello! I'm your calendar assistant. How can I help you today?</p>
		</div>
	</div>
	<div class="chat-input-container" data-testid="chat-input-container">
		<input type="text" class="chat-input" id="chatInput" placeholder="Type a message..." />
		<!-- TODO: attach an event listener to this button to call the backend -->
		<button class="send-button" id="sendButton">Send</button>
	</div>
</div>
