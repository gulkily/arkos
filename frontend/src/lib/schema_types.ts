/* type declarations for the API contract; add more as needed */
export type ChatMessage = { role: string; content: string };
export type ChatChoice = {
	index: number;
	message: ChatMessage;
	finish_reason?: string;
};
export type ChatCompletionRequest = {
	model: string;
	messages: Array<ChatMessage>;
	stream?: boolean;
	temperature?: number;
	thread_id?: string;
};
export type ChatCompletionResponse = {
	id: string;
	object: string;
	created: number;
	model: string;
	choices: Array<ChatChoice>;
};
