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

        // 1. Try login first
        let res = await fetch('/api/v1/auth/login/json', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        // 2. If user does not exist yet (401), register and then login
        if (res.status === 401) {
            await fetch('/api/v1/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, full_name: "Lead Evaluator" })
            });

            res = await fetch('/api/v1/auth/login/json', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
        }

        if (res.ok) {
            const data = await res.json();
            authToken = data.access_token;
            const sb = document.getElementById('sb-status');
            if (sb) sb.innerText = `${email}`;
        }
    } catch (e) {
        console.warn("Auth initialization note:", e);
    }
}

// --- Interactive Auth Modal Controller (Option B) ---
function openAuthModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) {
        hideAuthAlert();
        modal.classList.add('open');
    }
}

function closeAuthModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) {
        modal.classList.remove('open');
    }
}

function switchAuthTab(tab) {
    hideAuthAlert();
    const loginTab = document.getElementById('auth-tab-login');
    const regTab = document.getElementById('auth-tab-register');
    const loginForm = document.getElementById('auth-form-login');
    const regForm = document.getElementById('auth-form-register');

    if (tab === 'login') {
        loginTab.classList.add('active');
        regTab.classList.remove('active');
        loginForm.style.display = 'block';
        regForm.style.display = 'none';
    } else {
        loginTab.classList.remove('active');
        regTab.classList.add('active');
        loginForm.style.display = 'none';
        regForm.style.display = 'block';
    }
}

function showAuthAlert(msg, isError = true) {
    const el = document.getElementById('auth-alert');
    if (!el) return;
    el.style.display = 'block';
    el.style.backgroundColor = isError ? '#fef2f2' : '#f0fdf4';
    el.style.color = isError ? '#dc2626' : '#16a34a';
    el.style.border = `1px solid ${isError ? '#fecaca' : '#bbf7d0'}`;
    el.innerText = msg;
}

function hideAuthAlert() {
    const el = document.getElementById('auth-alert');
    if (el) el.style.display = 'none';
}

function loadDemoEvaluatorCredentials() {
    document.getElementById('auth-login-email').value = "evaluator@pragatibharati.org";
    document.getElementById('auth-login-password').value = "EvaluatorSecure2026!";
    showAuthAlert("Demo credentials pre-filled.", false);
}

