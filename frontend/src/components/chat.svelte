<script lang="ts">
	import { Ajv, type ValidateFunction } from 'ajv';
	import { type ChatMessage, type ChatCompletionResponse } from '../lib/schema_types.js';
	import response_schema from '../../../schemas/chatcompletionresponse_schema.json';
	import message_schema from '../../../schemas/chatmessage_schema.json';

	const ajv: Ajv = new Ajv();
	const response_validator: ValidateFunction<ChatCompletionResponse> = ajv
		.addSchema(message_schema)
		.compile<ChatCompletionResponse>(response_schema);

	let currentMessages: Array<ChatMessage> = $state([
		{
			role: 'assistant',
			content: "Hello! I'm your calendar assistant. How can I help you today?"
		}
	]);
	let currentUserMessage: string = $state('');

	// c.f. https://lightningchart.com/js-charts/api-documentation/v5.2.0/types/MouseEventHandler.html for typing
	async function handleMessageSending(event: MouseEvent): Promise<void> {
		console.log(`hello from ${event.toString()}, it's ${Date.now()}`);
		currentMessages = [...currentMessages, { role: 'user', content: currentUserMessage }]; // reassign for better reactivity
		const response: Response = await fetch('https://localhost:3000/v1/chat/completions', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				model: 'ark-reason',
				messages: currentMessages
			})
		});
		const responseJSON: unknown = await response.json();
		console.log(
			`response status was ${response.status} and responseJSON was ${String(responseJSON)}`
		);
		// TODO: append new input to currentMessages after validation

		// reset the input
		currentUserMessage = '';
	}
</script>

<div class="chat-container" data-testid="chat-container">
	<div class="chat-messages" data-testid="chat-messages">
		<!-- NOTE: for testing purposes, messages are numbered in `data-testid` using zero-indexing -->
		{#each currentMessages.entries() as [index, message] (index)}
			<div class={`message ${message.role}`} data-testid={`message${index}`}>
				<p>{message.content}</p>
			</div>
		{/each}
	</div>
	<div class="chat-input-container" data-testid="chat-input-container">
		<input
			type="text"
			class="chat-input"
			id="chatInput"
			placeholder="Type a message..."
			bind:value={currentUserMessage}
		/>
		<!-- c.f. https://svelte.dev/tutorial/svelte/text-inputs -->
		<button class="send-button" id="sendButton" onclick={handleMessageSending}>Send</button>
	</div>
</div>
