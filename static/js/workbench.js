// ==========================================================================
// CLASSIC RETRO WORKBENCH CONTROLLER
// Document Intelligence & Question Extraction Service
// ==========================================================================

let authToken = (typeof localStorage !== 'undefined' ? localStorage.getItem('pragati_token') : null) || window.authToken || null;
let activeDocumentId = null;
let pollingInterval = null;
let activeFilter = 'all';
let allLoadedQuestions = [];
let userDocuments = [];
let isAuthMandatory = false;

document.addEventListener('DOMContentLoaded', async () => {
    initDragAndDrop();
    await checkAuthenticationState();
});

// --- Authentication State Management & Gating ---
async function checkAuthenticationState() {
    authToken = (typeof localStorage !== 'undefined' ? localStorage.getItem('pragati_token') : null) || window.authToken || null;
    if (authToken) {
        try {
            const res = await fetch('/api/v1/auth/me', {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            if (res.ok) {
                const user = await res.json();
                setAuthenticatedUI(user.email);
                await loadDocumentsList();
                return true;
            }
        } catch (e) {
            console.warn("Auth token verification error:", e);
        }
    }
    // No token or token invalid: lock features and open mandatory login modal
    setUnauthenticatedUI();
    openAuthModal(true);
    return false;
}

function setAuthenticatedUI(email) {
    isAuthMandatory = false;
    const sb = document.getElementById('sb-status');
    if (sb) sb.innerText = email || "Evaluator";
    const dot = document.getElementById('sb-dot');
    if (dot) {
        dot.className = 'sys-dot-online';
    }
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) logoutBtn.style.display = 'inline-flex';

    // Unlock workspace
    const workspace = document.querySelector('.sys-workspace');
    if (workspace) workspace.classList.remove('sys-locked');

    // Enable close/cancel in modal for normal account management
    const closeBtn = document.getElementById('auth-modal-close-btn');
    if (closeBtn) closeBtn.style.display = 'block';
    const loginCancel = document.getElementById('auth-login-cancel-btn');
    if (loginCancel) loginCancel.style.display = 'inline-flex';
    const regCancel = document.getElementById('auth-reg-cancel-btn');
    if (regCancel) regCancel.style.display = 'inline-flex';
    const gateNotice = document.getElementById('auth-gate-notice');
    if (gateNotice) gateNotice.style.display = 'none';
    const modalTitle = document.getElementById('auth-modal-title');
    if (modalTitle) modalTitle.innerText = "User Authentication & Multi-Tenancy";
}

function setUnauthenticatedUI() {
    isAuthMandatory = true;
    authToken = null;
    window.authToken = null;
    if (typeof localStorage !== 'undefined') localStorage.removeItem('pragati_token');

    const sb = document.getElementById('sb-status');
    if (sb) sb.innerText = "Not Signed In";
    const dot = document.getElementById('sb-dot');
    if (dot) {
        dot.className = 'sys-dot-offline';
    }
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) logoutBtn.style.display = 'none';

    // Lock workspace
    const workspace = document.querySelector('.sys-workspace');
    if (workspace) workspace.classList.add('sys-locked');

    // Empty list container
    const container = document.getElementById('documents-list-container');
    if (container) container.innerHTML = '<div style="padding: 16px; text-align: center; color: var(--wb-text-muted); font-size: 12px;">Sign in to view archive</div>';

    // Reset status and viewport
    activeDocumentId = null;
    const docName = document.getElementById('status-doc-name');
    if (docName) docName.innerText = "None Selected";
    setStatusBadge("LOCKED");
    updateProgressBar(0);
    const viewport = document.getElementById('questions-viewport');
    if (viewport) {
        viewport.innerHTML = `
            <div style="padding: 80px 20px; text-align: center; color: var(--wb-text-muted);">
                <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 12px; color: var(--wb-primary);"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                <h3 style="color: var(--wb-text-primary); font-size: 15px; font-weight: 600;">Authentication Required</h3>
                <p style="margin-top: 6px; font-size: 13px;">Please sign in or register above to access the document intelligence workspace.</p>
            </div>
        `;
    }

    // Modal elements for mandatory auth
    const closeBtn = document.getElementById('auth-modal-close-btn');
    if (closeBtn) closeBtn.style.display = 'none';
    const loginCancel = document.getElementById('auth-login-cancel-btn');
    if (loginCancel) loginCancel.style.display = 'none';
    const regCancel = document.getElementById('auth-reg-cancel-btn');
    if (regCancel) regCancel.style.display = 'none';
    const gateNotice = document.getElementById('auth-gate-notice');
    if (gateNotice) gateNotice.style.display = 'flex';
    const modalTitle = document.getElementById('auth-modal-title');
    if (modalTitle) modalTitle.innerText = "Sign In Required";
}