async function handleManualLogin() {
    hideAuthAlert();
    const email = document.getElementById('auth-login-email').value.trim();
    const password = document.getElementById('auth-login-password').value;

    if (!email || !password) {
        showAuthAlert("Please enter both email and password.");
        return;
    }

    try {
        const res = await fetch('/api/v1/auth/login/json', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (res.ok) {
            const data = await res.json();
            authToken = data.access_token;
            document.getElementById('sb-status').innerText = `${email}`;
            closeAuthModal();
            // Reset active selection and reload user's documents
            activeDocumentId = null;
            document.getElementById('status-doc-name').innerText = "None Selected";
            setStatusBadge("IDLE");
            updateProgressBar(0);
            document.getElementById('questions-viewport').innerHTML = `
                <div style="padding: 80px 20px; text-align: center; color: var(--wb-text-muted);">
                    <h3 style="color: var(--wb-text-primary); font-size: 15px; font-weight: 600;">Signed in as ${escapeHtml(email)}</h3>
                    <p style="margin-top: 6px; font-size: 13px;">Loaded multi-tenant documents for your account.</p>
                </div>
            `;
            await loadDocumentsList();
        } else {
            const err = await res.json();
            showAuthAlert(err.detail || "Authentication failed.");
        }
    } catch (e) {
        showAuthAlert("Network error: " + e.message);
    }
}

async function handleManualRegister() {
    hideAuthAlert();
    const fullName = document.getElementById('auth-reg-name').value.trim();
    const email = document.getElementById('auth-reg-email').value.trim();
    const password = document.getElementById('auth-reg-password').value;

    if (!fullName || !email || !password) {
        showAuthAlert("Please fill in all registration fields.");
        return;
    }

    if (password.length < 6) {
        showAuthAlert("Password must be at least 6 characters.");
        return;
    }

    try {
        const regRes = await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name: fullName })
        });

        if (!regRes.ok) {
            const err = await regRes.json();
            showAuthAlert(err.detail || "Registration failed.");
            return;
        }

        // Auto login on successful register
        const loginRes = await fetch('/api/v1/auth/login/json', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (loginRes.ok) {
            const data = await loginRes.json();
            authToken = data.access_token;
            document.getElementById('sb-status').innerText = `${email}`;
            closeAuthModal();
            activeDocumentId = null;
            document.getElementById('status-doc-name').innerText = "None Selected";
            setStatusBadge("IDLE");
            updateProgressBar(0);
            await loadDocumentsList();
        } else {
            switchAuthTab('login');
            showAuthAlert("Account created successfully! Please sign in.", false);
        }
    } catch (e) {
        showAuthAlert("Registration error: " + e.message);
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

// --- Modern Progress Bar & Badges ---
function updateProgressBar(percentage) {
    const track = document.getElementById('progress-block-track');
    if (track) {
        track.style.width = `${percentage}%`;
    }
    const textEl = document.getElementById('progress-text');
    if (textEl) {
        textEl.innerText = `${percentage}% Complete`;
    }
}

function setStatusBadge(text) {
    const badge = document.getElementById('status-badge');
    if (!badge) return;
    badge.innerText = text;
    if (text === 'COMPLETED') {
        badge.className = 'sys-flag-confident';
        badge.style = '';
    } else if (text === 'FAILED' || text === 'ERROR') {
        badge.className = 'sys-flag-review';
        badge.style = '';
    } else {
        badge.className = '';
        badge.style = 'background:#f5f5f4; color:#78716c; border:1px solid #e7e5e4; border-radius:4px; font-size:11px; font-weight:600; padding:2px 8px;';
    }
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
                    <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 175px;" title="${escapeHtml(doc.filename)}">📄 ${escapeHtml(doc.filename.substring(0, 22))}</span>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="font-size: 10px; font-weight: 500;">[${doc.status}]</span>
                        <button class="sys-doc-del-btn" onclick="event.stopPropagation(); deleteSingleDocument('${doc.id}', '${escapeHtml(doc.filename)}')" title="Delete this document">✕</button>
                    </div>
                `;
                item.onclick = () => selectActiveDocument(doc);
                container.appendChild(item);
            });
        }
    } catch (err) {
        console.error("Error loading documents:", err);
    }
}

async function deleteSingleDocument(docId, filename) {
    if (!authToken) {
        await authenticateDefaultUser();
    }
    if (!authToken) {
        alert("Authentication required. Please log in first.");
        return;
    }
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) return;

    try {
        const res = await fetch(`/api/v1/documents/${docId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (res.ok) {
            if (activeDocumentId === docId) {
                activeDocumentId = null;
                document.getElementById('status-doc-name').innerText = "None Selected";
                setStatusBadge("IDLE");
                updateProgressBar(0);
                document.getElementById('questions-viewport').innerHTML = `
                    <div style="padding: 80px 20px; text-align: center; color: var(--wb-text-muted);">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 12px; color: var(--wb-border-dark);"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                        <h3 style="color: var(--wb-text-primary); font-size: 15px; font-weight: 600;">Document Intelligence Workbench</h3>
                        <p style="margin-top: 6px; font-size: 13px;">Select an uploaded document from the archive on the left to review extracted questions.</p>
                    </div>
                `;
            }
            await loadDocumentsList();
        } else {
            const err = await res.json();
            alert(`Failed to delete document: ${err.detail || 'Unknown error'}`);
        }
    } catch (e) {
        alert("Delete error: " + e.message);
    }
}
window.deleteSingleDocument = deleteSingleDocument;

async function clearAllDocuments() {
    if (!authToken) {
        await authenticateDefaultUser();
    }
    if (!authToken) {
        alert("Authentication required. Please log in first.");
        return;
    }
    if (!confirm("Are you sure you want to clear ALL documents from the archive?")) return;

    try {
        const res = await fetch('/api/v1/documents', {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (res.ok) {
            activeDocumentId = null;
            document.getElementById('status-doc-name').innerText = "None Selected";
            setStatusBadge("IDLE");
            updateProgressBar(0);
            document.getElementById('questions-viewport').innerHTML = `
                <div style="padding: 80px 20px; text-align: center; color: var(--wb-text-muted);">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 12px; color: var(--wb-border-dark);"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                    <h3 style="color: var(--wb-text-primary); font-size: 15px; font-weight: 600;">Archive Cleared</h3>
                    <p style="margin-top: 6px; font-size: 13px;">All documents have been removed. Upload a new examination paper to begin.</p>
                </div>
            `;
            await loadDocumentsList();
        } else {
            const err = await res.json();
            alert(`Failed to clear archive: ${err.detail || 'Unknown error'}`);
        }
    } catch (e) {
        alert("Clear archive error: " + e.message);
    }
}
window.clearAllDocuments = clearAllDocuments;

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
                        ${isCorrect ? '<span style="color:#16a34a; font-weight:600; font-size:11px; margin-left:auto;">✓ Key Match</span>' : ''}
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
                    <span style="font-size: 11px; font-weight: 600; color: var(--wb-text-secondary); margin-left: 6px;">[${q.question_type.toUpperCase()}]</span>
                </div>
                <div>${badgeHtml}</div>
            </div>
            ${reasonsHtml}
            <div class="sys-q-body" style="margin-top: 8px;">
                <p style="white-space: pre-wrap;">${escapeHtml(q.question_text)}</p>
                ${optionsHtml}
            </div>
            <div class="sys-card-footer">
                <div>
                    Confidence: <strong>${q.confidence}</strong> | 
                    Identified Answer: <strong>${q.answer ? '[' + q.answer + ']' : 'NONE'}</strong>
                </div>
                <div style="display: flex; gap: 4px;">
                    ${q.review_required ? `<button class="sys-button primary" style="font-size: 11px; padding: 4px 10px;" onclick="approveQuestion('${q.id}')">✓ Approve Question</button>` : ''}
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


function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Explicit Global Window Bindings for HTML onclick handlers
window.clearAllDocuments = clearAllDocuments;
window.deleteSingleDocument = deleteSingleDocument;
window.openAuthModal = openAuthModal;
window.closeAuthModal = closeAuthModal;
window.switchAuthTab = switchAuthTab;
window.handleManualLogin = handleManualLogin;
window.handleManualRegister = handleManualRegister;
window.loadDemoEvaluatorCredentials = loadDemoEvaluatorCredentials;
window.openAssociateModal = openAssociateModal;
window.closeAssociateModal = closeAssociateModal;
window.submitAnswerKeyAssociation = submitAnswerKeyAssociation;
window.exportStructuredJson = exportStructuredJson;
window.closeExportModal = closeExportModal;
window.copyJsonToClipboard = copyJsonToClipboard;
window.downloadJsonFile = downloadJsonFile;
window.switchFilterTab = switchFilterTab;
window.approveQuestion = approveQuestion;
window.loadQuestionsForActiveDoc = loadQuestionsForActiveDoc;
window.uploadSelectedFile = uploadSelectedFile;
window.handleFileSelected = handleFileSelected;

