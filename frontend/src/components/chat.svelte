<script lang="ts">
	// c.f. https://lightningchart.com/js-charts/api-documentation/v5.2.0/types/MouseEventHandler.html for typing
	async function handleMessageSending(event: MouseEvent): Promise<void> {
		/* TODO: replace this with a real event listener */
		console.log(`hello from ${event.toString()}, it's ${Date.now()}`);
		const response: Response = await fetch('https://localhost:3000/v1/chat/completions', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				model: 'ark-reason',
				messages: [] // TODO: add real messages
			})
		});
		const responseJSON: any = await response.json();
		console.log(`response status was ${response.status} and responseJSON was ${String(responseJSON)}`);
	}
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
		<button class="send-button" id="sendButton" onclick={handleMessageSending}>Send</button>
	</div>
</div>
