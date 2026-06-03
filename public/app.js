document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('question-form');
    const input = document.getElementById('question-input');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.spinner');
    
    const resultContainer = document.getElementById('result-container');
    const responseContent = document.getElementById('response-content');
    const copyBtn = document.getElementById('copy-btn');
    
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    const errorSuggestion = document.getElementById('error-suggestion');

    // Auto-resize textarea
    input.addEventListener('input', () => {
        // Auto resize height
        input.style.height = 'auto';
        input.style.height = `${Math.min(input.scrollHeight, 300)}px`;
    });

    // Keyboard shortcut: Ctrl + Enter to submit
    input.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            if (input.value.trim() && !submitBtn.disabled) {
                form.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const question = input.value.trim();
        const model = 'gpt-4.1-mini';

        if (!question) return;

        // Reset UI States
        setLoadingState(true);
        resultContainer.classList.add('hidden');
        errorContainer.classList.add('hidden');
        responseContent.innerHTML = '';
        errorMessage.textContent = '';
        errorSuggestion.textContent = '';

        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question, model })
            });

            const data = await response.json();

            if (!response.ok) {
                throw { 
                    status: response.status, 
                    message: data.error || 'Ein unbekannter Fehler ist aufgetreten.',
                    details: data.details
                };
            }

            // Render Markdown Response
            responseContent.innerHTML = formatMarkdown(data.reply);
            resultContainer.classList.remove('hidden');

            // Scroll response into view smoothly if on small screens
            resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        } catch (error) {
            console.error('Error during API request:', error);
            showError(error);
        } finally {
            setLoadingState(false);
        }
    });

    // Helper: Set UI Loading States
    function setLoadingState(isLoading) {
        submitBtn.disabled = isLoading;
        input.disabled = isLoading;

        if (isLoading) {
            btnText.textContent = 'Antwort wird generiert...';
            spinner.classList.remove('hidden');
        } else {
            btnText.textContent = 'Frage senden';
            spinner.classList.add('hidden');
        }
    }

    // Helper: Show Error Messages with Smart Diagnostics
    function showError(error) {
        errorContainer.classList.remove('hidden');
        errorMessage.textContent = error.message;
        
        // Context-aware troubleshooting suggestions
        if (error.status === 404 || (error.message && error.message.includes('model'))) {
            errorSuggestion.innerHTML = `<strong>Tipp:</strong> Das KI-Modell konnte nicht geladen werden. Bitte vergewissere dich, dass der API-Key aktiv ist.`;
        } else if (error.status === 401 || (error.message && error.message.includes('API key'))) {
            errorSuggestion.innerHTML = `<strong>Tipp:</strong> Der bereitgestellte API-Key ist ungültig oder abgelaufen. Bitte überprüfe den Key in deiner <code>.env</code>-Datei.`;
        } else {
            errorSuggestion.innerHTML = `<strong>Tipp:</strong> Bitte überprüfe deine Internetverbindung und stelle sicher, dass der API-Key aktiv ist.`;
        }
        
        errorContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Copy to clipboard with visual feedback
    copyBtn.addEventListener('click', async () => {
        // Extract raw text from the parsed HTML container (or we can keep raw text somewhere, but innerText works perfectly)
        const textToCopy = responseContent.innerText;
        
        try {
            await navigator.clipboard.writeText(textToCopy);
            
            // Success Feedback
            copyBtn.classList.add('success');
            copyBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425z"/>
                </svg>
                Kopiert!
            `;

            setTimeout(() => {
                copyBtn.classList.remove('success');
                copyBtn.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"/>
                        <path d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5h3zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3z"/>
                    </svg>
                    Kopieren
                `;
            }, 2000);
        } catch (err) {
            console.error('Kopieren fehlgeschlagen:', err);
        }
    });

    // Elegant lightweight Markdown parser (Safe Regex based)
    function formatMarkdown(text) {
        if (!text) return '';
        
        let html = text;
        
        // Escape HTML to prevent XSS
        html = html
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
            
        // Code blocks: ```code```
        html = html.replace(/```([\s\S]*?)```/g, (match, code) => {
            return `<pre><code>${code.trim()}</code></pre>`;
        });
        
        // Inline code: `code`
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Bold: **text**
        html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Italic: *text*
        html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        
        // Headings: ### heading
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
        
        // Lists: - item or * item
        html = html.replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>');
        html = html.replace(/^\s*\*\s+(.*$)/gim, '<li>$1</li>');
        
        // Wrap <li> elements in <ul>
        // Match consecutive <li> elements and wrap them
        html = html.replace(/(<li>.*<\/li>)+/g, '<ul>$&</ul>');
        
        return html;
    }

});