function handleUnauthorizedResponse() {
    setUnauthenticatedUI();
    openAuthModal(true);
    showAuthAlert("Your session has expired or authentication is required. Please sign in.");
}

function handleLogout() {
    setUnauthenticatedUI();
    openAuthModal(true);
    showAuthAlert("You have signed out successfully.", false);
}

// --- Interactive Auth Modal Controller ---
function openAuthModal(mandatory = false) {
    if (mandatory || !authToken) {
        setUnauthenticatedUI();
    }
    const modal = document.getElementById('auth-modal');
    if (modal) {
        hideAuthAlert();
        modal.classList.add('open');
        if (isAuthMandatory) {
            modal.classList.add('mandatory');
        } else {
            modal.classList.remove('mandatory');
        }
    }
}

function closeAuthModal() {
    if (isAuthMandatory && !authToken) {
        showAuthAlert("You must sign in or create an account to access the workbench features.");
        return;
    }
    const modal = document.getElementById('auth-modal');
    if (modal) {
        modal.classList.remove('open');
        modal.classList.remove('mandatory');
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
        let res = await fetch('/api/v1/auth/login/json', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        // If evaluator demo user is not yet created in a fresh DB, register it seamlessly
        if (res.status === 401 && email === "evaluator@pragatibharati.org") {
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
            if (typeof localStorage !== 'undefined') localStorage.setItem('pragati_token', authToken);
            window.authToken = authToken;
            setAuthenticatedUI(email);
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
            const err = await res.json().catch(() => ({}));
            showAuthAlert(err.detail || "Authentication failed. Please check credentials.");
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
            const err = await regRes.json().catch(() => ({}));
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
            if (typeof localStorage !== 'undefined') localStorage.setItem('pragati_token', authToken);
            window.authToken = authToken;
            setAuthenticatedUI(email);
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
        if (!authToken) {
            openAuthModal(true);
            showAuthAlert("Please sign in first to upload documents.");
            return;
        }
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelected(fileInput);
        }
    });
}

function handleFileSelected(input) {
    const textEl = document.getElementById('drop-zone-text');
    if (!textEl) return;
    if (!input.files || input.files.length === 0) {
        textEl.innerHTML = `
            <strong style="color: var(--wb-primary);">Click or Drag & Drop Documents</strong><br>
            Single or Multiple PDFs, Scanned pages, PNG, JPG (Max 25MB each)
        `;
        return;
    }

    if (input.files.length === 1) {
        const file = input.files[0];
        textEl.innerHTML = `
            <strong style="color: #16a34a;">✓ 1 File Selected:</strong><br>
            <span style="font-weight: 600; color: var(--wb-text-primary);">${escapeHtml(file.name)}</span> (${(file.size / 1024).toFixed(1)} KB)
        `;
    } else {
        const totalSize = Array.from(input.files).reduce((acc, f) => acc + f.size, 0);
        const fileNames = Array.from(input.files).map(f => escapeHtml(f.name)).slice(0, 3).join(', ');
        const more = input.files.length > 3 ? ` +${input.files.length - 3} more` : '';
        textEl.innerHTML = `
            <strong style="color: #16a34a;">✓ ${input.files.length} Files Selected:</strong><br>
            <span style="font-size: 11px; color: var(--wb-text-primary);">${fileNames}${more}</span><br>
            <span style="font-size: 11px; color: var(--wb-text-muted);">Total: ${(totalSize / 1024 / 1024).toFixed(2)} MB</span>
        `;
    }
}

