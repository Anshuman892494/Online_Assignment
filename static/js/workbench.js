// ==========================================================================
// CLASSIC RETRO WORKBENCH CONTROLLER
// Document Intelligence & Question Extraction Service
// ==========================================================================

let authToken = null;
let activeDocumentId = null;
let pollingInterval = null;
let activeFilter = 'all';
let allLoadedQuestions = [];
let userDocuments = [];

document.addEventListener('DOMContentLoaded', async () => {
    initDragAndDrop();
    await authenticateDefaultUser();
    await loadDocumentsList();
});

// --- Authentication ---
async function authenticateDefaultUser() {
    try {
        const email = "evaluator@pragatibharati.org";
        const password = "EvaluatorSecure2026!";

        // Register if not exists
        await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name: "Lead Evaluator" })
        });

        // Login
        const res = await fetch('/api/v1/auth/login/json', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (res.ok) {
            const data = await res.json();
            authToken = data.access_token;
            document.getElementById('sb-status').innerText = `Logged in: ${email}`;
        }
    } catch (e) {
        console.warn("Auth initialization note:", e);
    }
}

// --- Drag & Drop ---
function initDragAndDrop() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-upload-input');

    ['dragenter', 'dragover'].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelected(fileInput);
        }
    });
}

function handleFileSelected(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        document.getElementById('drop-zone-text').innerHTML = `
            <strong>Selected:</strong><br>${file.name} (${(file.size / 1024).toFixed(1)} KB)
        `;
    }
}

// --- File Upload ---
async function uploadSelectedFile() {
    const fileInput = document.getElementById('file-upload-input');
    if (!fileInput.files || fileInput.files.length === 0) {
        alert("Please select a file first.");
        return;
    }

    const file = fileInput.files[0];
    const role = document.getElementById('doc-role-select').value;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('role', role);

    document.getElementById('status-doc-name').innerText = file.name;
    setStatusBadge('QUEUED', '#000080');
    updateProgressBar(10);

    try {
        const res = await fetch('/api/v1/documents/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });

        if (!res.ok) {
            const err = await res.json();
            alert(`Upload Failed: ${err.detail || 'Unknown error'}`);
            setStatusBadge('FAILED', '#800000');
            updateProgressBar(0);
            return;
        }

        const data = await res.json();
        activeDocumentId = data.id;
        document.getElementById('status-doc-name').innerText = data.filename;
        
        // Start polling status
        startStatusPolling(data.id);
        await loadDocumentsList();

    } catch (e) {
        alert("Network error while uploading: " + e.message);
        setStatusBadge('ERROR', '#800000');
    }
}

// --- Asynchronous Status Polling ---
function startStatusPolling(docId) {
    if (pollingInterval) clearInterval(pollingInterval);

    pollingInterval = setInterval(async () => {
        try {
            const res = await fetch(`/api/v1/documents/${docId}/status`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });

            if (res.ok) {
                const statusData = await res.json();
                updateProgressBar(statusData.progress);
                
                if (statusData.status === 'COMPLETED') {
                    setStatusBadge('COMPLETED', '#008000');
                    document.getElementById('progress-text').innerText = '100% Extraction Completed';
                    clearInterval(pollingInterval);
                    await loadQuestionsForActiveDoc();
                    await loadDocumentsList();
                } else if (statusData.status === 'FAILED') {
                    setStatusBadge('FAILED', '#800000');
                    document.getElementById('progress-text').innerText = `Error: ${statusData.error_message || 'Processing failed'}`;
                    clearInterval(pollingInterval);
                } else {
                    setStatusBadge(statusData.status, '#000080');
                    document.getElementById('progress-text').innerText = `${statusData.progress}% Processing...`;
                }
            }
        } catch (err) {
            console.error("Polling error:", err);
        }
    }, 1000);
}

// --- Segmented Progress Bar ---
function updateProgressBar(percentage) {
    const track = document.getElementById('progress-block-track');
    track.innerHTML = '';
    const numBlocks = Math.floor(percentage / 5);
    for (let i = 0; i < numBlocks; i++) {
        const chunk = document.createElement('div');
        chunk.className = 'sys-block-chunk';
        track.appendChild(chunk);
    }
    track.style.width = `${percentage}%`;
    document.getElementById('progress-text').innerText = `${percentage}% Complete`;
}

function setStatusBadge(text, color) {
    const badge = document.getElementById('status-badge');
    badge.innerText = text;
    badge.style.backgroundColor = color;
}

