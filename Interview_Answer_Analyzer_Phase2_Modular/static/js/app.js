const form = document.getElementById('answer-form');
const questionInput = document.getElementById('question');
const answerInput = document.getElementById('answer');
const wordCount = document.getElementById('word-count');
const toast = document.getElementById('toast');
let toastTimer;

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2600);
}
function countWords(text) { return text.trim() ? text.trim().split(/\s+/).length : 0; }
answerInput.addEventListener('input', () => { wordCount.textContent = `${countWords(answerInput.value)} words`; });

document.getElementById('reset-btn').addEventListener('click', () => {
  questionInput.value = ''; answerInput.value = ''; wordCount.textContent = '0 words'; questionInput.focus();
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true; button.textContent = 'Analyzing...';
  try {
    const response = await fetch('/api/analyze', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question:questionInput.value, answer:answerInput.value})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Could not analyze this answer.');
    displayResult(data); await loadHistory(); showToast('Answer analyzed and saved.');
  } catch (error) { showToast(error.message); }
  finally { button.disabled = false; button.innerHTML = 'Analyze answer <span>↗</span>'; }
});

function displayResult(data) {
  document.getElementById('empty-state').classList.add('hidden');
  document.getElementById('result-content').classList.remove('hidden');
  document.getElementById('score-value').textContent = data.score;
  document.getElementById('result-words').textContent = data.word_count;
  document.getElementById('feedback-count').textContent = data.feedback.length;
  document.getElementById('score-label').textContent = data.score >= 80 ? 'Strong starting point' : data.score >= 55 ? 'Good progress' : 'Keep practising';
  document.getElementById('score-summary').textContent = data.score >= 80 ? 'Your answer meets several of the basic checks.' : 'Use the suggestions below to strengthen your response.';
  const list = document.getElementById('feedback-list'); list.innerHTML = '';
  data.feedback.forEach(item => { const li = document.createElement('li'); li.textContent = item; list.appendChild(li); });
}

async function loadHistory() {
  const container = document.getElementById('history-list');
  try {
    const response = await fetch('/api/history'); const items = await response.json();
    container.innerHTML = '';
    if (!items.length) { container.innerHTML = '<p class="muted">No saved attempts yet. Your analyzed answers will appear here.</p>'; return; }
    items.forEach(item => {
      const card = document.createElement('article'); card.className = 'history-card';
      const top = document.createElement('div'); top.className = 'history-card-top';
      const title = document.createElement('h3'); title.textContent = item.question;
      const score = document.createElement('span'); score.className = 'history-score'; score.textContent = `${item.score}/100`;
      top.append(title, score);
      const answer = document.createElement('p'); answer.textContent = item.answer.length > 150 ? item.answer.slice(0,150) + '…' : item.answer;
      const meta = document.createElement('div'); meta.className = 'history-meta'; meta.textContent = item.created_at;
      card.append(top, answer, meta); container.appendChild(card);
    });
  } catch { container.innerHTML = '<p class="muted">Could not load history. Check that the Flask server is running.</p>'; }
}

document.getElementById('refresh-btn').addEventListener('click', loadHistory);
document.getElementById('undo-btn').addEventListener('click', async () => {
  try { const response = await fetch('/api/undo', {method:'POST'}); const data = await response.json(); if (!response.ok) throw new Error(data.message); await loadHistory(); showToast(data.message); }
  catch (error) { showToast(error.message || 'Undo failed.'); }
});
document.getElementById('clear-history-btn').addEventListener('click', async () => {
  if (!confirm('Clear all saved answer history? This cannot be undone.')) return;
  try { const response = await fetch('/api/clear-history', {method:'POST'}); const data = await response.json(); await loadHistory(); showToast(data.message); }
  catch { showToast('Could not clear history.'); }
});
loadHistory();

// ---------------- Professor appointment booking ----------------
const bookingForm = document.getElementById('booking-form');
const bookingMessage = document.getElementById('booking-message');
const professorSelect = document.getElementById('professor-select');
const appointmentsList = document.getElementById('appointments-list');
const dateInput = document.getElementById('interview-date');

// Prevent choosing a date earlier than today.
const localToday = new Date();
const todayString = `${localToday.getFullYear()}-${String(localToday.getMonth() + 1).padStart(2, '0')}-${String(localToday.getDate()).padStart(2, '0')}`;
dateInput.min = todayString;

function showBookingMessage(message, isError = false) {
  bookingMessage.textContent = message;
  bookingMessage.classList.toggle('error', isError);
}

