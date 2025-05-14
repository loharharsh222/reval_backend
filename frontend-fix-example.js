/**
 * Example of how to correctly send LLM responses to the API
 */

// INCORRECT WAY - This is what's happening now
async function sendResponsesIncorrect() {
  // This results in "[object Response]" or "[object Object]"
  const response = await fetch('/api/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: "Hi",
      responses: {
        ChatGPT: someResponseObject,  // This becomes '[object Response]' 
        Gemini: someObjectData,       // This becomes '[object Object]'
        Llama: anotherObject          // This becomes '[object Object]'
      }
    })
  });
}

// CORRECT WAY - How it should be fixed
async function sendResponsesCorrect() {
  // First extract the text content from each response
  const chatGptText = await someResponseObject.text(); // If it's a Response object
  // Or if it's an object with a text property
  const geminiText = someObjectData.text || JSON.stringify(someObjectData);
  const llamaText = anotherObject.text || JSON.stringify(anotherObject);

  // Now send the actual text content
  const response = await fetch('/api/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: "Hi",
      responses: {
        ChatGPT: chatGptText,  // Now a proper string like "Hello, how can I help you?"
        Gemini: geminiText,    // Now a proper string like "Hi there! What can I assist with?"
        Llama: llamaText       // Now a proper string like "Hello! I'm here to help."
      }
    })
  });
}
