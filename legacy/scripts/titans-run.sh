#!/bin/sh
source ./scripts/inc.sh
source ${ROOTPATH}/scripts/guild.sh
source ${ROOTPATH}/scripts/titans.sh

if has_titan_valley_activities && guild_open "titan-valley"; then
    if ! has_open_artifact_sphere_today; then
        open_titan_artifact_spheres

        log "Checking hall of fame"
        play_action guild/tournament-of-elements-hall-of-fame-collect
    fi;

    ! has_tournament_raid_disabled && {
        log "Raiding tournament of elements"
        play_action guild/tournament-of-elements-raid-collect
        play_action guild/tournament-of-elements-play-mission
    }
    back_to_lobby

else
    log "Titans: Titan valley disabled"
fi;


if has_guild_island_activities && guild_open "guild-island" ; then

    # one summoning per day
    ! has_open_summon_sphere_today && {
        open_titan_summon_spheres
        summon_available_titans
    }    
    ! has_run_titans_evolve && {
        log "Titans: Daily check on titans for evolution"
        evolve_any_titan
    }

    has_titan_valley && ! has_run_titans_artifact_increase && {
        log "Increasing all titan artifacts"
        increase_titan_artifacts
    }

    ! has_lost_dungeon_mission && ! has_finished_daily_dungeon_levels \
    && {
            log "Titans: Collecting dungeon divination cards"
            collect_dungeon_divination_cards
            log "Titans: Playing dungeon missions"
            play_daily_dungeon_levels
    }

    back_to_lobby 

else

    log "Titans: Failed to open guild-island"
fi;


