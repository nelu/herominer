// Helper function to preserve the original date format from server
function formatDateTime(dateStr) {
    if (!dateStr) return '';
    // Return the date string as-is, preserving the YYYY-MM-DD HH:MM:SS format
    return dateStr;
}

let tasks = {}

// Helper function to get Unix timestamp from date string for sorting
function getTimestamp(dateStr) {
    if (!dateStr) return 0;
    // Parse the YYYY-MM-DD HH:MM:SS format manually to avoid browser timezone conversion
    const [datePart, timePart] = dateStr.split(' ');
    if (!datePart || !timePart) return 0;

    const [year, month, day] = datePart.split('-').map(Number);
    const [hours, minutes, seconds] = timePart.split(':').map(val => parseFloat(val));

    // Create date object with UTC to avoid timezone issues (but only for sorting)
    return Date.UTC(year, month - 1, day, hours, minutes, seconds) / 1000;
}

// Helper function to create task details panel
function createTaskDetailsPanel(taskData) {
    // Use the template to create the panel
    const template = document.getElementById('task-details-template');
    const fragment = template.content.cloneNode(true);
    const panel = document.createElement('div');
    panel.classList.add('task-details-panel');
    panel.appendChild(fragment);

    // Update the panel with task data
    panel.querySelector('#task-id').textContent = taskData.id || '';
    panel.querySelector('#task-name').textContent = taskData.name || '';
    panel.querySelector('#task-interval').textContent = taskData.interval || '';

    panel.querySelector('#task-start').textContent = taskData.task_start || 'Never';
    panel.querySelector('#task-finish').textContent = taskData.task_finish || 'Never';
    panel.querySelector('#task-next-run').textContent = taskData.next_run || 'Not scheduled';
    panel.querySelector('#task-next-scheduled').textContent = taskData.task_nextrun || 'Not set';

    panel.querySelector('#task-result').textContent = JSON.stringify(taskData.task_result, null, 2) || 'No result data';

    // ⬇️ NEW FIELDS
    panel.querySelector('#task-after').textContent = taskData.after || '—';
    panel.querySelector('#task-before').textContent = taskData.before || '—';
    panel.querySelector('#task-type').textContent = taskData.type || '—';
    panel.querySelector('#task-args').textContent = JSON.stringify(taskData.args || [], null, 2);

    return panel;
}

// Helper function to create task row from template
function createTaskRow(taskName, task) {
    const template = document.getElementById('task-row-template');
    const row = template.content.cloneNode(true).querySelector('tr');

    // Status class
    let statusClass = 'status-info';
    if (!task.task_start) statusClass = 'status-danger';
    else if (!task.task_finish) statusClass = 'status-success';
    else if (task.task_result === false) statusClass = 'status-danger';
    else if (task.type === "once") statusClass = 'status-warning';

    row.querySelector('.status-indicator').classList.add(statusClass);

    // Base fields
    row.querySelector('.task-name').textContent = taskName;
    row.querySelector('.task-interval').textContent = task.interval;

    const lastRun = task.task_start || 'Never';
    const nextRun = task.next_run || 'Not scheduled';

    const lastRunCell = row.querySelector('.task-last-run');
    lastRunCell.textContent = lastRun;
    lastRunCell.dataset.timestamp = task.task_start ? getTimestamp(task.task_start) : -1;

    const nextRunCell = row.querySelector('.task-next-run');
    nextRunCell.textContent = nextRun;
    nextRunCell.dataset.timestamp = task.next_run ? getTimestamp(task.next_run) : -1;

    let resultDisplay = 'N/A';
    if (task.task_result !== undefined) {
        if (typeof task.task_result === 'boolean') {
            resultDisplay = task.task_result ? 'Success' : 'Failed';
        } else {
            resultDisplay = String(task.task_result);
        }
    }
    row.querySelector('.task-result').textContent = resultDisplay;

    // ⬇️ Append new cells
    // const afterCell = row.querySelector('.task-before');
    // afterCell.textContent = task.after || '—';
    // row.appendChild(afterCell);

    const beforeCell = row.querySelector('.task-before');
    beforeCell.textContent = task.before || '—';

    const typeCell = row.querySelector('.task-type');
    typeCell.textContent = task.type || '—';

    const argsCell = row.querySelector('.task-args');
    argsCell.textContent = JSON.stringify(task.args || []);

    // Button data attributes
    row.querySelectorAll('button[data-task-id]').forEach(btn => {
        btn.setAttribute('data-task-id', task.id);
    });

    return row;
}

