document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('generator-form');
    const loader = document.getElementById('loader');
    const resultsDiv = document.getElementById('results');
    const errorDiv = document.getElementById('error');
    const generateBtn = document.getElementById('generate-btn');
    const downloadBtn = document.getElementById('download-btn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const topic = document.getElementById('topic').value;
        const style = document.getElementById('style').value;

        loader.classList.remove('hidden');
        resultsDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        generateBtn.disabled = true;

        try {
            const response = await fetch('/api/generate-blog-post', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic, style }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'An unknown error occurred.');
            }

            const data = await response.json();
            displayResults(data);

            downloadBtn.classList.remove('hidden');

        } catch (err) {
            errorDiv.textContent = `Error: ${err.message}`;
            errorDiv.classList.remove('hidden');
        } finally {
            loader.classList.add('hidden');
            generateBtn.disabled = false;
        }
    });

    function displayResults(data) {
        document.getElementById('result-title').textContent = data.title;
        document.getElementById('result-slug').textContent = data.slug;
        document.getElementById('result-description').innerHTML = marked.parse(data.description);

        document.getElementById('result-toc').innerHTML = marked.parse(data.tableOfContents);
        document.getElementById('result-content').innerHTML = marked.parse(data.content);

        document.getElementById('result-seo-title').textContent = data.seo.title;
        document.getElementById('result-seo-description').textContent = data.seo.description;

        const faqContainer = document.getElementById('result-faq');
        faqContainer.innerHTML = '';
        data.faq.forEach(item => {
            const faqItem = document.createElement('div');
            faqItem.className = 'faq-item';
            faqItem.innerHTML = `
                <h4>${item.title}</h4>
                <p>${item.description}</p>
            `;
            faqContainer.appendChild(faqItem);
        });

        resultsDiv.classList.remove('hidden');
    }
});