// --- Document Archive List ---
async function loadDocumentsList() {
    try {
        const res = await fetch('/api/v1/documents', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (res.ok) {
            userDocuments = await res.json();
            const container = document.getElementById('documents-list-container');
            container.innerHTML = '';

            if (userDocuments.length === 0) {
                container.innerHTML = '<div style="padding: 10px; text-align: center; color: #666;">No documents loaded.</div>';
                return;
            }

            userDocuments.forEach(doc => {
                const item = document.createElement('div');
                item.className = `sys-doc-item ${doc.id === activeDocumentId ? 'active' : ''}`;
                item.innerHTML = `
                    <span>&#128196; ${doc.filename.substring(0, 22)}</span>
                    <span>[${doc.status}]</span>
                `;
                item.onclick = () => selectActiveDocument(doc);
                container.appendChild(item);
            });
        }
    } catch (err) {
        console.error("Error loading documents:", err);
    }
}

function selectActiveDocument(doc) {
    activeDocumentId = doc.id;
    document.getElementById('status-doc-name').innerText = doc.filename;
    setStatusBadge(doc.status, doc.status === 'COMPLETED' ? '#008000' : '#000080');
    updateProgressBar(doc.progress);
    loadDocumentsList();
    loadQuestionsForActiveDoc();
}

// --- Question Desk & Rendering ---
async function loadQuestionsForActiveDoc() {
    if (!activeDocumentId) return;

    try {
        const res = await fetch(`/api/v1/documents/${activeDocumentId}/questions?limit=200`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (res.ok) {
            const data = await res.json();
            allLoadedQuestions = data.questions;
            updateTabCounts();
            renderQuestions();
        }
    } catch (err) {
        console.error("Error loading questions:", err);
    }
}

function updateTabCounts() {
    const total = allLoadedQuestions.length;
    const review = allLoadedQuestions.filter(q => q.review_required).length;
    const confident = allLoadedQuestions.filter(q => !q.review_required).length;

    document.getElementById('badge-count-all').innerText = total;
    document.getElementById('badge-count-review').innerText = review;
    document.getElementById('badge-count-confident').innerText = confident;
}

function switchFilterTab(filter) {
    activeFilter = filter;
    document.getElementById('tab-all').classList.toggle('active', filter === 'all');
    document.getElementById('tab-review').classList.toggle('active', filter === 'review');
    document.getElementById('tab-confident').classList.toggle('active', filter === 'confident');
    renderQuestions();
}

function renderQuestions() {
    const viewport = document.getElementById('questions-viewport');
    viewport.innerHTML = '';

    let questionsToShow = allLoadedQuestions;
    if (activeFilter === 'review') {
        questionsToShow = allLoadedQuestions.filter(q => q.review_required);
    } else if (activeFilter === 'confident') {
        questionsToShow = allLoadedQuestions.filter(q => !q.review_required);
    }

    if (questionsToShow.length === 0) {
        viewport.innerHTML = `
            <div style="padding: 40px; text-align: center; font-family: var(--sys-font-mono);">
                <h4>NO QUESTIONS FOUND UNDER FILTER [${activeFilter.toUpperCase()}]</h4>
            </div>
        `;
        return;
    }

    questionsToShow.forEach(q => {
        const card = document.createElement('div');
        card.className = 'sys-question-card sys-bevel-outset';

        // Header
        const pagesStr = (q.source_pages || []).join(' &rarr; ');
        const badgeHtml = q.review_required 
            ? `<span class="sys-flag-review">&#9888; REVIEW REQUIRED</span>`
            : `<span class="sys-flag-confident">&#10004; CONFIDENT (${Math.round(q.confidence * 100)}%)</span>`;

        let reasonsHtml = '';
        if (q.review_reasons && q.review_reasons.length > 0) {
            reasonsHtml = `<div style="margin-top: 4px; font-size: 10px; color: var(--sys-badge-review); font-weight: bold;">
                Flags: [${q.review_reasons.join(', ')}]
            </div>`;
        }

        // Options Grid
        let optionsHtml = '';
        if (q.options && q.options.length > 0) {
            optionsHtml = '<div class="sys-options-grid">';
            q.options.forEach(opt => {
                const isCorrect = q.answer && q.answer.trim().toUpperCase() === opt.label.trim().toUpperCase();
                optionsHtml += `
                    <div class="sys-option-row ${isCorrect ? 'correct' : ''}">
                        <input type="radio" disabled ${isCorrect ? 'checked' : ''}>
                        <strong>[${opt.label}]</strong>
                        <span>${escapeHtml(opt.text)}</span>
                        ${isCorrect ? '<em style="color:#008000; margin-left:auto;">[Key Match]</em>' : ''}
                    </div>
                `;
            });
            optionsHtml += '</div>';
        }

        card.innerHTML = `
            <div class="sys-card-header">
                <div>
                    <span class="sys-q-num">Q${q.question_number}</span>
                    <span class="sys-q-pages">[Page ${pagesStr}]</span>
                    <span style="font-size: 10px; font-weight: bold; margin-left: 6px;">[${q.question_type.toUpperCase()}]</span>
                </div>
                <div>${badgeHtml}</div>
            </div>
            ${reasonsHtml}
            <div class="sys-q-body sys-bevel-inset" style="margin-top: 6px;">
                <p style="white-space: pre-wrap;">${escapeHtml(q.question_text)}</p>
                ${optionsHtml}
            </div>
            <div class="sys-card-footer">
                <div>
                    Confidence: <strong>${q.confidence}</strong> | 
                    Identified Answer: <strong>${q.answer ? '[' + q.answer + ']' : 'NONE'}</strong>
                </div>
                <div style="display: flex; gap: 4px;">
                    ${q.review_required ? `<button class="sys-button" onclick="approveQuestion('${q.id}')">&#10004; Approve</button>` : ''}
                </div>
            </div>
        `;

        viewport.appendChild(card);
    });
}

async function approveQuestion(qId) {
    if (!activeDocumentId) return;
    try {
        const res = await fetch(`/api/v1/documents/${activeDocumentId}/questions/${qId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ review_required: false })
        });
        if (res.ok) {
            await loadQuestionsForActiveDoc();
        }
    } catch (e) {
        alert("Error approving question: " + e.message);
    }
}

