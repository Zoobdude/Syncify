import flet as ft

class EntryPoint(ft.UserControl):
    def build(self):
        return(ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Text("SpotiSync"),
            ft.Container(content=ft.Column(controls=[
                ft.FilledButton(text="Create a Room"),
                ft.ElevatedButton(text="Join a Room")
            ],))
        ]))

    def create_room(self):
        pass
    
    def join_room(self):
        pass
    
def main(page: ft.Page):
    page.add(EntryPoint())

ft.app(target=main, view=ft.AppView.WEB_BROWSER)