async function loadProfessors() {
  try {
    const response = await fetch('/api/professors');
    const professors = await response.json();
    professorSelect.innerHTML = '<option value="">Select a professor</option>';
    professors.forEach(professor => {
      const option = document.createElement('option');
      option.value = professor.id;
      option.textContent = `${professor.name} — ${professor.specialization}`;
      professorSelect.appendChild(option);
    });
  } catch {
    professorSelect.innerHTML = '<option value="">Could not load professors</option>';
  }
}

bookingForm.addEventListener('submit', async event => {
  event.preventDefault();
  const booking = {
    student_name: document.getElementById('student-name').value.trim(),
    student_email: document.getElementById('student-email').value.trim(),
    professor_id: professorSelect.value,
    interview_date: dateInput.value,
    interview_time: document.getElementById('interview-time').value,
    purpose: document.getElementById('interview-purpose').value.trim()
  };
  try {
    const response = await fetch('/api/appointments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(booking)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Could not book the interview.');
    showBookingMessage(`${data.message} Meeting link: ${data.meeting_link}`);
    bookingForm.reset();
    dateInput.min = todayString;
    await loadAppointments();
  } catch (error) {
    showBookingMessage(error.message, true);
  }
});

async function loadAppointments() {
  try {
    const response = await fetch('/api/appointments');
    const appointments = await response.json();
    appointmentsList.innerHTML = '';
    if (!appointments.length) {
      appointmentsList.innerHTML = '<p class="muted">No appointments yet. Submit the booking form to add one.</p>';
      return;
    }
    appointments.forEach(appointment => {
      const card = document.createElement('article');
      card.className = 'appointment-card';
      const top = document.createElement('div');
      top.className = 'appointment-top';
      const heading = document.createElement('div');
      const title = document.createElement('h3');
      title.textContent = `${appointment.student_name} with ${appointment.professor_name}`;
      const date = document.createElement('p');
      date.textContent = `${appointment.interview_date} at ${appointment.interview_time}`;
      heading.append(title, date);
      const status = document.createElement('span');
      status.className = `appointment-status ${appointment.status.toLowerCase()}`;
      status.textContent = appointment.status;
      top.append(heading, status);
      const purpose = document.createElement('p');
      purpose.textContent = `Purpose: ${appointment.purpose}`;
      const email = document.createElement('p');
      email.textContent = `Student email: ${appointment.student_email}`;
      card.append(top, purpose, email);

      if (appointment.status === 'Accepted' || appointment.status === 'Completed') {
        const link = document.createElement('a');
        link.href = appointment.meeting_link;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = 'Join video meeting ↗';
        const actions = document.createElement('div');
        actions.className = 'appointment-actions';
        actions.appendChild(link);
        card.appendChild(actions);
      }

      // These controls simulate the professor side in this classroom demo.
      const actions = document.createElement('div');
      actions.className = 'appointment-actions';
      if (appointment.status === 'Pending') {
        actions.append(
          makeActionButton('Accept request', 'approve-btn', () => updateAppointmentStatus(appointment.id, 'Accepted')),
          makeActionButton('Reject request', 'reject-btn', () => updateAppointmentStatus(appointment.id, 'Rejected'))
        );
      }
      if (appointment.status === 'Accepted' || appointment.status === 'Completed') {
        const feedback = document.createElement('textarea');
        feedback.className = 'appointment-feedback';
        feedback.placeholder = 'Professor feedback: strengths and suggestions';
        feedback.value = appointment.professor_feedback || '';
        feedback.setAttribute('aria-label', `Feedback for appointment ${appointment.id}`);
        const save = makeActionButton('Save feedback', 'approve-btn feedback-save', () => saveAppointmentFeedback(appointment.id, feedback.value));
        actions.append(feedback, save);
      }
      if (actions.children.length) card.appendChild(actions);
      appointmentsList.appendChild(card);
    });
  } catch {
    appointmentsList.innerHTML = '<p class="muted">Could not load appointments. Check that the Flask server is running.</p>';
  }
}

function makeActionButton(label, className, callback) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = className;
  button.textContent = label;
  button.addEventListener('click', callback);
  return button;
}

async function updateAppointmentStatus(id, status) {
  try {
    const response = await fetch(`/api/appointments/${id}/status`, {
      method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Could not update appointment.');
    showBookingMessage(data.message);
    await loadAppointments();
  } catch (error) {
    showBookingMessage(error.message, true);
  }
}

async function saveAppointmentFeedback(id, feedback) {
  try {
    const response = await fetch(`/api/appointments/${id}/feedback`, {
      method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ professor_feedback: feedback })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Could not save feedback.');
    showBookingMessage(data.message);
    await loadAppointments();
  } catch (error) {
    showBookingMessage(error.message, true);
  }
}

document.getElementById('refresh-appointments').addEventListener('click', loadAppointments);
loadProfessors();
loadAppointments();
