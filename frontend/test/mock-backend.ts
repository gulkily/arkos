// NOTE: replace `localhost:3000` by actual domain name once we get one

/**
 * Handles all HTTP requests to the mock backend
 * @param req the HTTP request to handle
 * @returns the HTTP response to send
 */
function handleMockBackendRequest(req: Request): Response {
	if (req.url === 'https://localhost:3000/vfm-mock') {
		return new Response('lorem ipsum dolor sit amet', { status: 200 });
	} else if (req.url === 'https://localhost:3000/v1/chat/completions') {
		if (req.method !== 'POST') {
			return new Response('wrong HTTP method!', { status: 405 });
		}
		// TODO: input validation
		return new Response('TODO', { status: 501 }); // NOTE: HTTP 501 = "not implemented"
	} else {
		return new Response('not found', { status: 404 });
	}
}

export default handleMockBackendRequest;
