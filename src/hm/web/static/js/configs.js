// configs.js
let configEditor;
let endpoint = window.location.pathname.endsWith('/')
    ? window.location.pathname
    : window.location.pathname + '/';

function loadConfigs() {
    const $tbody = $('#configTableBody');
    $.getJSON(endpoint, function (configs) {
        $tbody.empty();

        if (Object.keys(configs).length === 0) {
            $tbody.append(`<tr><td colspan="3" class="text-center">No configurations found</td></tr>`);
            return;
        }

        Object.entries(configs).forEach(([name, content]) => {
            const row = $('<tr>');
            const taskCount = typeof content.tasks === 'object' && content.tasks !== null
                ? Object.keys(content.tasks).length
                : 0;
            row.append(`<td>${name}</td>`);
            row.append(`<td>${taskCount}</td>`);
            const actionBtns = `
                <td>
                    <button class="btn btn-sm btn-warning edit-btn" data-name="${name}"><i class="bi bi-pencil"></i></button>
                    <button class="btn btn-sm btn-danger delete-btn" data-name="${name}"><i class="bi bi-trash"></i></button>
                </td>`;
            row.append(actionBtns);
            $tbody.append(row);
        });

        $('.edit-btn').click(function () {
            const name = $(this).data('name');
            $.getJSON(endpoint + name, function (data) {
                $('#configModalTitle').text(`Edit Configuration: ${name}`);
                $('#configName').val(name).prop('disabled', true);
                configEditor.setValue(JSON.stringify(data, null, 2), -1);
                $('#configModal').modal('show');
            });
        });

        $('.view-btn').click(function () {
            const name = $(this).data('name');
            $.getJSON(endpoint + name, function (data) {
                alert(`Content of ${name}:\n\n` + JSON.stringify(data, null, 2));
            });
        });

        $('.delete-btn').click(function () {
            const name = $(this).data('name');
            if (confirm(`Reset configuration ${name}?`)) {
                $.ajax({
                    url: endpoint + name,
                    type: 'DELETE',
                    success: function () {
                        loadConfigs();
                    },
                    error: function (xhr) {
                        alert('Error deleting: ' + (xhr.responseJSON?.error || xhr.statusText));
                    }
                });
            }
        });

        filterConfigs();
    });
}

function filterConfigs() {
    const search = $('#configSearchInput').val().toLowerCase();
    $('#configTableBody tr').each(function () {
        const row = $(this);
        const text = row.text().toLowerCase();
        row.toggle(text.includes(search));
    });
}

$('#createConfigBtn').click(function () {
    $('#configModalTitle').text('Create New Configuration');
    $('#configName').val('').prop('disabled', false);
    configEditor.setValue('{}', -1);
    $('#configModal').modal('show');
});

$('#configForm').submit(function (e) {
    e.preventDefault();
    const name = $('#configName').val().trim();
    let content;

    try {
        content = JSON.parse(configEditor.getValue());
    } catch (err) {
        alert('Invalid JSON content.');
        return;
    }

    const isNew = !$('#configName').prop('disabled');
    const method = isNew ? 'POST' : 'PUT';
    const url = isNew ? endpoint : endpoint + name;
    const payload = isNew ? {name, content} : content;

    $.ajax({
        url: url,
        method: method,
        contentType: 'application/json',
        data: JSON.stringify(payload),
        success: function () {
            $('#configModal').modal('hide');
            loadConfigs();
        },
        error: function (xhr) {
            alert('Error: ' + (xhr.responseJSON?.error || xhr.statusText));
        }
    });
});



