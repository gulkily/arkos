/* type declarations for the API contract; add more as needed */
type ChatMessage = { role: string; content: string };
type ChatChoice = {
	index: number;
	message: ChatMessage;
	finish_reason?: string;
};
type ChatCompletionRequest = {
	model: string;
	messages: Array<ChatMessage>;
	stream?: boolean;
	temperature?: number;
	thread_id?: string;
};
type ChatCompletionResponse = {
	id: string;
	object: string;
	created: number;
	model: string;
	choices: Array<ChatChoice>;
};
