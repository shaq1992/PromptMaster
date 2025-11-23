import flet as ft

class PromptBlock(ft.Column):
    def __init__(self, tag_name: str, delete_callback, parent_focus_callback, border_color: str, indent_level: int = 1):
        super().__init__()
        self.tag_name = tag_name
        self.delete_callback = delete_callback
        self.parent_focus_callback = parent_focus_callback
        self.border_color = border_color
        self.indent_level = indent_level
        
        # Indent logic
        self.left_margin = (self.indent_level - 1) * 40

        self.content_field = ft.TextField(
            multiline=True,
            min_lines=1 if indent_level > 1 else 3,
            border=ft.InputBorder.NONE,
            text_size=16,
            color=ft.colors.GREEN_50, # Retro Green Text
            cursor_color=ft.colors.GREEN_400,
            text_style=ft.TextStyle(font_family="Courier New"), # Monospace
            hint_text=f"// Enter {tag_name} data...",
            hint_style=ft.TextStyle(color=ft.colors.GREEN_900, font_family="Courier New"),
            on_submit=self.handle_shift_enter,
            shift_enter=True,
        )

    def build(self):
        is_child = self.indent_level > 1
        
        return ft.Container(
            content=ft.Column([
                # Header Row
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                self.tag_name.upper(), 
                                size=12 if is_child else 14, 
                                weight=ft.FontWeight.BOLD, 
                                color=ft.colors.BLACK,
                                font_family="Courier New"
                            ),
                            bgcolor=self.border_color, # The tag badge takes the neon color
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            border_radius=0, # Sharp 90s corners
                        ),
                        ft.IconButton(
                            icon=ft.icons.CLOSE_SHARP, # Sharp icon
                            icon_size=18, 
                            icon_color=self.border_color,
                            tooltip="DELETE_BLOCK",
                            on_click=lambda _: self.delete_callback(self)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                # The Text Input Area
                ft.Container(
                    content=self.content_field,
                    padding=ft.padding.only(left=5)
                )
            ]),
            bgcolor=ft.colors.BLACK, # Terminal Black background
            border=ft.border.all(2, self.border_color), # Thick Neon Border
            border_radius=0, # Boxy retro look
            padding=10 if is_child else 15,
            margin=ft.margin.only(bottom=15, left=self.left_margin),
            animate=ft.animation.Animation(300, "easeOut"),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=self.border_color, # Neon Glow effect
                offset=ft.Offset(0, 0),
            )
        )

    def handle_shift_enter(self, e):
        self.parent_focus_callback()

    def focus(self):
        self.content_field.focus()