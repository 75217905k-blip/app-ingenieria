import flet as ft

def main(page: ft.Page):
    page.title = "Prueba VSR Android"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    
    page.add(
        ft.Column([
            ft.Text("¡La aplicación abrió con éxito!", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400),
            ft.Text("El motor de Flet en Android está funcionando perfectamente.", size=14)
        ], alignment=ft.MainAxisAlignment.CENTER)
    )
