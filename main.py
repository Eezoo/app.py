import flet as ft
def main(page: ft.Page):
    page.title = "Flet Counter Example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def increment_counter(e):
        counter.value += 1
        page.update()

    counter = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)
    increment_button = ft.IconButton(icon=ft.icons.ADD, on_click=increment_counter)

    page.add(counter, increment_button)

app = ft.app(target=main)
if __name__ == "__main__":
    app()
