# LLM Response Evaluator - Troubleshooting Guide

## Common Issues & Solutions

### Issue: Same scores for different LLM models

#### Problem Diagnosis
If you're getting identical evaluation scores for different LLM responses, this could be due to:

1. **Invalid response formats**:
   - Frontend sending `[object Object]` or `[object Response]` instead of actual text
   - The evaluator receives and processes identical string representations

2. **Limitations in metric differentiation**:
   - The coherence score only analyzed sentence structure (not content)
   - Token overlap calculation without stemming missed word variations

#### How We Fixed It

1. **Added frontend data validation**:
   - API now detects and rejects `[object Object]` and `[object Response]` inputs
   - Added automatic JSON response extraction (extracts the 'text' field from JSON responses)
   - Added helpful error messages explaining how to fix the issue

2. **Improved NLP metrics**:
   - Added stemming for better token matching
   - Enhanced coherence calculation to consider question context
   - Added Jaccard similarity for content relevance

3. **More debug information**:
   - Added detailed logging with unique evaluation IDs
   - Added warnings for identical model responses

### Best Practices for Frontend Integration

1. **Always extract text content** before sending to evaluation API:
   ```javascript
   // Incorrect
   const responses = {
     ChatGPT: responseObject,  // This becomes [object Response]
     Gemini: modelObject       // This becomes [object Object]
   };
   
   // Correct
   const responses = {
     ChatGPT: await responseObject.text(),
     Gemini: modelObject.text || modelObject.content
   };
   ```

2. **Validate responses** before sending:
   ```javascript
   function isValidResponse(text) {
     return (
       typeof text === 'string' &&
       text.length > 0 &&
       !text.includes('[object ')
     );
   }
   ```

3. **Handle errors** gracefully:
   ```javascript
   try {
     const result = await fetch('/api/evaluate', {...});
     const data = await result.json();
     
     if (data.error) {
       console.error(`Evaluation failed: ${data.error}`);
       // Show user-friendly message
     }
   } catch (err) {
     console.error('API error:', err);
   }
   ```

## Understanding the Evaluation Metrics

### Special Handling for Short Prompts
- Short prompts (like "Hi", "Hello") now have specialized evaluation logic
- Greeting responses to greeting prompts receive boosted scores
- Brief, concise responses are appropriately rewarded for short prompts
- Prevents unfair penalization of naturally short responses to simple prompts

### Coherence Score (40% of overall)
- How well-structured the text is
- Now also considers question relevance
- Component metrics:
  - Short sentence penalty
  - Sentence length variation
  - Sentence count optimality
  - Content relevance (Jaccard similarity with question)

### Token Overlap (40% of overall)
- How well the response addresses the question
- Uses stemming to recognize word variations
- Measures shared tokens between question and response

### Length Ratio (20% of overall)
- Is the response appropriately sized?
- Penalizes too short or too long responses
- Optimal when length is proportional to question

## Testing Your Integration

Use our debug script to validate your integration:

```
python debug_evaluation.py
```

This will test both direct NLP evaluations and the service layer with sample responses.