// --- File Upload (Single & Batch Multiple) ---
async function uploadSelectedFile() {
    if (!authToken) {
        openAuthModal(true);
        showAuthAlert("Please sign in or create an account to upload documents.");
        return;
    }

    const fileInput = document.getElementById('file-upload-input');
    if (!fileInput.files || fileInput.files.length === 0) {
        alert("Please select one or more files first.");
        return;
    }

    const files = Array.from(fileInput.files);
    const defaultRole = document.getElementById('doc-role-select').value;
    const uploadBtn = document.querySelector('.sys-groupbox .sys-button.primary');
    if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.innerText = `Ingesting ${files.length} document${files.length > 1 ? 's' : ''}...`;
    }

    let successCount = 0;
    let lastUploadedDocId = null;
    let lastUploadedFilename = null;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        // Smart role detection if filename suggests answer key
        let role = defaultRole;
        if (files.length > 1 && defaultRole === 'QUESTION_PAPER') {
            const fnameLower = file.name.toLowerCase();
            if (fnameLower.includes('answer') || fnameLower.includes('key') || fnameLower.includes('solution')) {
                role = 'ANSWER_KEY';
            }
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('role', role);

        document.getElementById('status-doc-name').innerText = `[${i + 1}/${files.length}] ${file.name}`;
        setStatusBadge('QUEUED', '#000080');
        updateProgressBar(Math.round(((i) / files.length) * 100));

        try {
            const token = (typeof localStorage !== 'undefined' ? localStorage.getItem('pragati_token') : null) || authToken;
            const res = await fetch('/api/v1/documents/upload', {
                method: 'POST',
                headers: token ? { 'Authorization': `Bearer ${token}` } : {},
                body: formData
            });

            if (res.status === 401) {
                if (uploadBtn) {
                    uploadBtn.disabled = false;
                    uploadBtn.innerText = "Submit to Ingestion Queue";
                }
                handleUnauthorizedResponse();
                return;
            }

            if (res.ok) {
                const data = await res.json();
                successCount++;
                lastUploadedDocId = data.id;
                lastUploadedFilename = data.filename;
            } else {
                const err = await res.json().catch(() => ({}));
                console.error(`Failed to upload ${file.name}:`, err);
            }
        } catch (e) {
            console.error(`Upload error for ${file.name}:`, e);
        }
    }

    if (uploadBtn) {
        uploadBtn.disabled = false;
        uploadBtn.innerText = "Submit to Ingestion Queue";
    }

    if (successCount > 0) {
        await loadDocumentsList();
        if (lastUploadedDocId) {
            activeDocumentId = lastUploadedDocId;
            document.getElementById('status-doc-name').innerText = lastUploadedFilename || 'Uploaded';
            startStatusPolling(lastUploadedDocId);
        }
        // Reset file input and dropzone text
        fileInput.value = '';
        handleFileSelected(fileInput);
    } else {
        alert("Failed to upload selected file(s). Please verify file size and format.");
        setStatusBadge('FAILED', '#800000');
        updateProgressBar(0);
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

            if (res.status === 401) {
                clearInterval(pollingInterval);
                handleUnauthorizedResponse();
                return;
            }

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
    if (!authToken) return;
    try {
        const res = await fetch('/api/v1/documents', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (res.status === 401) {
            handleUnauthorizedResponse();
            return;
        }
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
        openAuthModal(true);
        alert("Authentication required. Please log in first.");
        return;
    }
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) return;

    try {
        const res = await fetch(`/api/v1/documents/${docId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (res.status === 401) {
            handleUnauthorizedResponse();
            return;
        }

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
            const err = await res.json().catch(() => ({}));
            alert(`Failed to delete document: ${err.detail || 'Unknown error'}`);
        }
    } catch (e) {
        alert("Delete error: " + e.message);
    }
}
window.deleteSingleDocument = deleteSingleDocument;

async function clearAllDocuments() {
    if (!authToken) {
        openAuthModal(true);
        alert("Authentication required. Please log in first.");
        return;
    }
    if (!confirm("Are you sure you want to clear ALL documents from the archive?")) return;

    try {
        const res = await fetch('/api/v1/documents', {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (res.status === 401) {
            handleUnauthorizedResponse();
            return;
        }

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
            const err = await res.json().catch(() => ({}));
            alert(`Failed to clear archive: ${err.detail || 'Unknown error'}`);
        }
    } catch (e) {
        alert("Clear archive error: " + e.message);
    }
}
window.clearAllDocuments = clearAllDocuments;

function selectActiveDocument(doc) {
    if (!authToken) {
        openAuthModal(true);
        return;
    }
    activeDocumentId = doc.id;
    document.getElementById('status-doc-name').innerText = doc.filename;
    setStatusBadge(doc.status, doc.status === 'COMPLETED' ? '#008000' : '#000080');
    updateProgressBar(doc.progress);
    loadDocumentsList();
    loadQuestionsForActiveDoc();
}

// --- Question Desk & Rendering ---
async function loadQuestionsForActiveDoc() {
    if (!activeDocumentId || !authToken) return;

    try {
        const res = await fetch(`/api/v1/documents/${activeDocumentId}/questions?limit=200`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (res.status === 401) {
            handleUnauthorizedResponse();
            return;
        }

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
    if (!authToken) {
        openAuthModal(true);
        return;
    }
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
        if (res.status === 401) {
            handleUnauthorizedResponse();
            return;
        }
        if (res.ok) {
            await loadQuestionsForActiveDoc();
        }
    } catch (e) {
        alert("Error approving question: " + e.message);
    }
}

// --- Standard JSON Export ---
async function exportStructuredJson() {
    if (!authToken) {
        openAuthModal(true);
        return;
    }
    if (!activeDocumentId) {
        alert("Please select a processed document to export.");
        return;
    }
    try {
        const token = (typeof localStorage !== 'undefined' ? localStorage.getItem('pragati_token') : null) || authToken;
        const res = await fetch(`/api/v1/documents/${activeDocumentId}/export`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        if (res.status === 401) {
            handleUnauthorizedResponse();
            return;
        }
        if (res.ok) {
            const data = await res.json();
            const textarea = document.getElementById('export-json-content');
            if (textarea) textarea.value = JSON.stringify(data, null, 2);

            const statsEl = document.getElementById('export-stats-text');
            if (statsEl) {
                statsEl.innerText = `File: ${data.filename} • ${data.total_questions} Questions • ${data.review_required_count} Flagged for Review`;
            }

            const modal = document.getElementById('export-modal');
            if (modal) modal.classList.add('open');
        } else {
            const err = await res.json().catch(() => ({}));
            alert("Export error: " + (err.detail || res.statusText));
        }
    } catch (err) {
        alert("Export error: " + err.message);
    }
}

function closeExportModal() {
    const modal = document.getElementById('export-modal');
    if (modal) modal.classList.remove('open');
}

function copyJsonToClipboard() {
    const textarea = document.getElementById('export-json-content');
    if (!textarea) return;
    const text = textarea.value;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('btn-copy-json');
        if (btn) {
            const originalHtml = btn.innerHTML;
            btn.innerHTML = '<span style="color: #16a34a; font-weight: 600;">✓ Copied to Clipboard!</span>';
            setTimeout(() => {
                btn.innerHTML = originalHtml;
            }, 2000);
        }
    }).catch(() => {
        textarea.select();
        document.execCommand('copy');
        alert("Structured JSON copied to clipboard!");
    });
}

function downloadJsonFile() {
    const textarea = document.getElementById('export-json-content');
    if (!textarea) return;
    const text = textarea.value;
    const blob = new Blob([text], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `standardized_export_${activeDocumentId || 'questions'}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// --- Answer Key Intelligence & Association Modal ---
async function openAnswerKeyModal() {
    if (!authToken) {
        openAuthModal(true);
        return;
    }

    if (!activeDocumentId) {
        if (userDocuments && userDocuments.length > 0) {
            selectActiveDocument(userDocuments[0]);
        } else {
            alert("Please select or upload an examination document first.");
            return;
        }
    }

    const modal = document.getElementById('associate-modal');
    if (!modal) return;

    // Set document title badge
    const badge = document.getElementById('ak-doc-title-badge');
    const activeDoc = userDocuments.find(d => d.id === activeDocumentId);
    if (badge) badge.innerText = activeDoc ? activeDoc.filename : 'Active Document';

    // Reset modal state before fetching
    const gridContainer = document.getElementById('ak-grid-container');
    const countBadge = document.getElementById('ak-detected-count');
    const confBadge = document.getElementById('ak-confidence-badge');
    const copyBtn = document.getElementById('btn-copy-ak');

    if (countBadge) countBadge.innerText = '0';
    if (confBadge) confBadge.innerHTML = `Detection Confidence: <strong style="color: var(--wb-text-muted);">Checking...</strong>`;
    if (copyBtn) copyBtn.disabled = true;

    // 1. Fetch detected answer key for active doc
    try {
        const token = (typeof localStorage !== 'undefined' ? localStorage.getItem('pragati_token') : null) || authToken;
        const res = await fetch(`/api/v1/documents/${activeDocumentId}/answer-key`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });

        if (res.status === 401) {
            handleUnauthorizedResponse();
            return;
        }

        if (res.ok) {
            const data = await res.json();
            const keys = data.answer_keys || {};
            const keyEntries = Object.entries(keys).sort((a, b) => {
                const numA = parseInt(a[0]) || 0;
                const numB = parseInt(b[0]) || 0;
                return numA - numB;
            });

            if (countBadge) countBadge.innerText = keyEntries.length;

            if (keyEntries.length === 0) {
                // No keys detected: show 0% and disable copy
                if (confBadge) {
                    confBadge.innerHTML = `Detection Confidence: <strong style="color: var(--wb-text-muted);">0% (No Keys Detected)</strong>`;
                }
                if (copyBtn) copyBtn.disabled = true;
                if (gridContainer) {
                    gridContainer.innerHTML = '<div style="grid-column: 1 / -1; padding: 20px; text-align: center; color: var(--wb-text-muted); font-size: 13px;">No embedded answer key detected in this document. You can link a separate answer key document from the "Link Separate Document" tab.</div>';
                }
            } else {
                const rawConf = typeof data.detection_confidence === 'number' ? data.detection_confidence : 0.0;
                const confPercent = Math.round(rawConf * 100);
                const confColor = confPercent >= 80 ? '#16a34a' : (confPercent >= 50 ? '#d97706' : '#dc2626');

                if (confBadge) {
                    confBadge.innerHTML = `Detection Confidence: <strong style="color: ${confColor};">${confPercent}%</strong>`;
                }
                if (copyBtn) copyBtn.disabled = false;
                if (gridContainer) {
                    gridContainer.innerHTML = keyEntries.map(([qNum, ans]) => `
                        <div style="display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; background: #fff; border: 1px solid var(--wb-border); border-radius: 4px; font-family: var(--font-mono);">
                            <span style="font-size: 12px; color: var(--wb-text-secondary); font-weight: 500;">Q${qNum}</span>
                            <span style="font-size: 12px; font-weight: 700; color: #ea580c; background: #fff7ed; padding: 1px 6px; border-radius: 3px; border: 1px solid #ffedd5;">${escapeHtml(ans)}</span>
                        </div>
                    `).join('');
                }
            }
        } else {
            if (confBadge) confBadge.innerHTML = `Detection Confidence: <strong style="color: var(--wb-text-muted);">0%</strong>`;
        }
    } catch (e) {
        console.warn("Answer key fetch error:", e);
        if (confBadge) confBadge.innerHTML = `Detection Confidence: <strong style="color: var(--wb-text-muted);">0%</strong>`;
    }

    // 2. Populate candidate documents for linking
    const select = document.getElementById('associate-key-doc-select');
    const emptyNote = document.getElementById('ak-link-empty-note');
    const btnAssociate = document.getElementById('btn-associate-now');

    if (select) {
        select.innerHTML = '';
        const candidates = userDocuments.filter(d => d.id !== activeDocumentId);
        if (candidates.length === 0) {
            if (emptyNote) emptyNote.style.display = 'block';
            if (select) select.style.display = 'none';
            if (btnAssociate) btnAssociate.disabled = true;
        } else {
            if (emptyNote) emptyNote.style.display = 'none';
            if (select) select.style.display = 'block';
            if (btnAssociate) btnAssociate.disabled = false;
            candidates.forEach(doc => {
                const opt = document.createElement('option');
                opt.value = doc.id;
                opt.innerText = `${doc.filename} (${doc.role})`;
                select.appendChild(opt);
            });
        }
    }

    // Default to detected answers tab
    switchAkTab('detected');
    modal.classList.add('open');
}

function switchAkTab(tab) {
    const tabDetected = document.getElementById('ak-tab-detected');
    const tabLink = document.getElementById('ak-tab-link');
    const panelDetected = document.getElementById('ak-panel-detected');
    const panelLink = document.getElementById('ak-panel-link');

    if (tab === 'detected') {
        if (tabDetected) {
            tabDetected.style.borderBottomColor = 'var(--wb-primary)';
            tabDetected.style.color = 'var(--wb-primary)';
            tabDetected.style.fontWeight = '600';
        }
        if (tabLink) {
            tabLink.style.borderBottomColor = 'transparent';
            tabLink.style.color = 'var(--wb-text-secondary)';
            tabLink.style.fontWeight = '500';
        }
        if (panelDetected) panelDetected.style.display = 'block';
        if (panelLink) panelLink.style.display = 'none';
    } else {
        if (tabLink) {
            tabLink.style.borderBottomColor = 'var(--wb-primary)';
            tabLink.style.color = 'var(--wb-primary)';
            tabLink.style.fontWeight = '600';
        }
        if (tabDetected) {
            tabDetected.style.borderBottomColor = 'transparent';
            tabDetected.style.color = 'var(--wb-text-secondary)';
            tabDetected.style.fontWeight = '500';
        }
        if (panelLink) panelLink.style.display = 'block';
        if (panelDetected) panelDetected.style.display = 'none';
    }
}

function copyAnswerKeyText() {
    const items = document.querySelectorAll('#ak-grid-container > div');
    if (!items || items.length === 0) {
        alert("No answer keys to copy.");
        return;
    }
    const lines = [];
    items.forEach(el => {
        lines.push(el.innerText.replace('\n', ': ').trim());
    });
    navigator.clipboard.writeText(lines.join('\n')).then(() => {
        alert("Answer keys copied to clipboard!");
    }).catch(() => {
        alert("Answer keys copied!");
    });
}

function closeAssociateModal() {
    const modal = document.getElementById('associate-modal');
    if (modal) modal.classList.remove('open');
}

async function submitAnswerKeyAssociation() {
    if (!authToken) {
        openAuthModal(true);
        return;
    }
    const keyDocSelect = document.getElementById('associate-key-doc-select');
    if (!keyDocSelect || !keyDocSelect.value) {
        alert("Please select an answer key document from the list.");
        return;
    }
    const keyDocId = keyDocSelect.value;
    try {
        const token = (typeof localStorage !== 'undefined' ? localStorage.getItem('pragati_token') : null) || authToken;
        const res = await fetch(`/api/v1/documents/${activeDocumentId}/associate-answer-key`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ answer_key_document_id: keyDocId })
        });
        if (res.status === 401) {
            handleUnauthorizedResponse();
            return;
        }
        if (res.ok) {
            const result = await res.json();
            alert(result.message);
            closeAssociateModal();
            await loadQuestionsForActiveDoc();
        } else {
            const err = await res.json().catch(() => ({}));
            alert(`Association Failed: ${err.detail || 'Unknown error'}`);
        }
    } catch (e) {
        alert("Association error: " + e.message);
    }
}

