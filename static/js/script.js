// script.js
let currentSelection = null;

function selectSection(element, sectionTitle) {
    // Deselect if there is a current selection
    if (currentSelection) {
        currentSelection.classList.remove('selected');
    }

    // Select new item
    element.classList.add('selected');
    currentSelection = element;

    // Show the action buttons
    document.getElementById('action-buttons').style.display = 'block';
}

function performAction(action) {
    const sectionTitle = currentSelection.textContent;
    const pageName = document.getElementById('pageName').value;

    const form = document.createElement('form');
    form.method = 'post';
    form.action = `/${action}`;

    form.innerHTML = `
        <input type="hidden" name="page_name" value="${pageName}">
        <input type="hidden" name="section_title" value="${sectionTitle}">
    `;

    document.body.appendChild(form);
    form.submit();
}
