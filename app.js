/**
 * DS LAB – Data Science Laboratory Portal
 * Frontend Interaction Script
 */

(function () {
  'use strict';

  // State
  let allExperiments = [];
  let deleteTargetExpId = null;
  let activeModal = null;

  // DOM Elements - Student ID Card
  const idCardPhoto = document.getElementById('idCardPhoto');
  const idCardName = document.getElementById('idCardName');
  const idCardRoll = document.getElementById('idCardRoll');
  const idCardSection = document.getElementById('idCardSection');
  const idCardBranch = document.getElementById('idCardBranch');
  const idCardProf = document.getElementById('idCardProf');
  const idCardGithub = document.getElementById('idCardGithub');
  const openEditProfileBtn = document.getElementById('openEditProfileBtn');

  // DOM Elements - Edit Profile Modal
  const editProfileModal = document.getElementById('editProfileModal');
  const editProfileForm = document.getElementById('editProfileForm');
  const editPhotoInput = document.getElementById('editPhotoInput');
  const editPhotoPreview = document.getElementById('editPhotoPreview');
  const choosePhotoBtn = document.getElementById('choosePhotoBtn');
  const editNameInput = document.getElementById('editNameInput');
  const editRollInput = document.getElementById('editRollInput');
  const editSectionInput = document.getElementById('editSectionInput');
  const editBranchInput = document.getElementById('editBranchInput');
  const editProfInput = document.getElementById('editProfInput');
  const editGithubInput = document.getElementById('editGithubInput');
  const saveProfileBtn = document.getElementById('saveProfileBtn');

  // DOM Elements - Experiments List & Toolbar
  const experimentsGrid = document.getElementById('experimentsGrid');
  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const experimentCountText = document.getElementById('experimentCountText');
  const emptyState = document.getElementById('emptyState');
  const emptyStateTitle = document.getElementById('emptyStateTitle');
  const emptyStateText = document.getElementById('emptyStateText');
  const openAddModalBtn = document.getElementById('openAddModalBtn');

  // DOM Elements - Add Experiment Modal
  const addExperimentModal = document.getElementById('addExperimentModal');
  const addExperimentForm = document.getElementById('addExperimentForm');
  const expNumberInput = document.getElementById('expNumberInput');
  const expTitleInput = document.getElementById('expTitleInput');
  const expShortDesc = document.getElementById('expShortDesc');
  const expD2Heading = document.getElementById('expD2Heading');
  const expLongContent = document.getElementById('expLongContent');
  const expGithubInput = document.getElementById('expGithubInput');
  const submitExpBtn = document.getElementById('submitExpBtn');

  // Cover Image upload elements
  const coverUploadZone = document.getElementById('coverUploadZone');
  const coverImageInput = document.getElementById('coverImageInput');
  const coverPreviewWrap = document.getElementById('coverPreviewWrap');
  const coverPreviewImg = document.getElementById('coverPreviewImg');
  const coverPrompt = document.getElementById('coverPrompt');
  const removeCoverBtn = document.getElementById('removeCoverBtn');

  // Video upload elements
  const expVideoInput = document.getElementById('expVideoInput');
  const chooseVideoBtn = document.getElementById('chooseVideoBtn');
  const videoFileBadge = document.getElementById('videoFileBadge');
  const videoFileName = document.getElementById('videoFileName');
  const removeVideoBtn = document.getElementById('removeVideoBtn');

  // DOM Elements - Read More / Details Modal
  const detailsModal = document.getElementById('detailsModal');
  const detailsExpBadge = document.getElementById('detailsExpBadge');
  const detailsExpTitle = document.getElementById('detailsExpTitle');
  const detailsCoverWrap = document.getElementById('detailsCoverWrap');
  const detailsCoverImg = document.getElementById('detailsCoverImg');
  const detailsShortDescText = document.getElementById('detailsShortDescText');
  const detailsD2Heading = document.getElementById('detailsD2Heading');
  const detailsLongContent = document.getElementById('detailsLongContent');
  const detailsVideoWrap = document.getElementById('detailsVideoWrap');
  const detailsVideoPlayer = document.getElementById('detailsVideoPlayer');
  const detailsGithubWrap = document.getElementById('detailsGithubWrap');
  const detailsGithubLink = document.getElementById('detailsGithubLink');

  // DOM Elements - Delete Confirmation Modal
  const deleteConfirmModal = document.getElementById('deleteConfirmModal');
  const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

  // Toast
  const toastNotification = document.getElementById('toastNotification');
  let toastTimer = null;

  /* ==========================================================================
     Toast Notification System
     ========================================================================== */
  function showToast(message, type = 'success') {
    if (toastTimer) clearTimeout(toastTimer);
    toastNotification.textContent = message;
    toastNotification.className = `toast toast--${type}`;
    toastNotification.hidden = false;

    toastTimer = setTimeout(() => {
      toastNotification.hidden = true;
    }, 3800);
  }

  /* ==========================================================================
     Modal Helpers
     ========================================================================== */
  function openModal(modalEl) {
    if (activeModal && activeModal !== modalEl) {
      closeModal(activeModal);
    }
    modalEl.hidden = false;
    document.body.style.overflow = 'hidden';
    activeModal = modalEl;
  }

  function closeModal(modalEl) {
    if (!modalEl) return;
    modalEl.hidden = true;
    document.body.style.overflow = '';
    if (activeModal === modalEl) activeModal = null;

    // Pause video player if details modal is closed
    if (modalEl === detailsModal && detailsVideoPlayer) {
      detailsVideoPlayer.pause();
    }
  }

  // Global close listener for backdrop and [data-close] buttons
  document.addEventListener('click', (e) => {
    if (e.target.matches('[data-close]') || e.target.closest('[data-close]')) {
      const parentModal = e.target.closest('.modal');
      if (parentModal) closeModal(parentModal);
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && activeModal) {
      closeModal(activeModal);
    }
  });

  /* ==========================================================================
     Student Profile Management
     ========================================================================== */
  async function loadStudentProfile() {
    try {
      const res = await fetch('/api/student');
      const data = await res.json();
      if (data.success && data.student) {
        renderStudentProfile(data.student);
      }
    } catch (err) {
      console.error('Failed to load student profile:', err);
    }
  }

  function renderStudentProfile(student) {
    idCardName.textContent = student.name || 'Student Name';
    idCardRoll.textContent = student.roll_no || 'Not added';
    idCardSection.textContent = student.section || 'Not added';
    idCardBranch.textContent = student.branch || 'Not added';
    idCardProf.textContent = student.assistant_professor || 'Not added';

    // Student Photo
    if (student.photo_url && student.photo_url.trim() !== '') {
      idCardPhoto.src = student.photo_url;
    } else {
      idCardPhoto.src = '/static/uploads/images/default_avatar.png';
    }

    // GitHub Repo
    if (student.github_url && student.github_url.trim() !== '') {
      const cleanUrl = student.github_url.trim();
      const repoName = cleanUrl.replace(/^https?:\/\/github\.com\//i, '').replace(/\/$/, '') || 'GitHub Repo';
      idCardGithub.innerHTML = `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer">${escapeHtml(repoName)}</a>`;
    } else {
      idCardGithub.innerHTML = '<span class="is-empty">Not added</span>';
    }
  }

  // Edit Profile Modal Open
  openEditProfileBtn.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/student');
      const data = await res.json();
      if (data.success && data.student) {
        const s = data.student;
        editNameInput.value = s.name || '';
        editRollInput.value = s.roll_no || '';
        editSectionInput.value = s.section || '';
        editBranchInput.value = s.branch || '';
        editProfInput.value = s.assistant_professor || '';
        editGithubInput.value = s.github_url || '';
        editPhotoPreview.src = s.photo_url && s.photo_url.trim() !== '' ? s.photo_url : '/static/uploads/images/default_avatar.png';
        editPhotoInput.value = '';
        clearErrors(editProfileForm);
        openModal(editProfileModal);
      }
    } catch (err) {
      showToast('Could not load profile details', 'error');
    }
  });

  // Choose photo button trigger
  choosePhotoBtn.addEventListener('click', () => editPhotoInput.click());

  editPhotoInput.addEventListener('change', () => {
    const file = editPhotoInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        editPhotoPreview.src = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  });

  // Save Profile Form Submission
  editProfileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearErrors(editProfileForm);

    const name = editNameInput.value.trim();
    const roll = editRollInput.value.trim();

    let hasError = false;
    if (!name) {
      setError(editProfileForm, 'name', 'Please enter student name.');
      hasError = true;
    }
    if (!roll) {
      setError(editProfileForm, 'roll_no', 'Please enter roll number.');
      hasError = true;
    }
    if (hasError) return;

    setBtnLoading(saveProfileBtn, true);

    const formData = new FormData(editProfileForm);
    try {
      const res = await fetch('/api/student', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        renderStudentProfile(data.student);
        closeModal(editProfileModal);
        showToast('Student ID card updated successfully!');
      } else {
        showToast(data.error || 'Failed to update ID card.', 'error');
      }
    } catch (err) {
      showToast('Error updating ID card: ' + err.message, 'error');
    } finally {
      setBtnLoading(saveProfileBtn, false);
    }
  });

  /* ==========================================================================
     Experiments Management
     ========================================================================== */
  async function loadExperiments() {
    try {
      const res = await fetch('/api/experiments');
      const data = await res.json();
      if (data.success) {
        allExperiments = data.experiments || [];
        filterAndRenderExperiments();
      }
    } catch (err) {
      console.error('Failed to load experiments:', err);
      experimentCountText.textContent = 'Error loading experiments';
    }
  }

  function filterAndRenderExperiments() {
    const query = searchInput.value.trim().toLowerCase();
    
    // Toggle clear search button
    clearSearchBtn.hidden = query.length === 0;

    const filtered = allExperiments.filter((exp) => {
      if (!query) return true;
      const expNo = String(exp.experiment_no || '').toLowerCase();
      const title = String(exp.title || '').toLowerCase();
      const desc = String(exp.short_description || '').toLowerCase();
      return expNo.includes(query) || title.includes(query) || desc.includes(query);
    });

    renderExperiments(filtered, query);
  }

  function renderExperiments(list, query) {
    experimentsGrid.innerHTML = '';

    if (allExperiments.length === 0) {
      emptyState.hidden = false;
      emptyStateTitle.textContent = 'No experiments added yet.';
      emptyStateText.innerHTML = 'Click <strong>+ Add</strong> to add your first DS Lab experiment.';
      experimentCountText.textContent = '0 experiments';
      return;
    }

    if (list.length === 0) {
      emptyState.hidden = false;
      emptyStateTitle.textContent = 'No matching experiments found.';
      emptyStateText.textContent = `No results found for "${query}". Try searching by experiment number or topic.`;
      experimentCountText.textContent = '0 of ' + allExperiments.length + ' experiments';
      return;
    }

    emptyState.hidden = true;
    experimentCountText.textContent = `${list.length} ${list.length === 1 ? 'experiment' : 'experiments'}`;

    const fragment = document.createDocumentFragment();
    list.forEach((exp) => {
      const card = createExperimentCard(exp);
      fragment.appendChild(card);
    });
    experimentsGrid.appendChild(fragment);
  }

  function createExperimentCard(exp) {
    const card = document.createElement('article');
    card.className = 'exp-card';
    card.dataset.id = exp.id;

    const coverUrl = exp.cover_url || '/static/uploads/images/sample_eda_cover.png';
    const hasGithub = exp.github_url && exp.github_url.trim() !== '';

    card.innerHTML = `
      <div class="exp-card__cover">
        <img src="${escapeHtml(coverUrl)}" alt="${escapeHtml(exp.title)}" loading="lazy">
        <span class="exp-card__badge">Exp ${escapeHtml(exp.experiment_no)}</span>
      </div>
      <div class="exp-card__body">
        <h3 class="exp-card__title">${escapeHtml(exp.title)}</h3>
        <p class="exp-card__desc">${escapeHtml(exp.short_description)}</p>
      </div>
      <div class="exp-card__footer">
        <div class="exp-card__actions-left">
          <button type="button" class="btn btn--primary btn--small btn-readmore" data-id="${exp.id}">Read More</button>
          ${hasGithub ? `
            <a href="${escapeHtml(exp.github_url)}" target="_blank" rel="noopener noreferrer" class="btn btn--ghost btn--small btn--gh" title="GitHub Repository">
              <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.6 7.6 0 0 1 4 0c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>
              GitHub
            </a>
          ` : ''}
        </div>
        <div class="exp-card__actions-right">
          <button type="button" class="btn--icon-danger btn-delete" data-id="${exp.id}" title="Delete Experiment" aria-label="Delete Experiment">
            <svg viewBox="0 0 24 24" width="17" height="17" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              <line x1="10" y1="11" x2="10" y2="17"></line>
              <line x1="14" y1="11" x2="14" y2="17"></line>
            </svg>
          </button>
        </div>
      </div>
    `;

    // Attach event listeners
    const readMoreBtn = card.querySelector('.btn-readmore');
    readMoreBtn.addEventListener('click', () => openExperimentDetails(exp.id));

    const deleteBtn = card.querySelector('.btn-delete');
    deleteBtn.addEventListener('click', () => openDeleteConfirm(exp.id));

    return card;
  }

  // Instant Search
  searchInput.addEventListener('input', () => {
    filterAndRenderExperiments();
  });

  clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    filterAndRenderExperiments();
    searchInput.focus();
  });

  /* ==========================================================================
     Add Experiment Modal & File Uploads
     ========================================================================== */
  openAddModalBtn.addEventListener('click', () => {
    addExperimentForm.reset();
    clearErrors(addExperimentForm);
    resetCoverUpload();
    resetVideoUpload();

    // Auto suggest next experiment number
    if (allExperiments.length > 0) {
      const numbers = allExperiments
        .map((e) => parseInt(e.experiment_no, 10))
        .filter((n) => !isNaN(n));
      const nextNum = numbers.length > 0 ? Math.max(...numbers) + 1 : 1;
      expNumberInput.value = nextNum;
    } else {
      expNumberInput.value = '1';
    }

    openModal(addExperimentModal);
    expTitleInput.focus();
  });

  // Cover Image Handling
  coverUploadZone.addEventListener('click', (e) => {
    if (e.target !== removeCoverBtn && !e.target.closest('#removeCoverBtn')) {
      coverImageInput.click();
    }
  });

  coverImageInput.addEventListener('change', () => {
    const file = coverImageInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        coverPreviewImg.src = e.target.result;
        coverPreviewWrap.hidden = false;
        coverPrompt.hidden = true;
      };
      reader.readAsDataURL(file);
    }
  });

  removeCoverBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    resetCoverUpload();
  });

  function resetCoverUpload() {
    coverImageInput.value = '';
    coverPreviewImg.src = '';
    coverPreviewWrap.hidden = true;
    coverPrompt.hidden = false;
  }

  // Video Upload Handling
  chooseVideoBtn.addEventListener('click', () => expVideoInput.click());

  expVideoInput.addEventListener('change', () => {
    const file = expVideoInput.files[0];
    if (file) {
      videoFileName.textContent = file.name;
      videoFileBadge.hidden = false;
      chooseVideoBtn.hidden = true;
    }
  });

  removeVideoBtn.addEventListener('click', () => {
    resetVideoUpload();
  });

  function resetVideoUpload() {
    expVideoInput.value = '';
    videoFileName.textContent = '';
    videoFileBadge.hidden = true;
    chooseVideoBtn.hidden = false;
  }

  // Form Submission: Add Experiment
  addExperimentForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearErrors(addExperimentForm);

    const expNo = expNumberInput.value.trim();
    const title = expTitleInput.value.trim();
    const shortDesc = expShortDesc.value.trim();
    const longContent = expLongContent.value.trim();

    let hasError = false;
    if (!expNo) {
      setError(addExperimentForm, 'experiment_no', 'Experiment number is required.');
      hasError = true;
    }
    if (!title) {
      setError(addExperimentForm, 'title', 'Experiment name is required.');
      hasError = true;
    }
    if (!shortDesc) {
      setError(addExperimentForm, 'short_description', 'Short description (D1) is required.');
      hasError = true;
    }
    if (!longContent) {
      setError(addExperimentForm, 'long_content', 'Full experiment content is required.');
      hasError = true;
    }

    if (hasError) return;

    setBtnLoading(submitExpBtn, true);

    const formData = new FormData(addExperimentForm);
    try {
      const res = await fetch('/api/experiments', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();

      if (data.success && data.experiment) {
        allExperiments.push(data.experiment);
        // Sort experiments
        allExperiments.sort((a, b) => {
          const numA = parseInt(a.experiment_no, 10) || 999;
          const numB = parseInt(b.experiment_no, 10) || 999;
          return numA - numB;
        });
        filterAndRenderExperiments();
        closeModal(addExperimentModal);
        showToast('Experiment added successfully!');
      } else {
        showToast(data.error || 'Failed to add experiment.', 'error');
      }
    } catch (err) {
      showToast('Error uploading experiment: ' + err.message, 'error');
    } finally {
      setBtnLoading(submitExpBtn, false);
    }
  });

  /* ==========================================================================
     Read More / Experiment Details Modal
     ========================================================================== */
  async function openExperimentDetails(expId) {
    try {
      const exp = allExperiments.find((item) => item.id === expId);
      if (!exp) return;

      detailsExpBadge.textContent = `Experiment ${exp.experiment_no}`;
      detailsExpTitle.textContent = exp.title;
      detailsShortDescText.textContent = exp.short_description;
      detailsD2Heading.textContent = exp.d2_heading || 'Long Description';

      // Format long content cleanly into styled sections
      detailsLongContent.innerHTML = formatLongContent(exp.long_content);

      // Cover image
      const coverUrl = exp.cover_url || '/static/uploads/images/sample_eda_cover.png';
      detailsCoverImg.src = coverUrl;

      // Video section
      if (exp.video_url && exp.video_url.trim() !== '') {
        detailsVideoPlayer.src = exp.video_url;
        detailsVideoWrap.hidden = false;
      } else {
        detailsVideoPlayer.pause();
        detailsVideoPlayer.removeAttribute('src');
        detailsVideoWrap.hidden = true;
      }

      // GitHub link
      if (exp.github_url && exp.github_url.trim() !== '') {
        detailsGithubLink.href = exp.github_url;
        detailsGithubWrap.hidden = false;
      } else {
        detailsGithubWrap.hidden = true;
      }

      openModal(detailsModal);
    } catch (err) {
      console.error('Error displaying experiment details:', err);
      showToast('Failed to display experiment details.', 'error');
    }
  }

  function formatLongContent(text) {
    if (!text) return '<p>No content provided.</p>';
    const lines = text.split('\n');
    let html = '';
    let currentParagraph = '';

    const sectionRegex = /^(AIM|OBJECTIVE|PROCEDURE|ALGORITHM|METHODOLOGY|OBSERVATIONS|OBSERVATION|RESULTS|RESULT|OUTPUT|CONCLUSION|CODE|DISCUSSION|INFERENCES):?/i;

    lines.forEach((rawLine) => {
      const line = rawLine.trim();
      if (!line) {
        if (currentParagraph) {
          html += `<p class="exp-paragraph">${escapeHtml(currentParagraph)}</p>`;
          currentParagraph = '';
        }
        return;
      }

      const match = line.match(sectionRegex);
      if (match) {
        if (currentParagraph) {
          html += `<p class="exp-paragraph">${escapeHtml(currentParagraph)}</p>`;
          currentParagraph = '';
        }
        const sectionTitle = line.replace(/:$/, '');
        html += `<div class="exp-section-header">${escapeHtml(sectionTitle)}</div>`;
      } else {
        if (currentParagraph) {
          currentParagraph += '\n' + line;
        } else {
          currentParagraph = line;
        }
      }
    });

    if (currentParagraph) {
      html += `<p class="exp-paragraph">${escapeHtml(currentParagraph)}</p>`;
    }

    return html;
  }

  /* ==========================================================================
     Delete Experiment Flow
     ========================================================================== */
  function openDeleteConfirm(expId) {
    deleteTargetExpId = expId;
    openModal(deleteConfirmModal);
  }

  confirmDeleteBtn.addEventListener('click', async () => {
    if (!deleteTargetExpId) return;

    setBtnLoading(confirmDeleteBtn, true);
    try {
      const res = await fetch(`/api/experiments/${deleteTargetExpId}`, {
        method: 'DELETE'
      });
      const data = await res.json();

      if (data.success) {
        allExperiments = allExperiments.filter((e) => e.id !== deleteTargetExpId);
        filterAndRenderExperiments();
        closeModal(deleteConfirmModal);
        showToast('Experiment deleted successfully!');
      } else {
        showToast(data.error || 'Failed to delete experiment.', 'error');
      }
    } catch (err) {
      showToast('Error deleting experiment: ' + err.message, 'error');
    } finally {
      setBtnLoading(confirmDeleteBtn, false);
      deleteTargetExpId = null;
    }
  });

  /* ==========================================================================
     Utility Functions
     ========================================================================== */
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function setError(form, fieldName, msg) {
    const errorEl = form.querySelector(`[data-error="${fieldName}"]`);
    if (errorEl) errorEl.textContent = msg;
  }

  function clearErrors(form) {
    form.querySelectorAll('.error-msg').forEach((el) => (el.textContent = ''));
  }

  function setBtnLoading(btn, isLoading) {
    const textSpan = btn.querySelector('.btn-text');
    const spinner = btn.querySelector('.btn-spinner');
    if (isLoading) {
      btn.disabled = true;
      if (textSpan) textSpan.style.opacity = '0.5';
      if (spinner) spinner.hidden = false;
    } else {
      btn.disabled = false;
      if (textSpan) textSpan.style.opacity = '1';
      if (spinner) spinner.hidden = true;
    }
  }

  /* ==========================================================================
     Initial Page Load
     ========================================================================== */
  window.addEventListener('DOMContentLoaded', () => {
    loadStudentProfile();
    loadExperiments();
  });

})();
