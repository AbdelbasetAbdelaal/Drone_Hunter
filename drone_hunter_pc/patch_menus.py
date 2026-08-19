import re

with open('src/ui/menus.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Sector Status
sector_status = '''
        t_mark = "> " if is_selected else "  "
        s_text = font_card.render(f"{t_mark}SECTOR {s_id}: {sec['name']}", True, t_col)
        canvas.blit(s_text, (55, sy + 15))
        
        if is_completed:
            lk = font_card.render("[COMPLETED]", True, COLOR_EMERALD)
            canvas.blit(lk, (s_rect.right - lk.get_width() - 10, sy + 15))
        elif is_unlocked:
            lk = font_card.render("[AVAILABLE]", True, COLOR_CYAN)
            canvas.blit(lk, (s_rect.right - lk.get_width() - 10, sy + 15))
        else:
            lk = font_card.render("[LOCKED]", True, (150, 50, 50))
            canvas.blit(lk, (s_rect.right - lk.get_width() - 10, sy + 15))
            
        if is_unlocked:
'''
content = re.sub(r't_mark = "o" " if is_completed else \("> " if is_selected else ""\)\s+s_text = font_card\.render.*?if is_unlocked:', sector_status.strip() + '\n            ', content, flags=re.DOTALL)

# Fix Mission Status
mission_status = '''
        m_num = f"[{m['mission_number']:02d}] "
        m_name_surf = font_banner.render(f"{m_num}{m['name']}", True, t_col)
        canvas.blit(m_name_surf, (440, my_y + 15))
        
        if is_completed:
            st = font_card.render("[COMPLETED]", True, COLOR_EMERALD)
            canvas.blit(st, (m_rect.right - st.get_width() - 20, my_y + 25))
        elif is_unlocked:
            st = font_card.render("[AVAILABLE]", True, COLOR_CYAN)
            canvas.blit(st, (m_rect.right - st.get_width() - 20, my_y + 25))
            interactive_rects["missions"][m_id] = m_rect
        else:
            st = font_card.render("[LOCKED]", True, (150, 50, 50))
            canvas.blit(st, (m_rect.right - st.get_width() - 20, my_y + 25))
'''
content = re.sub(r't_mark = "o" " if is_completed else ""\s+m_num =.*?canvas\.blit\(st, \(m_rect\.right - 90, my_y \+ 25\)\)', mission_status.strip(), content, flags=re.DOTALL)

with open('src/ui/menus.py', 'w', encoding='utf-8') as f:
    f.write(content)
