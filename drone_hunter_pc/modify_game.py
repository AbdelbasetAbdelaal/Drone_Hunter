import re

with open('src/core/game.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports
if 'MissionSystem' not in content:
    content = content.replace('from src.systems.combat_director import CombatDirector',
        'from src.systems.combat_director import CombatDirector\nfrom src.systems.mission_system import MissionSystem\nfrom src.data.mission_data import get_mission_data')
    
if 'STATE_MISSION_BRIEFING' not in content:
    content = content.replace('STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_VICTORY',
        'STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_VICTORY,\n    STATE_MISSION_BRIEFING, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED, GameState')

if 'draw_mission_select_ui' not in content:
    content = content.replace('draw_sector_select_ui, draw_pause_settings_ui,',
        'draw_sector_select_ui, draw_pause_settings_ui, draw_mission_select_ui, draw_mission_briefing, draw_mission_complete, draw_mission_failed,')

if 'self.mission_system = ' not in content:
    content = content.replace('self.combat_director = CombatDirector(self.encounter_system)',
        'self.combat_director = CombatDirector(self.encounter_system)\n        self.mission_system = MissionSystem()')

# Replace sector select rendering block to use the new UI
if 'draw_mission_select_ui(canvas, ctx, ctx.scrap)' not in content:
    content = content.replace(
        'elif ctx.state == STATE_SECTOR_SELECT:\n            draw_sector_select_ui(canvas, ctx.unlocked_sectors, ctx.coins, ctx.difficulty_mode, ctx.unlocked_stages)',
        'elif ctx.state == STATE_SECTOR_SELECT:\n            ui_rects = draw_mission_select_ui(canvas, ctx, ctx.scrap)\n            self.ui_rects_cache = ui_rects'
    )
    
if 'elif ctx.state in (STATE_PLAYING, STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER):' in content:
    content = content.replace(
        'elif ctx.state in (STATE_PLAYING, STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER):',
        'elif ctx.state in (STATE_PLAYING, STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED):'
    )

if 'elif ctx.state == STATE_GAME_OVER:\n                draw_game_over_ui(canvas, ctx.total_score, ctx.highscore)' in content:
    content = content.replace(
        'elif ctx.state == STATE_GAME_OVER:\n                draw_game_over_ui(canvas, ctx.total_score, ctx.highscore)',
        'elif ctx.state == STATE_GAME_OVER:\n                draw_game_over_ui(canvas, ctx.total_score, ctx.highscore)\n            elif ctx.state == STATE_MISSION_COMPLETE:\n                is_sec = (self.mission_system.active_mission_data["mission_number"] == 5)\n                draw_mission_complete(canvas, self.mission_system.active_mission_data, self.mission_system.is_mission_success, is_sec)\n            elif ctx.state == STATE_MISSION_FAILED:\n                draw_mission_failed(canvas, ctx.scrap)'
    )

# Briefing render
if 'elif ctx.state == STATE_MISSION_BRIEFING:' not in content:
    content = content.replace(
        'elif ctx.state == STATE_HANGAR:',
        'elif ctx.state == STATE_MISSION_BRIEFING:\n            self.ui_rects_cache = draw_mission_briefing(canvas, get_mission_data(self.pending_mission_id), ctx.scrap)\n        elif ctx.state == STATE_HANGAR:'
    )

with open('src/core/game.py', 'w', encoding='utf-8') as f:
    f.write(content)