// Function to filter tasks based on search input
function filterTasks() {
    const searchText = $('#taskSearchInput').val().toLowerCase();
    const $rows = $('#taskTableBody tr').not('[colspan]');

    $rows.each(function () {
        const $row = $(this);
        const rowText = $row.text().toLowerCase();

        if (rowText.includes(searchText)) {
            $row.show();
        } else {
            $row.hide();
        }
    });

    // Check if any rows are visible
    const visibleRows = $('#taskTableBody tr:visible').length;
    if (visibleRows === 0 && $('#taskTableBody tr').length > 0) {
        // If we have rows but none are visible after filtering
        $('#taskTableBody').append(
            `<tr class="no-results-row"><td colspan="7" class="text-center">No tasks match your search</td></tr>`
        );
    } else {
        // Remove any no-results rows if we have visible rows
        $('#taskTableBody .no-results-row').remove();
    }
}

$(document).ready(function () {

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Show modal on button click
    $('#createTaskBtn').click(function () {
        $('#createTaskForm')[0].reset();
        $('#createTaskModal').modal('show');
    });


    // Make table headers sortable
    $('.sortable').click(function () {
        sortTable($(this).text());
    });

    // Search functionality
    $('#taskSearchInput').on('input', function () {
        filterTasks();
    });

    // Clear search button
    $('#clearSearchBtn').click(function () {
        $('#taskSearchInput').val('');
        filterTasks();
    });
});

// Table sorting function using jQuery
function sortTable(column) {
    const $table = $('#tasksTable');
    const $tbody = $('#taskTableBody');

    // Get column index
    const columnIndex = $table.find('th').filter(function () {
        return $(this).text() === column;
    }).index();

    // Sort state tracking - store both column and direction
    const currentSortData = $tbody.data('sort-data') || {column: '', direction: 'asc'};

    // Determine sort direction - if same column, toggle direction, else default to asc
    let isAsc = true;
    if (currentSortData.column === column) {
        isAsc = currentSortData.direction !== 'asc';
    }

    // Update sort direction indicator
    $table.find('th').removeClass('sort-asc sort-desc');
    $table.find('th').eq(columnIndex).addClass(isAsc ? 'sort-asc' : 'sort-desc');

    // Get all rows and sort them
    const $rows = $tbody.find('tr').not('[colspan]');

    $rows.sort(function (a, b) {
        const $aValue = $(a).find('td').eq(columnIndex).text();
        const $bValue = $(b).find('td').eq(columnIndex).text();

        // Handle date columns using stored Unix timestamps
        if (column === 'Last Run' || column === 'Next Run') {
            // Get Unix timestamps from data attributes
            const aTimestamp = parseFloat($(a).find('td').eq(columnIndex).data('timestamp') || -1);
            const bTimestamp = parseFloat($(b).find('td').eq(columnIndex).data('timestamp') || -1);

            return isAsc ? aTimestamp - bTimestamp : bTimestamp - aTimestamp;
        }

        // Handle result column
        if (column === 'Last Result') {
            // Special handling for Success/Failed/N/A
            const resultOrder = {'Success': 0, 'Failed': 1, 'N/A': 2};
            if ($aValue in resultOrder && $bValue in resultOrder) {
                return isAsc
                    ? resultOrder[$aValue] - resultOrder[$bValue]
                    : resultOrder[$bValue] - resultOrder[$aValue];
            }
        }

        // Default string comparison
        return isAsc
            ? $aValue.localeCompare($bValue)
            : $bValue.localeCompare($aValue);
    });

    // Append sorted rows back to the table
    $tbody.append($rows);

    // Store sort state with both column and direction
    $tbody.data('sort-data', {
        column: column,
        direction: isAsc ? 'asc' : 'desc'
    });
}