// --- Smooth Refresh All Handler ---
async function handleRefreshAll() {
    if (!authToken) {
        openAuthModal(true);
        return;
    }
    const btnText = document.getElementById('refresh-btn-text');
    const icon = document.getElementById('refresh-icon');

    if (icon) {
        icon.style.transition = 'transform 0.6s ease';
        icon.style.transform = 'rotate(360deg)';
    }

    try {
        await loadDocumentsList();
        if (activeDocumentId) {
            await loadQuestionsForActiveDoc();
        }
        if (btnText) {
            btnText.innerHTML = '<span style="color: #16a34a; font-weight: 600;">✓ Updated</span>';
            setTimeout(() => {
                btnText.innerText = 'Refresh';
                if (icon) {
                    icon.style.transition = 'none';
                    icon.style.transform = 'none';
                }
            }, 900);
        }
    } catch (e) {
        console.warn("Refresh error:", e);
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
window.handleLogout = handleLogout;
window.checkAuthenticationState = checkAuthenticationState;
window.loadDemoEvaluatorCredentials = loadDemoEvaluatorCredentials;
window.openAnswerKeyModal = openAnswerKeyModal;
window.openAssociateModal = openAnswerKeyModal;
window.closeAssociateModal = closeAssociateModal;
window.switchAkTab = switchAkTab;
window.copyAnswerKeyText = copyAnswerKeyText;
window.submitAnswerKeyAssociation = submitAnswerKeyAssociation;
window.handleRefreshAll = handleRefreshAll;
window.exportStructuredJson = exportStructuredJson;
window.closeExportModal = closeExportModal;
window.copyJsonToClipboard = copyJsonToClipboard;
window.downloadJsonFile = downloadJsonFile;
window.switchFilterTab = switchFilterTab;
window.approveQuestion = approveQuestion;
window.loadQuestionsForActiveDoc = loadQuestionsForActiveDoc;
window.uploadSelectedFile = uploadSelectedFile;
window.handleFileSelected = handleFileSelected;

