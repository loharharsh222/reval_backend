/**
 * Example of how to correctly send LLM responses to the API
 * Updated with support for JSON response formatting
 */

// INCORRECT WAY - This is what causes the frontend data transmission issues
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

/**
 * Helper function to extract text content from various response formats
 */
function extractTextContent(response) {
  // Handle null/undefined
  if (!response) {
    return '';
  }
  
  // Check if response is already a string
  if (typeof response === 'string') {
    // Try to parse JSON strings (some LLMs return JSON-stringified responses)
    if (response.startsWith('{') && response.endsWith('}')) {
      try {
        const parsed = JSON.parse(response);
        // Most LLMs use a 'text' field for the main content
        if (parsed && typeof parsed.text === 'string') {
          return parsed.text;
        }
        // Check other common fields
        if (parsed && typeof parsed.content === 'string') {
          return parsed.content;
        }
        if (parsed && typeof parsed.message === 'string') {
          return parsed.message;
        }
      } catch (e) {
        // If parsing fails, return the original string
        console.warn('Failed to parse JSON response', e);
      }
    }
    return response;
  }
  
  // Handle objects (common with fetch API responses)
  if (typeof response === 'object') {
    // Check common fields where text content might be stored
    if (response.text && typeof response.text === 'string') {
      return response.text;
    }
    if (response.content && typeof response.content === 'string') {
      return response.content;
    }
    // Handle nested content (common in OpenAI and other APIs)
    if (response.choices && Array.isArray(response.choices) && response.choices.length > 0) {
      const firstChoice = response.choices[0];
      if (firstChoice.text) {
        return firstChoice.text;
      }
      if (firstChoice.message && firstChoice.message.content) {
        return firstChoice.message.content;
      }
    }
    
    // Last resort - stringify the object (not recommended)
    console.warn('Could not extract text content from object', response);
    try {
      return JSON.stringify(response);
    } catch (e) {
      return '';
    }
  }
    // For other types, convert to string
  return String(response);
}

/**
 * CORRECT WAY - Process responses before sending to API
 */
async function sendResponsesCorrect() {
  // Raw responses from different LLM APIs
  const rawResponses = {
    // String response (simple)
    ChatGPT: "The capital of France is Paris.",
    
    // JSON string response (needs parsing)
    Gemini: '{"text": "Paris is the capital of France.", "confidence": 0.95}',
    
    // Object response (like OpenAI API)
    Claude: {
      "id": "chatcmpl-123",
      "choices": [{
        "message": {
          "content": "The capital of France is Paris."
        }
      }]
    }
  };

  // Process all responses to extract text content
  const processedResponses = {};
  Object.keys(rawResponses).forEach(modelName => {
    processedResponses[modelName] = extractTextContent(rawResponses[modelName]);
  });
  
  // Send to API - now all responses are properly formatted text
  const response = await fetch('/api/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: "What is the capital of France?",
      responses: processedResponses
    })
  });
  
  // Result should now have different scores for each model
  const result = await response.json();
  console.log('Evaluation results:', result);
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
