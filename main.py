import flet as ft
from prompt_blocks import PromptBlock
import math

def main(page: ft.Page):
    # --- 1. App Configuration ---
    page.title = "PROMPT_MASTER_v1.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0 
    page.window_width = 800
    page.window_height = 900
    
    # Retro Palette
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

    # --- 2. UI Components ---
    
    # Header
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
        height=300, 
        animate=ft.animation.Animation(500, "easeOutCubic"), 
    )

    # Workspace
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
        border_radius=0 
    )

    # --- 3. Token Counter UI ---
    token_text = ft.Text(
        "[Token Count: 0]", 
        font_family="Courier New", 
        color=ft.colors.GREEN_400, 
        size=16, 
        weight="bold"
    )

    token_container = ft.Container(
        content=token_text,
        padding=ft.padding.symmetric(horizontal=15, vertical=10),
        border=ft.border.all(1, ft.colors.GREEN_900), 
        bgcolor=ft.colors.BLACK,
    )

    # --- 4. The Copy Button (Moved inside layout) ---
    copy_button = ft.ElevatedButton(
        text="COPY PROMPT",
        icon=ft.icons.COPY,
        bgcolor=ft.colors.PINK_600,
        color=ft.colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=0), # Retro Square
            padding=20,
        ),
        on_click=lambda e: copy_to_clipboard(e)
    )

    # Group Token Counter and Button together
    bottom_actions_row = ft.Row(
        controls=[
            token_container,
            ft.Container(width=10), # Gap between count and button
            copy_button
        ],
        alignment=ft.MainAxisAlignment.END,
        visible=False # Hidden initially
    )

    # --- 5. Logic Functions ---

    def calculate_tokens():
        """Iterates through all blocks and sums length"""
        total_chars = 0
        for block in blocks_column.controls:
            total_chars += len(block.content_field.value)
        
        # Standard estimation: 1 token ~= 4 chars
        est_tokens = math.ceil(total_chars / 4)
        token_text.value = f"[Token Count: {est_tokens}]"
        page.update()

    def toggle_ui_state():
        has_items = len(blocks_column.controls) > 0
        
        if has_items:
            header_container.height = 120 
            header_title.size = 28
            header_tagline.size = 12
            header_tagline.visible = True 
        else:
            header_container.height = 300 
            header_title.size = 50
            header_tagline.size = 16
        
        # Toggle The entire Bottom Row
        bottom_actions_row.visible = has_items
        
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
        calculate_tokens()
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
            border_color=color, 
            delete_callback=delete_block,
            parent_focus_callback=focus_command_bar,
            text_change_callback=calculate_tokens,
            indent_level=level
        )
        
        blocks_column.controls.append(new_block)
        command_input.value = ""
        suggestion_container.visible = False
        
        toggle_ui_state()
        new_block.focus()
        calculate_tokens()

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
                                ft.Container(width=10, height=10, bgcolor=color), 
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

    # --- 6. Layout ---
    main_layout = ft.Container(
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[ft.colors.INDIGO_900, ft.colors.BLACK], 
        ),
        expand=True,
        padding=20,
        content=ft.Column(
            controls=[
                header_container,   
                blocks_column,      
                suggestion_container, 
                ft.Row([
                    ft.Text(">", size=20, color=ft.colors.GREEN_400, font_family="Courier New", weight="bold"),
                    command_input
                ], alignment=ft.MainAxisAlignment.CENTER),
                # Bottom Action Bar
                ft.Container(height=10), # Margin
                bottom_actions_row
            ],
            spacing=0
        )
    )

    page.add(main_layout)

if __name__ == "__main__":
    ft.app(target=main)