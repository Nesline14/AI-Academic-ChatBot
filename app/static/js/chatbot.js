/* CampusBot - Student AI Assistant Client */
document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('campusbot-toggle');
  const chatWindow = document.getElementById('campusbot-window');
  const closeBtn = document.getElementById('campusbot-close');
  const chatForm = document.getElementById('campusbot-form');
  const chatInput = document.getElementById('campusbot-input');
  const chatMessages = document.getElementById('campusbot-messages');

  if (!toggleBtn || !chatWindow) return;

  // Toggle Chat Window
  toggleBtn.addEventListener('click', () => {
    chatWindow.classList.toggle('open');
    if (chatWindow.classList.contains('open') && chatInput) {
      chatInput.focus();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      chatWindow.classList.remove('open');
    });
  }

  // Global helper for suggestion pills
  window.campusBotSend = function(text) {
    if (!text) return;
    if (chatInput) chatInput.value = text;
    if (chatForm) {
      chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
  };

  // Submit message
  if (chatForm) {
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const message = chatInput.value.trim();
      if (!message) return;

      // 1. Append User Message
      appendMessage(message, 'user');
      chatInput.value = '';

      // 2. Append Loading Indicator
      const loadingId = 'loading-' + Date.now();
      appendLoading(loadingId);

      try {
        const response = await fetch('/api/chatbot', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        removeLoading(loadingId);

        if (response.ok && data.response) {
          appendMessage(data.response, 'bot', true);
        } else {
          appendMessage(data.error || 'Sorry, I could not retrieve that right now. Please try again.', 'bot');
        }
      } catch (err) {
        removeLoading(loadingId);
        appendMessage('Network connection issue. Please verify your connection or try again.', 'bot');
      }
    });
  }

  function appendMessage(content, sender, isHtml = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${sender}`;
    if (isHtml) {
      msgDiv.innerHTML = content;
    } else {
      msgDiv.textContent = content;
    }
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function appendLoading(id) {
    const loadDiv = document.createElement('div');
    loadDiv.id = id;
    loadDiv.className = 'chat-msg bot small text-muted';
    loadDiv.innerHTML = '<i class="bi bi-three-dots"></i> CampusBot is thinking...';
    chatMessages.appendChild(loadDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function removeLoading(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }
});
