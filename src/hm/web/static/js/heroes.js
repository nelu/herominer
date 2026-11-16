// Helper function to get Unix timestamp from date string for sorting
function getTimestamp(dateValue) {
    if (!dateValue) return 0;

    // If the value is already a number (Unix timestamp), return it directly
    if (typeof dateValue === 'number') return dateValue;

    // If the value is a numeric string, try to parse it as a number
    if (typeof dateValue === 'string' && !isNaN(dateValue)) {
        return parseFloat(dateValue);
    }

    // If we have a date string in YYYY-MM-DD HH:MM:SS format
    if (typeof dateValue === 'string' && dateValue.includes(' ') && dateValue.includes('-')) {
        try {
            // Parse the YYYY-MM-DD HH:MM:SS format manually to avoid browser timezone conversion
            const [datePart, timePart] = dateValue.split(' ');
            if (!datePart || !timePart) return 0;

            const [year, month, day] = datePart.split('-').map(Number);
            const [hours, minutes, seconds] = timePart.split(':').map(val => parseFloat(val));

            // Create date object with UTC to avoid timezone issues (but only for sorting)
            return Date.UTC(year, month - 1, day, hours, minutes, seconds) / 1000;
        } catch (e) {
            console.warn("Error parsing date string:", e);
            return 0;
        }
    }

    // If all else fails, try to use the JavaScript Date object
    try {
        return new Date(dateValue).getTime() / 1000;
    } catch (e) {
        console.warn("Unable to parse date value:", dateValue);
        return 0;
    }
}

