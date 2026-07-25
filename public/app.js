document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('auditForm');
    const input = document.getElementById('urlInput');
    const btn = document.getElementById('submitBtn');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');
    const errorContainer = document.getElementById('errorContainer');
    const resultsSection = document.getElementById('resultsSection');

    // DOM Elements for results
    const resStatus = document.getElementById('resStatus');
    const resTime = document.getElementById('resTime');
    const resTitle = document.getElementById('resTitle');
    const resDesc = document.getElementById('resDesc');
    const resWords = document.getElementById('resWords');
    const resH1 = document.getElementById('resH1');
    const resImages = document.getElementById('resImages');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        let url = input.value.trim();
        if (!url) return;
        
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            url = 'https://' + url;
            input.value = url;
        }

        // UI Loading State
        errorContainer.style.display = 'none';
        resultsSection.style.display = 'none';
        btn.disabled = true;
        btnText.style.display = 'none';
        loader.style.display = 'block';

        try {
            // Use relative path - works on both localhost and Vercel
            const response = await fetch(`/api/audit?url=${encodeURIComponent(url)}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'An error occurred while fetching the audit data.');
            }

            if (data.success === false) {
                // Handled error (e.g. non-HTML content)
                throw new Error(data.error_message);
            }

            // Populate Results
            populateResults(data);
            
            // Show Results
            resultsSection.style.display = 'block';
            resultsSection.classList.add('fade-in');

        } catch (error) {
            errorContainer.textContent = error.message;
            errorContainer.style.display = 'block';
        } finally {
            // Restore UI state
            btn.disabled = false;
            btnText.style.display = 'block';
            loader.style.display = 'none';
        }
    });

    function populateResults(payload) {
        const data = payload.data;
        
        // Status & Time
        resStatus.textContent = payload.status_code;
        resStatus.className = 'metric highlight'; // Reset class
        if (payload.status_code >= 400) {
            resStatus.className = 'metric alert';
            resStatus.style.color = 'var(--error)';
        }

        resTime.textContent = `${payload.response_time_ms}ms`;

        // Meta
        resTitle.textContent = data.page_title || 'No title tag found';
        resTitle.style.color = data.page_title ? 'inherit' : 'var(--text-muted)';
        
        resDesc.textContent = data.meta_description || 'No meta description found';
        resDesc.style.color = data.meta_description ? 'inherit' : 'var(--text-muted)';

        // Content
        resWords.textContent = data.approximate_word_count.toLocaleString();
        resH1.textContent = data.h1_count;
        
        resImages.textContent = data.images_missing_alt;
        if (data.images_missing_alt > 0) {
            resImages.className = 'metric alert';
            resImages.style.color = 'var(--error)';
        } else {
            resImages.className = 'metric highlight';
            resImages.style.color = 'var(--success)';
        }
    }
});
