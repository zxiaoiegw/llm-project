# Import necessary libraries
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'zxiao-llm-project-2025')
LOCATION = 'us-central1'

# Initialize Gemini 2.0 Flash
VERTEX_AI_READY = False
model = None

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    
    # Initialize Vertex AI
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    # Load Gemini 2.0 Flash
    model = GenerativeModel("gemini-2.0-flash-001")
    VERTEX_AI_READY = True
    logger.info("✅ Vertex AI Gemini 2.0 Flash initialized successfully")
    
except Exception as e:
    logger.error(f"❌ Vertex AI Gemini 2.0 Flash initialization failed: {str(e)}")
    VERTEX_AI_READY = False

# HTML template for the web app
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vertex AI Gemini 2.0 Summarization</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            font-weight: 300;
        }
        .service-header {
            background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
            color: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
            text-align: center;
        }
        .service-header h2 {
            margin: 0 0 10px 0;
            font-size: 1.5em;
            font-weight: 400;
        }
        .service-header p {
            margin: 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .status-indicator {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 600;
        }
        .status-ready {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .input-section {
            margin-bottom: 30px;
        }
        label {
            display: block;
            margin-bottom: 12px;
            font-weight: 600;
            color: #333;
            font-size: 1.1em;
        }
        textarea {
            width: 100%;
            height: 300px;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            box-sizing: border-box;
            transition: border-color 0.3s ease;
        }
        textarea:focus {
            outline: none;
            border-color: #4285f4;
            box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.1);
        }
        .button-container {
            text-align: center;
            margin: 30px 0;
        }
        .summarize-btn {
            background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 18px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
        }
        .summarize-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(66, 133, 244, 0.4);
        }
        .summarize-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .result-section {
            margin-top: 30px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 15px;
            border-left: 5px solid #4285f4;
            display: none;
        }
        .result-section.show {
            display: block;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .summary-text {
            font-size: 1.1em;
            line-height: 1.6;
            color: #333;
            margin-bottom: 15px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
        }
        .model-info {
            color: #666;
            font-size: 0.9em;
            text-align: right;
            font-style: italic;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
            margin-right: 10px;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .error {
            background: #f8d7da;
            border-left-color: #dc3545;
            color: #721c24;
        }
        .clear-btn {
            background: #6c757d;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 15px;
        }
        .clear-btn:hover {
            background: #5a6268;
        }
        .model-badge {
            background: #ea4335;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✨ Vertex AI Text Summarization</h1>       
        
        <div class="input-section">
            <label for="textInput">Enter text to summarize:</label>
            <textarea id="textInput" placeholder="Paste or type text here...">Climate change refers to long-term shifts in global temperatures and weather patterns. While climate variations are natural, since the 1800s human activities have been the main driver of climate change, primarily due to the burning of fossil fuels like coal, oil and gas. Burning fossil fuels generates greenhouse gas emissions that act like a blanket wrapped around the Earth, trapping the sun's heat and raising temperatures. The main greenhouse gases that are causing climate change include carbon dioxide and methane. These come from using gasoline for driving a car or coal for heating a building, for example. Clearing land and cutting down forests can also release carbon dioxide. Agriculture, oil and gas operations are major sources of methane emissions.</textarea>
        </div>
        
        <div class="button-container">
            <button class="summarize-btn" onclick="summarizeText()" {% if not vertex_ai_ready %}disabled{% endif %}>
                <span class="button-text">Generate Summary</span>
            </button>
        </div>
        
        <div id="result" class="result-section">
            <div class="summary-text" id="summaryText"></div>
            <div class="model-info" id="modelInfo"></div>
            <button class="clear-btn" onclick="clearResults()">Clear Results</button>
        </div>
    </div>

    <script>
        // Main API Function
        async function summarizeText() {
            const textInput = document.getElementById('textInput');
            const button = document.querySelector('.summarize-btn');
            const buttonText = document.querySelector('.button-text');
            const resultDiv = document.getElementById('result');
            const summaryDiv = document.getElementById('summaryText');
            const modelDiv = document.getElementById('modelInfo');
            
            const text = textInput.value.trim();
            if (!text) {
                alert('Please enter some text to summarize.');
                return;
            }
            
            // Show loading state
            button.disabled = true;
            buttonText.innerHTML = '<span class="loading"></span>Processing with Gemini 2.0...';
            resultDiv.className = 'result-section';
            
            try {
                const response = await fetch('/summarize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: text })
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP ${response.status}`);
                }
                
                const data = await response.json();
                
                // Show results
                summaryDiv.textContent = data.summary;
                modelDiv.textContent = `${data.model} • Processing Time: ${data.processing_time_ms}ms`;
                resultDiv.className = 'result-section show';
                
            } catch (error) {
                summaryDiv.textContent = `Error: ${error.message}`;
                modelDiv.textContent = 'Please check Vertex AI configuration.';
                resultDiv.className = 'result-section show error';
            }
            
            // Reset button
            button.disabled = false;
            buttonText.textContent = 'Generate Summary';
        }
        
        // Helper Functions
        function clearResults() {
            document.getElementById('result').className = 'result-section';
        }
        
        // Allow Enter key to submit
        document.getElementById('textInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.ctrlKey) {
                e.preventDefault();
                summarizeText();
            }
        });
    </script>
</body>
</html>
"""

# Route for the main page
@app.route('/')
def index():
    """Serve the HTML interface"""
    return render_template_string(HTML_TEMPLATE, vertex_ai_ready=VERTEX_AI_READY)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Vertex AI Gemini 2.0 Summarization Service',
        'project': PROJECT_ID,
        'location': LOCATION,
        'vertex_ai_ready': VERTEX_AI_READY,
        'model': 'gemini-2.0-flash-001',
        'version': 'gemini-2.0'
    })

# Text summarization endpoint
@app.route('/summarize', methods=['POST'])
def summarize():
    """Text summarization using Gemini 2.0 Flash"""
    import time
    start_time = time.time()
    
    try:
        # Check if Vertex AI is available
        if not VERTEX_AI_READY:
            return jsonify({
                'error': 'Vertex AI Gemini 2.0 is not available. Check initialization logs.'
            }), 503
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing "text" field in request body'}), 400
        
        input_text = data['text']
        if not input_text.strip():
            return jsonify({'error': 'Text field cannot be empty'}), 400
            
        logger.info('Processing Gemini 2.0 summarization request')
        
        # Create prompt for Gemini 2.0
        prompt = f"""Please provide a concise and informative summary of the following text. 
        The summary should capture the main points and key information in 2-3 sentences:

        {input_text}"""
        
        # Generate summary using Gemini 2.0 Flash
        response = model.generate_content(prompt)
        
        if not response.text or not response.text.strip():
            return jsonify({
                'error': 'Gemini 2.0 returned empty response'
            }), 500
            
        summary = response.text.strip()
        processing_time = int((time.time() - start_time) * 1000)
        
        result = {
            'summary': summary,
            'model': 'Google Vertex AI Gemini 2.0 Flash',
            'processing_time_ms': processing_time,
            'word_count': len(input_text.split()),
            'vertex_ai_used': True
        }
        
        logger.info(f'Gemini 2.0 summarization completed in {processing_time}ms')
        return jsonify(result)
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Gemini 2.0 Error: {error_msg}')
        
        return jsonify({
            'error': f'Gemini 2.0 failed: {error_msg}',
            'service': 'Vertex AI Gemini 2.0'
        }), 500

# Main function to run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)