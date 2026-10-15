from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line, Ellipse, RoundedRectangle, InstructionGroup
import os
import math

# Fondo general oscuro
Window.clearcolor = (0.07, 0.09, 0.13, 1)

class TarjetaAncha(BoxLayout):
    def __init__(self, bg_color=(0.12, 0.15, 0.22, 1), radius=[12], **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
        self.bind(pos=self.actualizar_rect, size=self.actualizar_rect)

    def actualizar_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class PantallaCaratula(Screen):
    """Pantalla 1: Carátula de bienvenida con soporte para imagen de fondo (fondo_caratula.jpg)"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout principal de la carátula
        layout = BoxLayout(orientation='vertical', padding=24, spacing=20)
        
        # Verificamos si existe la imagen de fondo personalizada
        with self.canvas.before:
            self.bg_group = InstructionGroup()
            self.actualizar_fondo(self, self.size)
        self.bind(size=self.actualizar_fondo, pos=self.actualizar_fondo)

        # Tarjeta superior con título
        tarjeta_titulo = TarjetaAncha(bg_color=(0.08, 0.12, 0.2, 0.85), orientation='vertical', padding=20, spacing=15, size_hint_y=None, height=180)
        
        lbl_titulo = Label(
            text="[b][size=26sp]DISEÑO DE VIGAS[/size][/b]\n[color=4EA8DE][size=18sp]POR FLEXIÓN[/size][/color]",
            font_size='22sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            markup=True
        )
        lbl_titulo.bind(size=lbl_titulo.setter('text_size'))
        
        lbl_normas = Label(
            text="Norma Peruana NTE E.060  |  Código ACI 318",
            font_size='13sp',
            color=(0.75, 0.85, 0.95, 1),
            halign='center',
            valign='middle'
        )
        lbl_normas.bind(size=lbl_normas.setter('text_size'))

        tarjeta_titulo.add_widget(lbl_titulo)
        tarjeta_titulo.add_widget(lbl_normas)

        # Botón para ingresar a la calculadora
        btn_entrar = Button(
            text="INICIAR SISTEMA DE CÁLCULO",
            font_size='16sp',
            bold=True,
            background_normal='',
            background_color=(0.1, 0.65, 0.4, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=55
        )
        btn_entrar.bind(on_press=self.ir_a_calculadora)

        layout.add_widget(BoxLayout(size_hint_y=0.2)) # Espaciador superior
        layout.add_widget(tarjeta_titulo)
        layout.add_widget(BoxLayout(size_hint_y=0.4)) # Espaciador central
        layout.add_widget(btn_entrar)

        self.add_widget(layout)

    def actualizar_fondo(self, instance, value):
        self.bg_group.clear()
        with self.bg_group:
            if os.path.exists('fondo_caratula.jpg'):
                Color(1, 1, 1, 1)
                Rectangle(source='fondo_caratula.jpg', pos=self.pos, size=self.size)
            else:
                # Color sólido por defecto si aún no suben la imagen
                Color(0.07, 0.09, 0.13, 1)
                Rectangle(pos=self.pos, size=self.size)

    def ir_a_calculadora(self, instance):
        self.manager.current = 'calculadora'


class WidgetDeVigaAmplio(BoxLayout):
    """Widget gráfico con el acero inferior alineado tocando exactamente el estribo interior."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.b = 30.0
        self.h = 75.0
        self.num_barras_inf = 3
        self.estado_color = (0.1, 0.75, 0.4, 1)
        self.bind(pos=self.actualizar_dibujo, size=self.actualizar_dibujo)

    def actualizar_parametros(self, b, h, num_inf, cumple):
        self.b = max(10.0, float(b))
        self.h = max(10.0, float(h))
        self.num_barras_inf = max(2, int(num_inf))
        self.estado_color = (0.1, 0.75, 0.4, 1) if cumple else (0.9, 0.3, 0.3, 1)
        self.actualizar_dibujo()

    def actualizar_dibujo(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.09, 0.12, 0.18, 1)
            Rectangle(pos=self.pos, size=self.size)

            padding = 20
            w_disp = self.width - (padding * 2)
            h_disp = self.height - (padding * 2)
            
            if w_disp <= 0 or h_disp <= 0:
                return

            escala = min(w_disp / self.b, h_disp / self.h)
            viga_w = self.b * escala
            viga_h = self.h * escala
            
            viga_x = self.x + (self.width - viga_w) / 2
            viga_y = self.y + (self.height - viga_h) / 2

            # Contorno de Concreto
            Color(*self.estado_color)
            Line(rectangle=(viga_x, viga_y, viga_w, viga_h), width=4)

            # Estribo interior
            estribo_m = 7
            if viga_w > (estribo_m * 2) and viga_h > (estribo_m * 2):
                Color(0.5, 0.6, 0.7, 1)
                estribo_x = viga_x + estribo_m
                estribo_y = viga_y + estribo_m
                estribo_w = viga_w - (estribo_m * 2)
                estribo_h = viga_h - (estribo_m * 2)
                Line(rectangle=(estribo_x, estribo_y, estribo_w, estribo_h), width=1.8)
            else:
                return

            # Acero Inferior: Ajustado para que las barras de los extremos toquen exactamente los bordes del estribo
            radio = 6.0
            Color(0.95, 0.95, 0.95, 1) # Color acero brillante
            
            y_pos = estribo_y + 2 # Pegado al borde inferior del estribo
            
            if self.num_barras_inf == 2:
                xs_inf = [estribo_x + 2, estribo_x + estribo_w - (radio * 2) - 2]
            else:
                ancho_util = estribo_w - 4 - (radio * 2)
                paso_inf = ancho_util / (self.num_barras_inf - 1)
                xs_inf = [estribo_x + 2 + (i * paso_inf) for i in range(self.num_barras_inf)]

            for x_i in xs_inf:
                Ellipse(pos=(x_i, y_pos), size=(radio*2, radio*2))


class PantallaCalculadora(Screen):
    """Pantalla 2: Calculadora principal con ancho al 100%"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        root = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        main_layout = BoxLayout(orientation='vertical', padding=8, spacing=10, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Encabezado superior con botón para regresar a la carátula
        header_card = TarjetaAncha(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=12, spacing=6, size_hint_y=None)
        header_card.bind(minimum_height=header_card.setter('height'))
        
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=35)
        btn_volver = Button(
            text="← Menú",
            size_hint_x=None,
            width=80,
            background_color=(0.2, 0.25, 0.35, 1),
            color=(1, 1, 1, 1),
            font_size='13sp',
            bold=True
        )
        btn_volver.bind(on_press=self.regresar_caratula)
        top_bar.add_widget(btn_volver)
        top_bar.add_widget(Label(text="[b]DISEÑO DE VIGAS POR FLEXIÓN[/b]", font_size='14sp', color=(1,1,1,1), markup=True, halign='center'))
        header_card.add_widget(top_bar)
        main_layout.add_widget(header_card)

        # Formulario de Ingreso (Ancho Completo)
        form_card = TarjetaAncha(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=12, spacing=10, size_hint_y=None)
        form_card.bind(minimum_height=form_card.setter('height'))

        form_card.add_widget(Label(text="Norma de Diseño:", font_size='13sp', bold=True, color=(0.8, 0.85, 0.9, 1), size_hint_y=None, height=20, halign="left"))
        self.norma = Spinner(
            text='Norma Peruana NTE E.060', 
            values=('Norma Peruana NTE E.060', 'Código ACI 318'), 
            size_hint_y=None, 
            height=42, 
            font_size='14sp',
            background_color=(0.15, 0.3, 0.5, 1)
        )
        form_card.add_widget(self.norma)

        grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        fields = [
            ("Base b (cm):", "30"),
            ("Altura h (cm):", "75"),
            ("Peralte efectivo d (cm):", "69"),
            ("Concreto f'c (Kg/cm²):", "210"),
            ("Acero fy (Kg/cm²):", "4200"),
            ("Momento Último Mu (Tn·m):", "30"),
            ("Factor de reducción ø:", "0.9")
        ]

        self.inputs = {}
        for label_text, default_val in fields:
            lbl = Label(
                text=label_text,
                font_size='13sp',
                bold=True,
                color=(0.85, 0.9, 0.95, 1),
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=42
            )
            lbl.bind(size=lbl.setter('text_size'))
            
            inp = TextInput(
                text=default_val,
                multiline=False,
                input_filter='float',
                font_size='16sp',
                halign='center',
                background_color=(0.18, 0.22, 0.3, 1),
                foreground_color=(1, 1, 1, 1),
                size_hint_y=None,
                height=42,
                padding=[6, 8, 6, 8]
            )
            grid.add_widget(lbl)
            grid.add_widget(inp)
            self.inputs[label_text] = inp

        form_card.add_widget(grid)
        main_layout.add_widget(form_card)

        # Botón de Cálculo
        btn_calcular = Button(
            text="CALCULAR ACERO POR FLEXIÓN",
            font_size='16sp',
            bold=True,
            background_normal='',
            background_color=(0.1, 0.65, 0.4, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=50
        )
        btn_calcular.bind(on_press=self.ejecutar_diseno)
        main_layout.add_widget(btn_calcular)

        # Bloque Gráfico Dinámico (Ancho Completo)
        self.viga_canvas = WidgetDeVigaAmplio(size_hint_y=None, height=200)
        main_layout.add_widget(self.viga_canvas)

        # Tarjeta de Resultados
        self.res_card = TarjetaAncha(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=14, spacing=8, size_hint_y=None)
        self.res_card.bind(minimum_height=self.res_card.setter('height'))

        self.resultado_label = Label(
            text="[color=8899A6]Ingrese los parámetros y presione [CALCULAR ACERO POR FLEXIÓN][/color]",
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            halign="left",
            valign="top",
            markup=True,
            size_hint_y=None,
            height=260
        )
        self.resultado_label.bind(size=self.resultado_label.setter('text_size'))
        self.res_card.add_widget(self.resultado_label)
        main_layout.add_widget(self.res_card)

        root.add_widget(main_layout)
        self.add_widget(root)

    def regresar_caratula(self, instance):
        self.manager.current = 'caratula'

    def ejecutar_diseno(self, instance):
        try:
            b = float(self.inputs["Base b (cm):"].text)
            
            if b < 25.0:
                self.resultado_label.text = f"[color=FF6B6B][b]❌ RESTRICCIÓN NORMATIVA:[/b]\nLa base 'b' ingresada es {b} cm. El ancho mínimo permitido para vigas es [b]25 cm[/b].[/color]"
                self.viga_canvas.actualizar_parametros(b, float(self.inputs["Altura h (cm):"].text), 2, cumple=False)
                return

            h = float(self.inputs["Altura h (cm):"].text)
            d = float(self.inputs["Peralte efectivo d (cm):"].text)
            fc = float(self.inputs["Concreto f'c (Kg/cm²):"].text)
            fy = float(self.inputs["Acero fy (Kg/cm²):"].text)
            mu_tn = float(self.inputs["Momento Último Mu (Tn·m):"].text)
            phi = float(self.inputs["Factor de reducción ø:"].text)
            
            mu_kgcm = mu_tn * 100000.0
            k = mu_kgcm / (phi * fc * b * (d ** 2))
            
            if (1.0 - 2.36 * k) < 0:
                self.resultado_label.text = "[color=FF6B6B][b]❌ ERROR:[/b] Momento Mu excesivo para las dimensiones de la sección.[/color]"
                self.viga_canvas.actualizar_parametros(b, h, 2, cumple=False)
                return
                
            w = (1.0 - math.sqrt(1.0 - 2.36 * k)) / 1.18
            rho = w * (fc / fy)
            as_calculado = rho * b * d
            
            rho_min1 = (0.79 * math.sqrt(fc)) / fy
            rho_min2 = 14.0 / fy
            as_min_norma = max(rho_min1, rho_min2) * b * d
            
            beta1 = 0.85 if fc <= 280 else max(0.85 - (0.05 * (fc - 280) / 70), 0.65)
            rho_b = (0.85 * beta1 * fc / fy) * (6000 / (6000 + fy))
            
            if "E.060" in self.norma.text:
                rho_max = 0.75 * rho_b
                nombre_norma = "NTE E.060 (Perú)"
            else:
                rho_max = (0.85 * beta1 * fc / fy) * (0.003 / (0.003 + 0.004))
                nombre_norma = "ACI 318"
                
            as_max = rho_max * b * d
            as_diseno = max(as_calculado, as_min_norma)
            
            area_varilla = 1.99 
            num_inf = math.ceil(as_diseno / area_varilla)
            num_inf = max(2, num_inf)

            cumple = True
            if as_calculado > as_max:
                cumple = False

            self.viga_canvas.actualizar_parametros(b, h, num_inf, cumple=cumple)

            txt = f"[b][size=16sp][color=4EA8DE]RESULTADOS [{nombre_norma}][/color][/size][/b]\n"
            txt += f"[color=556677]────────────────────────────────────────[/color]\n"
            txt += f"• [color=CCD6F6]Parámetro K:[/color] [b]{k:.4f}[/b]   |   [color=CCD6F6]Parámetro w:[/color] [b]{w:.4f}[/b]\n"
            txt += f"• [color=CCD6F6]Acero Calculado:[/color] [b]{as_calculado:.2f} cm²[/b]\n"
            txt += f"• [color=CCD6F6]Acero Mín / Máx:[/color] [b]{as_min_norma:.2f} / {as_max:.2f} cm²[/b]\n\n"
            txt += f"[size=15sp]🔥 [color=FFFFFF]ACERO FINAL (Tracción):[/color] [b][color=4EA8DE]{as_diseno:.2f} cm²[/color][/b][/size]\n"
            txt += f"• [color=CCD6F6]Detalle Gráfico:[/color] [b]{num_inf} varillas inferiores (Tracción)[/b]\n\n"
            
            if as_calculado < as_min_norma:
                txt += "[color=FFD166][b]⚠️ NOTA: Se asignó el Acero Mínimo por norma.[/b][/color]"
            elif as_calculado > as_max:
                txt += "[color=FF6B6B][b]❌ ALERTA: ¡SECCIÓN SOBREFORZADA! Excede el máximo.[/b][/color]"
            else:
                txt += "[color=06D6A0][b]✅ DISEÑO CORRECTO: Cumple con la cuantía.[/b][/color]"
                
            self.resultado_label.text = txt
        except Exception as e:
            self.resultado_label.text = f"[color=FF6B6B][b]❌ Error en los datos:[/b] {str(e)}[/color]"


class CalculadoraDisenoVigaApp(App):
    def build(self):
        self.title = 'Diseño de Vigas por Flexión'
        sm = ScreenManager()
        sm.add_widget(PantallaCaratula(name='caratula'))
        sm.add_widget(PantallaCalculadora(name='calculadora'))
        return sm


if __name__ == '__main__':
    CalculadoraDisenoVigaApp().run()