// --- Standard JSON Export ---
async function exportStructuredJson() {
    if (!activeDocumentId) {
        alert("Please select a processed document to export.");
        return;
    }
    try {
        const res = await fetch(`/api/v1/documents/${activeDocumentId}/export`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (res.ok) {
            const data = await res.json();
            document.getElementById('export-json-content').value = JSON.stringify(data, null, 2);
            document.getElementById('export-modal').classList.add('open');
        }
    } catch (err) {
        alert("Export error: " + err.message);
    }
}

function closeExportModal() {
    document.getElementById('export-modal').classList.remove('open');
}

function copyJsonToClipboard() {
    const text = document.getElementById('export-json-content').value;
    navigator.clipboard.writeText(text);
    alert("Structured JSON copied to clipboard!");
}

function downloadJsonFile() {
    const text = document.getElementById('export-json-content').value;
    const blob = new Blob([text], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `extracted_${activeDocumentId || 'questions'}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// --- Link Separate Answer Key Modal ---
function openAssociateModal() {
    if (!activeDocumentId) {
        alert("Select a question paper document first.");
        return;
    }
    const select = document.getElementById('associate-key-doc-select');
    select.innerHTML = '';
    const candidates = userDocuments.filter(d => d.id !== activeDocumentId);
    if (candidates.length === 0) {
        alert("No other uploaded documents available to link as an answer key.");
        return;
    }
    candidates.forEach(doc => {
        const opt = document.createElement('option');
        opt.value = doc.id;
        opt.innerText = `${doc.filename} (${doc.role})`;
        select.appendChild(opt);
    });
    document.getElementById('associate-modal').classList.add('open');
}

function closeAssociateModal() {
    document.getElementById('associate-modal').classList.remove('open');
}

async function submitAnswerKeyAssociation() {
    const keyDocId = document.getElementById('associate-key-doc-select').value;
    try {
        const res = await fetch(`/api/v1/documents/${activeDocumentId}/associate-answer-key`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ answer_key_document_id: keyDocId })
        });
        if (res.ok) {
            const result = await res.json();
            alert(result.message);
            closeAssociateModal();
            await loadQuestionsForActiveDoc();
        } else {
            const err = await res.json();
            alert(`Association Failed: ${err.detail || 'Unknown error'}`);
        }
    } catch (e) {
        alert("Association error: " + e.message);
    }
}

function showAboutModal() {
    alert("Pragati Bharati — Round 2 Engineering Assignment\nDocument Intelligence & Question Extraction Workbench\nTechnology: FastAPI + PostgreSQL + Redis + PyMuPDF + Gemini Vision AI");
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
