import flet as ft
from prompt_blocks import PromptBlock
from snippet_manager import SnippetManager 
from llm_response import get_response
import math
import threading

def main(page: ft.Page):
    # --- 1. App Configuration ---
    page.title = "PROMPT_MASTER_v1.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0 
    page.window_width = 800
    page.window_height = 900
    
    snippet_mgr = SnippetManager()
    
    NEON_COLORS = {
        "role":        ft.colors.CYAN_400,
        "context":     ft.colors.PINK_500,
        "task":        ft.colors.LIME_400,
        "constraints": ft.colors.RED_500,
        "output":      ft.colors.PURPLE_400,
        "format":      ft.colors.TEAL_400,
        "examples":    ft.colors.AMBER_400,
        "default":     ft.colors.WHITE,
        "feedback":    ft.colors.GREEN_300
    }
    
    app_state = {
        "last_main_key": "default",
        "temp_save_block": None, 
        "active_snippet_block": None,
        "focused_block": None
    }
    
    COMMANDS = {
        "role": "ROLE", "context": "CONTEXT", "task": "TASK",
        "constraints": "CONSTRAINTS", "output": "OUTPUT",
        "format": "FORMAT", "examples": "EXAMPLES"
    }

    # --- 2. UI Components ---
    
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

    token_text = ft.Text("[Token Count: 0]", font_family="Courier New", color=ft.colors.GREEN_400, size=16, weight="bold")
    token_container = ft.Container(
        content=token_text,
        padding=ft.padding.symmetric(horizontal=15, vertical=10),
        border=ft.border.all(1, ft.colors.GREEN_900), 
        bgcolor=ft.colors.BLACK,
    )

    copy_button = ft.ElevatedButton(
        text="COPY PROMPT", icon=ft.icons.COPY, bgcolor=ft.colors.PINK_600, color=ft.colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0), padding=20),
        on_click=lambda e: copy_to_clipboard(e)
    )

    bottom_actions_row = ft.Row(
        controls=[token_container, ft.Container(width=10), copy_button],
        alignment=ft.MainAxisAlignment.END,
        visible=False 
    )
    
    # --- 3. Save Dialog ---
    snippet_name_field = ft.TextField(
        label="SNIPPET_NAME",
        autofocus=True,
        bgcolor=ft.colors.BLACK,
        color=ft.colors.GREEN_400,
        border_color=ft.colors.GREEN_400,
        text_style=ft.TextStyle(font_family="Courier New"),
        on_submit=lambda e: finalize_save_snippet()
    )
    
    save_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("SAVE SNIPPET TO LIBRARY", font_family="Courier New", color=ft.colors.CYAN_400),
        content=ft.Container(height=80, content=snippet_name_field),
        actions=[
            ft.TextButton("CANCEL", on_click=lambda e: close_dialog()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=ft.colors.GREY_900,
        shape=ft.RoundedRectangleBorder(radius=0)
    )

    # --- 4. Logic Functions ---

    def calculate_tokens():
        total_chars = 0
        for block in blocks_column.controls:
            total_chars += len(block.content_field.value)
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
        if app_state["focused_block"] == block_instance:
            app_state["focused_block"] = None
        calculate_tokens()
        toggle_ui_state()

    # --- Snippet Logic ---

    def track_focus(block_instance):
        app_state["focused_block"] = block_instance

    def handle_keyboard_events(e: ft.KeyboardEvent):
        if e.ctrl and e.key == " ":
            block = app_state["focused_block"]
            if block:
                initiate_load_snippet(block)

    def initiate_save_snippet(block_instance):
        content = block_instance.content_field.value.strip()
        if not content:
            page.snack_bar = ft.SnackBar(ft.Text("ERROR: BLOCK_EMPTY", font_family="Courier New"))
            page.snack_bar.open = True
            page.update()
            return
            
        app_state["temp_save_block"] = block_instance
        snippet_name_field.value = "" 
        page.dialog = save_dialog
        save_dialog.open = True
        page.update()

    def finalize_save_snippet():
        name = snippet_name_field.value.strip()
        block = app_state["temp_save_block"]
        
        if name and block:
            success = snippet_mgr.save_snippet(
                section_tag=block.tag_name, 
                name=name, 
                content=block.content_field.value
            )
            if success:
                page.snack_bar = ft.SnackBar(ft.Text(f"SNIPPET '{name}' SAVED!", font_family="Courier New"))
            else:
                page.snack_bar = ft.SnackBar(ft.Text("ERROR_SAVING_SNIPPET", font_family="Courier New"))
        
        close_dialog()
        page.snack_bar.open = True
        page.update()

    def close_dialog():
        save_dialog.open = False
        page.update()

    def insert_snippet(content):
        block = app_state["active_snippet_block"]
        if block:
            current_text = block.content_field.value
            if current_text:
                block.content_field.value = current_text + "\n" + content
            else:
                block.content_field.value = content
            
            block.focus()
            suggestion_container.visible = False
            calculate_tokens()
            page.update()

    def initiate_load_snippet(block_instance):
        app_state["active_snippet_block"] = block_instance
        tag = block_instance.tag_name
        
        snippets = snippet_mgr.load_snippets(tag)
        
        if snippets:
            suggestion_container.visible = True
            suggestion_list.controls.clear()
            suggestion_list.height = min(len(snippets) * 45, 200)
            
            color = block_instance.border_color
            
            for snip in snippets:
                suggestion_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.FLASH_ON, color=color, size=16),
                            ft.Text(snip['name'], size=16, color=ft.colors.GREEN_50, font_family="Courier New"),
                            ft.Text(f"[{len(snip['content'])} chars]", size=12, color=ft.colors.GREY_500, font_family="Courier New")
                        ]),
                        padding=10,
                        on_click=lambda _, c=snip['content']: insert_snippet(c),
                        ink=True,
                        bgcolor=ft.colors.BLACK
                    )
                )
        else:
             page.snack_bar = ft.SnackBar(ft.Text("NO_SNIPPETS_FOUND_FOR_SECTION", font_family="Courier New"))
             page.snack_bar.open = True
        
        page.update()

    def focus_command_bar():
        command_input.focus()
        app_state["focused_block"] = None 
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
            save_request_callback=initiate_save_snippet,
            snippet_request_callback=initiate_load_snippet,
            on_focus_callback=track_focus,
            indent_level=level
        )
        
        blocks_column.controls.append(new_block)
        command_input.value = ""
        suggestion_container.visible = False
        
        toggle_ui_state()
        new_block.focus()
        app_state["focused_block"] = new_block 
        calculate_tokens()
        
        # --- RETURN THE BLOCK (Crucial for AI Injection) ---
        return new_block

    def on_input_change(e):
        val = command_input.value.strip().lower()
        if val.startswith("/") and not val.startswith("//") and not val.startswith("/forge"):
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

    # --- AI FUNCTIONS ---
    def run_forge(archetype_text):
        """Runs in a separate thread to prevent UI freezing"""
        try:
            # 1. Construct the Meta-Prompt
            system_prompt = f"""
            Act as an expert Prompt Engineer.
            Generate a detailed, high-quality System Role (Persona) based on this brief description: "{archetype_text}".
            
            Requirements:
            1. Start directly with "You are..."
            2. Define the Tone, Style, and Philosophy of the persona.
            3. Keep it under 150 words.
            4. Be specific and distinct.
            """
            
            # 2. Call the API
            generated_role = get_response(system_prompt)
            
            # 3. Create Block & Inject (Must be done on Main Thread via page.run_task ideally, 
            # but Flet handles UI updates from threads reasonably well if we don't create controls in thread)
            # We will use a helper to update UI safely
            page.run_thread(lambda: inject_forge_result(generated_role))
            
        except Exception as e:
            print(f"Forge Error: {e}")
            command_input.value = "ERROR: FORGE_FAILED"
            command_input.disabled = False
            page.update()

    def inject_forge_result(text):
        """Called after API returns"""
        # Create the ROLE block
        new_block = add_block("role", 1)
        
        # Inject text
        new_block.content_field.value = text.strip()
        
        # Reset UI
        command_input.disabled = False
        command_input.value = ""
        command_input.hint_text = "TYPE / TO INITIATE..."
        command_input.update()
        
        # Update Tokens
        calculate_tokens()
        page.update()


    def execute_command():
        val = command_input.value.strip()
        if not val: return

        # --- NEW: FORGE COMMAND ---
        if val.startswith("/forge "):
            # Extract the archetype text (remove '/forge ' which is 7 chars)
            archetype = val[7:].strip().replace('"', '') # Strip quotes if user used them
            if archetype:
                # UI Feedback
                command_input.value = "INITIALIZING NEURAL LINK..."
                command_input.disabled = True
                page.update()
                
                # Run API call in background thread so app doesn't freeze
                threading.Thread(target=run_forge, args=(archetype,), daemon=True).start()
            return
        # ---------------------------

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
    page.on_keyboard_event = handle_keyboard_events

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
                ft.Container(height=10),
                bottom_actions_row
            ],
            spacing=0
        )
    )

    page.add(main_layout)

if __name__ == "__main__":
    ft.app(target=main)