// Helper function to create hero details panel
function createHeroDetailsPanel(heroData) {
    // Use the template to create the panel
    const template = document.getElementById('hero-details-template');
    const fragment = template.content.cloneNode(true);
    const panel = document.createElement('div');
    panel.classList.add('hero-details-panel');
    panel.appendChild(fragment);

    // Update the panel with hero data
    panel.querySelector('#hero-id').textContent = heroData._slug || '';
    panel.querySelector('#hero-name').textContent = heroData.name || '';
    panel.querySelector('#hero-level').textContent = heroData.level || 0;
    panel.querySelector('#hero-class').textContent = heroData.class || 'Unknown';

    // Basic stats
    panel.querySelector('#hero-power').textContent = heroData.power || 0;
    panel.querySelector('#hero-health').textContent = heroData.stats?.health || 'N/A';
    panel.querySelector('#hero-attack').textContent = heroData.stats?.physical_attack || 'N/A';
    panel.querySelector('#hero-defense').textContent = heroData.stats?.armor || 'N/A';

    // Additional stats section
    const additionalStats = [
        {label: 'Stars', value: heroData.stars || 0, icon: '⭐'},
        {label: 'XP', value: heroData.xp?.toLocaleString() || 0},
        {label: 'Strength', value: heroData.stats?.strength || 'N/A'},
        {label: 'Agility', value: heroData.stats?.agility || 'N/A'},
        {label: 'Intelligence', value: heroData.stats?.intelligence || 'N/A'},
        {label: 'Magic Attack', value: heroData.stats?.magic_attack || 'N/A'},
        {label: 'Magic Defense', value: heroData.stats?.magic_defense || 'N/A'},
        {label: 'Armor Penetration', value: heroData.stats?.armor_penetration || 'N/A'}
    ];

    // Create additional stats section
    const statsSection = document.createElement('div');
    statsSection.className = 'mt-3';
    statsSection.innerHTML = `
        <h6>Additional Stats</h6>
        <div class="row">
            ${additionalStats.map(stat => `
                <div class="col-md-3 col-sm-6 mb-2">
                    <div class="card bg-light">
                        <div class="card-body p-2 text-center">
                            <div class="small text-muted">${stat.label}</div>
                            <div class="fw-bold">${stat.icon ? stat.icon + ' ' : ''}${stat.value}</div>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    panel.appendChild(statsSection);

    // Artifacts section
    const artifactsList = panel.querySelector('#hero-equipment');
    artifactsList.innerHTML = '';

    if (heroData.artifacts?.available && Object.keys(heroData.artifacts.available).length > 0) {
        Object.entries(heroData.artifacts.available).forEach(([slotId, artifact]) => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';

            // Star icons for artifact quality
            const starIcons = artifact.stars > 0 ? '⭐'.repeat(artifact.stars) : '';

            li.innerHTML = `
                <div>
                    <span class="fw-bold">${artifact.name}</span>
                    <span class="text-muted small"> (Level ${artifact.lvl})</span>
                </div>
                <span class="badge bg-primary">${starIcons}</span>
            `;
            artifactsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.textContent = 'No artifacts equipped';
        artifactsList.appendChild(li);
    }

    // Skills section
    const skillsList = panel.querySelector('#hero-skills');
    skillsList.innerHTML = '';

    if (heroData.skills?.available && Object.keys(heroData.skills.available).length > 0) {
        Object.entries(heroData.skills.available).forEach(([skillId, skill]) => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';

            // Cost info if available
            const costInfo = skill.cost > 0 ? ` (Cost: ${skill.cost})` : '';

            li.innerHTML = `
                <div>
                    <span class="fw-bold">${skill.name}</span>
                    ${costInfo}
                </div>
                <span class="badge bg-info">Level ${skill.lvl}</span>
            `;
            skillsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.textContent = 'No skills available';
        skillsList.appendChild(li);
    }

    // Add skins section
    const skinsSection = document.createElement('div');
    skinsSection.className = 'mt-4';
    skinsSection.innerHTML = `
        <h6>Available Skins</h6>
        <ul class="list-group">
            ${heroData.skins?.available && Object.keys(heroData.skins.available).length > 0
        ? Object.entries(heroData.skins.available).map(([skinId, skin]) => `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            <span class="fw-bold">${skin.name}</span>
                            ${skin.locked ? '<span class="badge bg-secondary ms-2">Locked</span>' : ''}
                        </div>
                        ${skin.lvl ? `<span class="badge bg-success">Level ${skin.lvl}</span>` : ''}
                    </li>
                `).join('')
        : '<li class="list-group-item">No skins available</li>'
    }
        </ul>
    `;
    panel.appendChild(skinsSection);

    // Add slots/equipment section if available
    if (heroData.slots?.available && Object.keys(heroData.slots.available).length > 0) {
        const slotsSection = document.createElement('div');
        slotsSection.className = 'mt-4';
        slotsSection.innerHTML = `
            <h6>Equipment Slots</h6>
            <div class="row">
                ${Object.entries(heroData.slots.available).map(([slotId, slot]) => `
                    <div class="col-md-2 col-sm-4 col-6 mb-2">
                        <div class="card ${slot.equipped ? 'bg-success text-white' : 'bg-light'}">
                            <div class="card-body p-2 text-center">
                                <div class="small">${slot.equipped ? 'Equipped' : 'Empty'}</div>
                                <div class="fw-bold">Slot ${slotId}</div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
            ${heroData.slots.color_lvl ? `<div class="small text-muted mt-1">Equipment Color Level: ${heroData.slots.color_lvl}</div>` : ''}
        `;
        panel.appendChild(slotsSection);
    }

    // Add ascension info if available
    if (heroData.ascension) {
        const ascensionSection = document.createElement('div');
        ascensionSection.className = 'mt-4';
        ascensionSection.innerHTML = `
            <h6>Ascension Details</h6>
            <div class="card bg-light">
                <div class="card-body p-2">
                    <div class="row">
                        <div class="col-6">
                            <span class="text-muted">Rank:</span> 
                            <span class="fw-bold">${heroData.ascension.rank}</span>
                        </div>
                        <div class="col-6">
                            <span class="text-muted">Specialization:</span> 
                            <span class="fw-bold">${heroData.ascension.role_specialization || 'None'}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        panel.appendChild(ascensionSection);
    }

    // Add last update info
    if (heroData.last_update) {
        const lastUpdateDate = new Date(heroData.last_update * 1000); // Convert Unix timestamp to JS date
        const lastUpdateSection = document.createElement('div');
        lastUpdateSection.className = 'mt-4 text-end small text-muted';
        lastUpdateSection.textContent = `Last updated: ${lastUpdateDate.toLocaleString()}`;
        panel.appendChild(lastUpdateSection);
    }

    return panel;
}

// Helper function to create hero row from template
function createHeroRow(heroSlug, hero) {
    // Use the template to create the row
    const template = document.getElementById('hero-row-template');
    const row = template.content.cloneNode(true).querySelector('tr');

    // Set status indicator - only two possible statuses
    const statusClass = hero.status === 'available' ? 'status-available' : 'status-inactive';
    row.querySelector('.status-indicator').classList.add(statusClass);

    // Set basic information
    row.querySelector('.hero-name').textContent = hero.name || heroSlug;
    row.querySelector('.hero-level').textContent = hero.level || 0;

    // Display stars with star icons
    const stars = hero.stars || 0;
    row.querySelector('.hero-stars').innerHTML = stars > 0 ? '⭐'.repeat(stars) : '0';

    row.querySelector('.hero-power').textContent = hero.power || 0;

    // Format last activity
    const lastActivity = hero.last_activity || 'Never';
    const lastActivityCell = row.querySelector('.hero-last-activity');
    lastActivityCell.textContent = lastActivity;
    if (hero.last_activity) {
        lastActivityCell.dataset.timestamp = getTimestamp(hero.last_activity);
    } else {
        lastActivityCell.dataset.timestamp = -1;
    }

    // Set button data attributes
    row.querySelectorAll('button[data-hero-id]').forEach(btn => {
        btn.setAttribute('data-hero-id', heroSlug);
    });

    return row;
}

// Function to filter heroes based on search input
function filterHeroes() {
    const searchText = $('#heroSearchInput').val().toLowerCase();
    const $rows = $('#heroTableBody tr').not('[colspan]');

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
    const visibleRows = $('#heroTableBody tr:visible').length;
    if (visibleRows === 0 && $('#heroTableBody tr').length > 0) {
        // If we have rows but none are visible after filtering
        $('#heroTableBody').append(
            `<tr class="no-results-row"><td colspan="9" class="text-center">No heroes match your search</td></tr>`
        );
    } else {
        // Remove any no-results rows if we have visible rows
        $('#heroTableBody .no-results-row').remove();
    }
}

// Table sorting function using jQuery
// Single implementation of the sortTable function
function sortTable(column) {
    // Add a debounce mechanism to prevent double execution
    if (window.sortTableInProgress) {
        return;
    }

    window.sortTableInProgress = true;
    setTimeout(() => {
        window.sortTableInProgress = false;
    }, 300); // Clear flag after 300ms

    const $table = $('#heroesTable');
    const $tbody = $('#heroTableBody');

    // Get column index and normalized column name
    const columnIndex = $table.find('th').filter(function () {
        // Use textContent to get the text without the icon elements
        const headerText = $(this).clone().children().remove().end().text().trim();
        return headerText === column;
    }).index();

    const $header = $table.find('th').eq(columnIndex);

    // Sort state tracking - store both column and direction
    const currentSortData = $tbody.data('sort-data') || {column: '', direction: 'asc'};

    // Determine sort direction - if same column, toggle direction, else default to asc
    let isAsc = true;
    if (currentSortData.column === column) {
        isAsc = currentSortData.direction !== 'asc';
    }

    // Update sort direction indicator - first remove all classes
    $table.find('th').removeClass('sort-asc sort-desc');

    // Then add the appropriate class to the current header
    $header.addClass(isAsc ? 'sort-asc' : 'sort-desc');

    // Log sort state for debugging
    console.log(`Sorting ${column} ${isAsc ? 'ascending' : 'descending'}`);

    // Get all rows and sort them
    const $rows = $tbody.find('tr').not('[colspan]');

    $rows.sort(function (a, b) {
        const $aValue = $(a).find('td').eq(columnIndex).text();
        const $bValue = $(b).find('td').eq(columnIndex).text();

        // Handle numerical columns - level and power
        if (column === 'Level' || column === 'Power') {
            const aNum = parseInt($aValue) || 0;
            const bNum = parseInt($bValue) || 0;
            return isAsc ? aNum - bNum : bNum - aNum;
        }

        // Handle stars column - count star emoji for proper numeric sorting
        if (column === 'Stars') {
            const aStars = ($aValue.match(/⭐/g) || []).length || 0;
            const bStars = ($bValue.match(/⭐/g) || []).length || 0;
            return isAsc ? aStars - bStars : bStars - aStars;
        }

        // Handle date column - Last Update (renamed from Last Activity)
        if (column === 'Last Update') {
            // Get Unix timestamps from data attributes
            const aTimestamp = parseFloat($(a).find('td').eq(columnIndex).data('timestamp') || -1);
            const bTimestamp = parseFloat($(b).find('td').eq(columnIndex).data('timestamp') || -1);

            return isAsc ? aTimestamp - bTimestamp : bTimestamp - aTimestamp;
        }

        // Handle XP column
        if (column === 'XP') {
            const aNum = parseInt($aValue.replace(/,/g, '')) || 0;
            const bNum = parseInt($bValue.replace(/,/g, '')) || 0;
            return isAsc ? aNum - bNum : bNum - aNum;
        }

        // Handle Slots Color Level column
        if (column === 'Slots Color Level') {
            // If it's N/A, treat as 0 for sorting
            const aValue = $aValue === 'N/A' ? 0 : parseInt($aValue) || 0;
            const bValue = $bValue === 'N/A' ? 0 : parseInt($bValue) || 0;
            return isAsc ? aValue - bValue : bValue - aValue;
        }

        // Default string comparison
        return isAsc
            ? $aValue.localeCompare($bValue)
            : $bValue.localeCompare($aValue);
    });

    // Append sorted rows back to the table
    $tbody.empty().append($rows);

    // Store sort state with both column and direction
    $tbody.data('sort-data', {
        column: column,
        direction: isAsc ? 'asc' : 'desc'
    });
}


function initHeroesPage() {
    // Load heroes on page load
    loadHeroes();

    // Set up search functionality
    $('#heroSearchInput').on('keyup', filterHeroes);
    $('#clearSearchBtn').on('click', function () {
        $('#heroSearchInput').val('');
        filterHeroes();
    });

    // Set up create hero button
    $('#createHeroBtn').on('click', function () {
        window.location.href = '/heroes/create';
    });

    // Clear any existing handlers first to prevent duplicates
    $('.sortable').off('click');

    // Set up sortable headers
    $('.sortable').on('click', function () {
        const field = $(this).clone().children().remove().end().text().trim();
        sortTable(field);
    });
}

function loadHeroes(isAutoRefresh = false) {
    const $tableBody = $('#heroTableBody');

    // Save current sort state before clearing the table
    const currentSort = $tableBody.data('sort');

    // Save current search text
    const currentSearch = $('#heroSearchInput').val();

    // Only clear search input for manual refresh, not auto-refresh
    if (!isAutoRefresh) {
        $('#heroSearchInput').val('');
    }

    // Show loading indicator in the refresh button during manual refresh
    if (!isAutoRefresh) {
        $('#refreshBtn').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...');
        $('#refreshBtn').prop('disabled', true);
    }

    $.ajax({
        url: '/heroes/',
        headers: {
            'Accept': 'application/json'
        },
        success: function (heroes) {
            $tableBody.empty();

            if (Object.keys(heroes).length === 0) {
                $tableBody.html('<tr><td colspan="7" class="text-center">No heroes found</td></tr>');
                return;
            }

            $.each(heroes, function (heroSlug, hero) {
                // Create row from template and append to table
                const row = createHeroRow(heroSlug, hero);
                $tableBody.append(row);
            });

            // Add event listeners to buttons using jQuery event delegation
            $(document).off('click', '.view-btn, .edit-btn, .delete-btn');

            $(document).on('click', '.view-btn', function () {
                const heroId = $(this).data('hero-id');
                showHeroDetails(heroId, heroes[heroId]);
            });

            $(document).on('click', '.edit-btn', function () {
                const heroId = $(this).data('hero-id');
                window.location.href = `/heroes/edit/${heroId}`;
            });

            $(document).on('click', '.delete-btn', function () {
                const heroId = $(this).data('hero-id');
                if (confirm('Are you sure you want to delete this hero?')) {
                    deleteHero(heroId);
                }
            });

            // Initialize tooltips for new buttons
            initTooltips();

            // Re-apply sorting if there was a previous sort
            if ($tableBody.data('sort-data') && $tableBody.data('sort-data').column) {
                const sortData = $tableBody.data('sort-data');
                // We need to manually invoke sort to maintain the previous sort direction
                sortTable(sortData.column);

                // If it was descending, we need to sort again to toggle back to descending
                // since the first call will always start with ascending
                if (sortData.direction === 'desc') {
                    sortTable(sortData.column);
                }
            }

            // If this was an auto-refresh and we had a search filter, re-apply it
            if (isAutoRefresh && currentSearch) {
                $('#heroSearchInput').val(currentSearch);
                filterHeroes();
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
            console.error('Error loading heroes:', error);
            $tableBody.html(`<tr><td colspan="9" class="text-center text-danger">Error loading heroes: ${error}</td></tr>`);

            // Update last updated time with error indicator
            $('#lastUpdated').html(`${formatLastUpdated()} <span class="badge bg-danger">Error refreshing</span>`);

            // Reset refresh button
            $('#refreshBtn').html('<i class="bi bi-arrow-clockwise"></i> Refresh');
            $('#refreshBtn').prop('disabled', false);
        }
    });
}

function createHeroRow(heroSlug, hero) {
    // Use the template to create the row
    const template = document.getElementById('hero-row-template');
    const row = template.content.cloneNode(true).querySelector('tr');

    // Set status indicator - only two possible statuses
    const statusClass = hero.status === 'available' ? 'status-available' : 'status-inactive';
    row.querySelector('.status-indicator').classList.add(statusClass);

    // Set basic information
    row.querySelector('.hero-name').textContent = hero.name || heroSlug;
    row.querySelector('.hero-level').textContent = hero.level || 0;

    // Display stars with star icons
    const stars = hero.stars || 0;
    row.querySelector('.hero-stars').innerHTML = stars > 0 ? '⭐'.repeat(stars) : '0';

    row.querySelector('.hero-power').textContent = hero.power || 0;

    // Add XP and slots color level
    row.querySelector('.hero-xp').textContent = hero.xp || 0;
    row.querySelector('.hero-slots-color-lvl').textContent = hero.slots_color_lvl || 'N/A';

    // Format last update (renamed from last_activity)
    const lastUpdateCell = row.querySelector('.hero-last-update');

    if (hero.last_update) {
        // If it's a timestamp, convert to human-readable date
        let timestamp = hero.last_update;
        if (typeof timestamp === 'number' || !isNaN(timestamp)) {
            const date = new Date(Number(timestamp) * 1000);
            lastUpdateCell.textContent = date.toLocaleString();
        } else {
            // If it's already a string, display as is
            lastUpdateCell.textContent = hero.last_update;
        }
        lastUpdateCell.dataset.timestamp = getTimestamp(hero.last_update);
    } else if (hero.last_activity) {
        // Fallback to last_activity
        lastUpdateCell.textContent = hero.last_activity;
        lastUpdateCell.dataset.timestamp = getTimestamp(hero.last_activity);
    } else {
        lastUpdateCell.textContent = 'Never';
        lastUpdateCell.dataset.timestamp = -1;
    }

    // Set button data attributes
    row.querySelectorAll('button[data-hero-id]').forEach(btn => {
        btn.setAttribute('data-hero-id', heroSlug);
    });

    return row;
}

function formatDate(dateString) {
    if (!dateString) return 'Never';

    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    // If less than a day, show relative time
    if (diff < 24 * 60 * 60 * 1000) {
        const hours = Math.floor(diff / (60 * 60 * 1000));
        if (hours < 1) {
            const minutes = Math.floor(diff / (60 * 1000));
            return minutes < 1 ? 'Just now' : `${minutes} min ago`;
        }
        return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    }

    // Otherwise show the date
    return date.toLocaleDateString();
}

function showHeroDetails(heroId, hero) {
    // Set hero identifier in the data object for consistent reference
    hero._slug = heroId;

    // Set modal title
    $('#heroDetailTitle').text(`${hero.name} (Level ${hero.level})`);

    // Create a detailed hero panel using our helper function
    const detailsPanel = createHeroDetailsPanel(hero);

    // Clear previous content and add the new details
    $('#heroDetailBody').empty().append(detailsPanel);

    // Show the modal
    const heroDetailModal = new bootstrap.Modal(document.getElementById('heroDetailModal'));
    heroDetailModal.show();
}

function deleteHero(heroId) {
    $.ajax({
        url: `/heroes/${heroId}`,
        type: 'DELETE',
        success: function (result) {
            // Reload heroes list
            loadHeroes();
            // Show success message
            alert('Hero deleted successfully');
        },
        error: function (xhr, status, error) {
            console.error('Error deleting hero:', error);
            alert('Error deleting hero: ' + error);
        }
    });
}

function filterHeroes() {
    const searchText = $('#heroSearchInput').val().toLowerCase();

    $('#heroTableBody tr').each(function () {
        const row = $(this);
        const name = row.find('.hero-name').text().toLowerCase();
        const stars = row.find('.hero-stars').text().toLowerCase();

        if (name.includes(searchText) || stars.includes(searchText)) {
            row.show();
        } else {
            row.hide();
        }
    });
}

// This duplicate function has been removed as it conflicts with the other implementation

function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover'
        });
    });
}

function showHeroDetails(heroId, heroData) {
    const $modal = $('#heroDetailModal');
    const $modalTitle = $('#heroDetailTitle');
    const $modalBody = $('#heroDetailBody');

    $modalTitle.text(`Hero Details: ${heroData.name || heroId}`);

    // Clear previous content
    $modalBody.empty();

    // Create and append the details panel
    const detailsPanel = createHeroDetailsPanel(heroData);
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

function deleteHero(heroId) {
    $.ajax({
        url: `/heroes/${heroId}`,
        method: 'DELETE',
        headers: {
            'Accept': 'application/json'
        },
        success: function (data) {
            alert(data.message || 'Hero deleted successfully');
            loadHeroes();  // Refresh the hero list
        },
        error: function (xhr, status, error) {
            console.error('Error deleting hero:', error);
            alert('Failed to delete hero: ' + error);
        }
    });
}

// The main document ready handler is already defined above as $(document).ready(initHeroesPage)
// This duplicate handler has been removed to prevent double binding of event handlers
