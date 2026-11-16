
let heroData = {};

function deepSearch(obj, queryParts) {
    const textDump = JSON.stringify(obj).toLowerCase();
    return queryParts.every(part => {
        if (part.includes(":")) {
            const [key, val] = part.split(":");
            return textDump.includes(`"${key.toLowerCase()}":${val.toLowerCase()}`);
        }
        return textDump.includes(part);
    });
}

function filterHeroes(query) {
    const result = {};
    const queryParts = query.toLowerCase().trim().split(/\s+/);
    Object.entries(heroData).forEach(([id, hero]) => {
        if (deepSearch(hero, queryParts)) {
            result[id] = hero;
        }
    });
    return result;
}

function groupHeroes(filtered, mode) {
    const groups = {};
    Object.entries(filtered).forEach(([id, hero]) => {
        let key = "Unknown";
        switch (mode) {
            case "power":
                const power = hero.power || 0;
                key = power < 1000 ? "0–999" :
                      power < 2000 ? "1000–1999" :
                      power < 3000 ? "2000–2999" : "3000+";
                break;
            case "slots.color_lvl":
                key = hero.slots?.color_lvl != null ? `Color ${hero.slots.color_lvl}` : "No color level";
                break;
            case "level":
                const lvl = hero.level || 0;
                key = lvl <= 10 ? "1–10" :
                      lvl <= 20 ? "11–20" :
                      lvl <= 30 ? "21–30" :
                      lvl <= 40 ? "31–40" :
                      lvl <= 50 ? "41–50" : "51+";
                break;
            case "stars":
                key = hero.stars != null ? `${hero.stars}★` : "No stars";
                break;
            case "has_evolve":
                const artifacts = hero.artifacts?.available || {};
                const hasEvolve = Object.values(artifacts).some(a => a.has_evolution);
                key = hasEvolve ? "Has Evolution" : "No Evolution";
                break;
            default:
                key = "Ungrouped";
        }

        if (!groups[key]) groups[key] = [];
        groups[key].push({ id, text: hero.name });
    });
    return groups;
}

function renderDropdown(filtered) {
    const mode = $("#group-mode").val();
    const grouped = groupHeroes(filtered, mode);
    const $select = $("#hero-select");
    $select.empty();

    Object.entries(grouped).forEach(([groupName, heroes]) => {
        const $optgroup = $(`<optgroup label="${groupName}"></optgroup>`);
        heroes.forEach(hero => {
            $optgroup.append(`<option value="${hero.id}">${hero.text}</option>`);
        });
        $select.append($optgroup);
    });

    $select.trigger("change.select2");
}

function renderHeroEditor(id) {
    const hero = heroData[id];
    if (!hero) return;

    $("#hero-editor").html(`
        <h2>✏️ Edit Hero: ${hero.name}</h2>
        <textarea id="editor">${JSON.stringify(hero, null, 2)}</textarea><br>
        <button id="save">💾 Save</button>
        <div id="dialog" title="Status"><p>Saving hero data...</p></div>
    `).show();

    $("#save").click(function () {
        try {
            const updated = JSON.parse($("#editor").val());
            $("#dialog").dialog({ modal: true });
            $.ajax({
                url: `/heroes/${id}`,
                method: "PUT",
                contentType: "application/json",
                data: JSON.stringify(updated),
                success: () => {
                    $("#dialog").html("<p>Hero saved successfully ✅</p>");
                    heroData[id] = updated;
                },
                error: () => {
                    $("#dialog").html("<p>Failed to save hero ❌</p>");
                }
            });
        } catch (e) {
            alert("Invalid JSON");
        }
    });
}

function loadHeroes(callback) {
    $.ajax({
        url: "/heroes/",
        type: "GET",
        headers: {
            "Accept": "application/json"
        },
        success: function(data) {
            heroData = data;
            callback(heroData);
        }
    });
}

$(document).ready(function () {
    $("#hero-select").select2({ placeholder: "Select a hero", allowClear: true });

    loadHeroes(function(data) {
        renderDropdown(data);
    });

    $("#search").on("input", function () {
        const query = this.value;
        const filtered = filterHeroes(query);
        renderDropdown(filtered);
    });

    $("#group-mode").on("change", function () {
        const query = $("#search").val();
        const filtered = filterHeroes(query);
        renderDropdown(filtered);
    });

    $("#hero-select").on("change", function () {
        const id = $(this).val();
        if (id) renderHeroEditor(id);
    });
});
