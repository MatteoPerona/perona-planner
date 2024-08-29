// Toggle visibility of tasks and rotate arrow
function toggleTasks(element) {
    const tasksContainer = element.nextElementSibling;
    const arrow = element.querySelector('.arrow');
    const isHidden = tasksContainer.style.display === "none" || tasksContainer.style.display === "";
    tasksContainer.style.display = isHidden ? "block" : "none";
    arrow.classList.toggle('down', isHidden);
}

// Toggle visibility of edit form
function toggleEditForm(formId) {
    const form = document.getElementById(formId);
    form.style.display = form.style.display === "none" ? "block" : "none";
}

// Toggle visibility of add form and associated button
function toggleAddForm(formId, btnId) {
    [formId, btnId].forEach(id => {
        const element = document.getElementById(id);
        element.style.display = element.style.display === "none" ? "block" : "none";
    });
}

// Update task completion status via API
function updateTaskCompletion(taskId, checkboxElement) {
    fetch(`/task_completion/${taskId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'task_completed': checkboxElement.checked })
    })
    .then(response => {
        if (!response.ok) {
            console.log('Failed to update');
            checkboxElement.checked = !checkboxElement.checked;
        }
    })
    .catch(error => console.error('Error:', error));
}