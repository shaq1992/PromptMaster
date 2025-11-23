import flet as ft
from prompt_blocks import PromptBlock

def main(page: ft.Page):
    # --- 1. App Configuration ---
    page.title = "PROMPT_MASTER_v1.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0 # Full screen gradient
    page.window_width = 700
    page.window_height = 900
    
    # Define the Retro 90s Neon Palette
    NEON_COLORS = {
        "role":        ft.colors.CYAN_400,
        "context":     ft.colors.PINK_500,
        "task":        ft.colors.LIME_400,
        "constraints": ft.colors.RED_500,
        "output":      ft.colors.PURPLE_400,
        "format":      ft.colors.TEAL_400,
        "examples":    ft.colors.AMBER_400,
        "default":     ft.colors.WHITE
    }
    
    app_state = {"last_main_key": "default"}
    COMMANDS = {
        "role": "ROLE", "context": "CONTEXT", "task": "TASK",
        "constraints": "CONSTRAINTS", "output": "OUTPUT",
        "format": "FORMAT", "examples": "EXAMPLES"
    }

    # --- 3. UI Components ---
    
    # A. The Header (Animated Container)
    # We use a mutable height to shrink it when typing starts
    header_title = ft.Text("PROMPT MASTER", size=50, weight="bold", color=ft.colors.CYAN_300, font_family="Courier New", text_align="center")
    header_tagline = ft.Text("ARCHITECT YOUR AI INTERACTIONS", size=16, color=ft.colors.PINK_300, font_family="Courier New", italic=True, text_align="center")
    
    header_container = ft.Container(
        content=ft.Column([
            ft.Icon(ft.icons.TERMINAL, size=40, color=ft.colors.LIME_400),
            header_title,
            header_tagline
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        
        alignment=ft.alignment.center,
        padding=20,
        height=300, # Initial "Hero" height
        animate=ft.animation.Animation(500, "easeOutCubic"), # Smooth slide up
    )

    # B. The Workspace
    blocks_column = ft.Column(scroll=ft.ScrollMode.HIDDEN, expand=True)

    suggestion_list = ft.ListView(height=0, spacing=2, padding=0)
    suggestion_container = ft.Container(
        content=suggestion_list,
        bgcolor=ft.colors.BLACK,
        visible=False,
        border=ft.border.all(1, ft.colors.GREEN_400),
        padding=0,
        margin=ft.margin.only(bottom=5),
        shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.GREEN_900)
    )

    # C. The Input (Retro Console Style)
    command_input = ft.TextField(
        hint_text="TYPE / TO INITIATE...",
        hint_style=ft.TextStyle(color=ft.colors.GREEN_900, font_family="Courier New"),
        bgcolor=ft.colors.BLACK,
        color=ft.colors.GREEN_400,
        cursor_color=ft.colors.GREEN_400,
        text_style=ft.TextStyle(font_family="Courier New", weight="bold"),
        expand=True,
        on_submit=lambda e: execute_command(),
        height=50,
        content_padding=15,
        border_color=ft.colors.GREEN_700,
        focused_border_color=ft.colors.GREEN_400,
        focused_border_width=2,
        border_radius=0 # Square
    )

    # --- 4. Logic Functions ---

    def toggle_ui_state():
        """Animates header based on whether content exists"""
        has_items = len(blocks_column.controls) > 0
        
        if has_items:
            header_container.height = 120 # Shrink to banner
            header_title.size = 28
            header_tagline.size = 12
            header_tagline.visible = True # Keep tagline!
        else:
            header_container.height = 300 # Grow to Hero
            header_title.size = 50
            header_tagline.size = 16
        
        check_fab_visibility()
        page.update()

    def check_fab_visibility():
        page.floating_action_button.visible = len(blocks_column.controls) > 0
        page.update()

    def generate_nested_xml():
        xml_output = []
        stack = [] 

        for block in blocks_column.controls:
            current_level = block.indent_level
            tag = block.tag_name.lower().replace(" ", "_")
            content = block.content_field.value.strip()

            while stack and stack[-1][1] >= current_level:
                closing_tag, _ = stack.pop()
                indent = "  " * len(stack)
                xml_output.append(f"{indent}</{closing_tag}>")

            indent_str = "  " * len(stack)
            xml_output.append(f"{indent_str}<{tag}>")
            
            if content:
                content_indent = indent_str + "  "
                formatted_content = "\n".join([f"{content_indent}{line}" for line in content.splitlines()])
                xml_output.append(formatted_content)

            stack.append((tag, current_level))

        while stack:
            closing_tag, _ = stack.pop()
            indent = "  " * len(stack)
            xml_output.append(f"{indent}</{closing_tag}>")

        return "\n".join(xml_output)

    def copy_to_clipboard(e):
        final_string = generate_nested_xml()
        page.set_clipboard(final_string)
        page.snack_bar = ft.SnackBar(ft.Text("DATA_COPIED_TO_CLIPBOARD", font_family="Courier New"))
        page.snack_bar.open = True
        page.update()

    def delete_block(block_instance):
        blocks_column.controls.remove(block_instance)
        toggle_ui_state()

    def focus_command_bar():
        command_input.focus()
        page.update()

    def add_block(tag_input, level):
        if level == 1:
            key_found = None
            for k in COMMANDS.keys():
                if tag_input.lower() == k:
                    key_found = k
                    break
            
            current_key = key_found if key_found else "default"
            app_state["last_main_key"] = current_key
            
            display_tag = COMMANDS.get(current_key, tag_input.upper())
            color = NEON_COLORS.get(current_key, NEON_COLORS["default"])
        else:
            display_tag = tag_input.upper()
            family_key = app_state["last_main_key"]
            color = NEON_COLORS.get(family_key, NEON_COLORS["default"])

        new_block = PromptBlock(
            tag_name=display_tag,
            border_color=color, # Pass the neon color as border
            delete_callback=delete_block,
            parent_focus_callback=focus_command_bar,
            indent_level=level
        )
        
        blocks_column.controls.append(new_block)
        command_input.value = ""
        suggestion_container.visible = False
        
        toggle_ui_state()
        new_block.focus()

    def on_input_change(e):
        val = command_input.value.strip().lower()
        
        if val.startswith("/") and not val.startswith("//"):
            search_term = val[1:] 
            matches = [k for k in COMMANDS.keys() if k.startswith(search_term)]
            
            if matches:
                suggestion_container.visible = True
                suggestion_list.controls.clear()
                suggestion_list.height = min(len(matches) * 45, 200)
                
                for m in matches:
                    color = NEON_COLORS[m]
                    suggestion_list.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Container(width=10, height=10, bgcolor=color), # Pixel dot
                                ft.Text(f"/{m}", size=16, color=ft.colors.GREEN_50, font_family="Courier New"),
                                ft.Text(f"<{COMMANDS[m]}>", size=12, color=ft.colors.GREEN_700, font_family="Courier New")
                            ]),
                            padding=10,
                            on_click=lambda _, cmd=m: add_block(cmd, 1),
                            ink=True,
                            bgcolor=ft.colors.BLACK
                        )
                    )
            else:
                suggestion_container.visible = False
        else:
            suggestion_container.visible = False
        
        page.update()

    def execute_command():
        val = command_input.value.strip()
        if not val: return

        if val.startswith("///"):
            custom_tag = val[3:].strip()
            if custom_tag: add_block(custom_tag, 3)
        
        elif val.startswith("//"):
            custom_tag = val[2:].strip()
            if custom_tag: add_block(custom_tag, 2)
        
        elif val.startswith("/"):
            if suggestion_container.visible and suggestion_list.controls:
                search_term = val[1:].lower()
                matches = [k for k in COMMANDS.keys() if k.startswith(search_term)]
                if matches: add_block(matches[0], 1)
            else:
                custom_tag = val[1:].strip()
                if custom_tag: add_block(custom_tag, 1)

    command_input.on_change = on_input_change

    # --- 5. FAB ---
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.icons.COPY,
        text="COPY PROMPT",
        bgcolor=ft.colors.PINK_600,
        shape=ft.RoundedRectangleBorder(radius=0), # Square button
        width=150,
        visible=False,
        on_click=copy_to_clipboard
    )

    # --- 6. Layout ---
    
    # We use a main container with a Gradient Background
    main_layout = ft.Container(
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[ft.colors.INDIGO_900, ft.colors.BLACK], # Synthwave Gradient
        ),
        expand=True,
        padding=20,
        content=ft.Column(
            controls=[
                header_container,   # Animated Header at top
                blocks_column,      # Content scrolls in middle
                suggestion_container, 
                ft.Row([
                    ft.Text(">", size=20, color=ft.colors.GREEN_400, font_family="Courier New", weight="bold"),
                    command_input
                ], alignment=ft.MainAxisAlignment.CENTER)
            ],
            spacing=0
        )
    )

    page.add(main_layout)

if __name__ == "__main__":
    ft.app(target=main)