function loadTasks(isAutoRefresh = false) {
    const $tableBody = $('#taskTableBody');

    // Save current sort state before clearing the table
    const currentSortData = $tableBody.data('sort-data');

    // Save current search text
    const currentSearch = $('#taskSearchInput').val();

    // Only clear search input for manual refresh, not auto-refresh
    if (!isAutoRefresh) {
        $('#taskSearchInput').val('');
    }

    // Show loading indicator in the refresh button during manual refresh
    if (!isAutoRefresh) {
        $('#refreshBtn').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...');
        $('#refreshBtn').prop('disabled', true);
    }

    $.ajax({
        url: '/tasks/',
        headers: {
            'Accept': 'application/json'
        },
        success: function (t) {
            tasks = t;
            $tableBody.empty();

            if (Object.keys(tasks).length === 0) {
                $tableBody.html('<tr><td colspan="7" class="text-center">No tasks found</td></tr>');
                return;
            }

            $.each(tasks, function (taskName, task) {
                // Create row from template and append to table
                const row = createTaskRow(taskName, task);

                $(row.querySelector('.view-btn'))
                    .on('click', function () {
                        const taskId = $(this).data('task-id');
                        showTaskDetails(taskId);
                    });

                $(row.querySelector('.delete-btn')).on('click', function () {
                    const taskId = $(this).data('task-id');
                    if (confirm('Are you sure you want to delete this task?')) {
                        deleteTask(taskId);
                    }
                });

                $(row.querySelector('.edit-btn')).on('click', function () {
                    const taskId = $(this).data('task-id');
                    const task = tasks[taskId];

                    // Set modal title explicitly indicating it's a copy action
                    $('#createTaskModalLabel').text('Copy Task');

                    // Prefill fields with existing task details
                    //$('#taskName').val(task.name + '_copy'); // Optional: append "_copy" to distinguish new task
                    $('#taskName').val('');
                    $('#taskFunction').val(task.function);
                    $('#taskInterval').val(task.interval);
                    $('#taskOnce').prop('checked', true);
                    $('#taskArgs').val(JSON.stringify(task.args || []));

                    // Important: Clear any stored task-id, as this is not an update, but a new copy
                    $('#createTaskForm').removeData('task-id');

                    // Open modal
                    $('#createTaskModal').modal('show');
                });
                // Add event listeners to buttons using jQuery event delegation
                // $(document).off('click', '.view-btn, .edit-btn, .delete-btn');

                $tableBody.append(row);
                // Initialize tooltips for new buttons

            });
            initTooltips();

            currentSortData && sortTable(currentSortData.column);

            // If this was an auto-refresh and we had a search filter, re-apply it
            if (isAutoRefresh && currentSearch) {
                $('#taskSearchInput').val(currentSearch);
                filterTasks();
            }

            // Update last updated indicator - handled by base.html's functions
            if (isAutoRefresh && $('#autoRefreshBtn').hasClass('active')) {
                // Pulse animation on the spinner to indicate activity
                $('#autoRefreshSpinner').fadeOut(100).fadeIn(100);
            }

            // Reset refresh button
            $('#refreshBtn').html('<i class="bi bi-arrow-clockwise"></i> Refresh');
            $('#refreshBtn').prop('disabled', false);
        },
        error: function (xhr, status, error) {
            console.error('Error loading tasks:', error);
            $tableBody.html(`<tr><td colspan="7" class="text-center text-danger">Error loading tasks: ${error}</td></tr>`);

            // Update last updated time with error indicator
            $('#lastUpdated').html(`${formatLastUpdated()} <span class="badge bg-danger">Error refreshing</span>`);

            // Reset refresh button
            $('#refreshBtn').html('<i class="bi bi-arrow-clockwise"></i> Refresh');
            $('#refreshBtn').prop('disabled', false);
        }
    });
}

function showTaskDetails(taskId) {
    const $modal = $('#taskDetailModal');
    const $modalTitle = $('#taskDetailTitle');
    const $modalBody = $('#taskDetailBody');
    let taskData = tasks[taskId]
    $modalTitle.text(`Task Details: ${taskData.name}`);

    // Clear previous content
    $modalBody.empty();

    // Create and append the details panel
    const detailsPanel = createTaskDetailsPanel(taskData);
    $modalBody.append(detailsPanel);

    // Show the modal using jQuery
    $modal.modal('show');
}

// Initialize tooltips for dynamically added elements
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl)
    });
}

function deleteTask(taskId) {
    $.ajax({
        url: '/tasks/'+encodeURIComponent(taskId),
        method: 'DELETE',
        headers: {
            'Accept': 'application/json'
        },
        success: function (data) {
            alert(data.message);
            loadTasks();  // Refresh the task list
        },
        error: function (xhr, status, error) {
            console.error('Error deleting task:', error);
            alert('Failed to delete task: ' + error);
        }
    });
}


// Handle form submission
$('#createTaskForm').submit(function (e) {
    e.preventDefault();

    const name = $('#taskName').val().trim();
    const functionPath = $('#taskFunction').val().trim();
    const interval = $('#taskInterval').val().trim();
    const once = $('#taskOnce').is(':checked');
    let args = [];

    try {
        const rawArgs = $('#taskArgs').val().trim();
        args = rawArgs ? JSON.parse(rawArgs) : [];
    } catch (err) {
        alert('Invalid arguments. Must be a valid JSON array.');
        return;
    }

    $.ajax({
        url: '/tasks/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            name,
            function: functionPath,
            interval,
            once,
            args
        }),
        success: function () {
            $('#createTaskModal').modal('hide');
            loadTasks();
        },
        error: function (xhr) {
            alert('Error creating task: ' + (xhr.responseJSON?.error || xhr.statusText));
        }
    });
});