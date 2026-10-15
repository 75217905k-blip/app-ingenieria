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
from kivy.graphics import Color, Rectangle, Line, Ellipse, RoundedRectangle
import math

# Fondo general estilo panel tecnológico oscuro/elegante
Window.clearcolor = (0.07, 0.09, 0.13, 1)

class TarjetaDashboard(BoxLayout):
    def __init__(self, bg_color=(0.12, 0.15, 0.22, 1), radius=[16], **kwargs):
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


class WidgetDeVigaGigante(BoxLayout):
    """Widget gráfico interactivo gigante y detallado para visualizar claramente la sección y el acero inferior."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.b = 30.0
        self.h = 75.0
        self.num_barras_inf = 3  
        self.estado_color = (0.1, 0.75, 0.4, 1)
        self.bind(pos=self.actualizar_dibujo, size=self.actualizar_dibujo)

    def actualizar_parametros(self, b, h, num_inf, cumple):
        self.b = max(15.0, float(b))
        self.h = max(20.0, float(h))
        self.num_barras_inf = max(2, int(num_inf))
        self.estado_color = (0.1, 0.75, 0.4, 1) if cumple else (0.9, 0.3, 0.3, 1)
        self.actualizar_dibujo()

    def actualizar_dibujo(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.04, 0.06, 0.10, 1)
            Rectangle(pos=self.pos, size=self.size)

            # Márgenes mínimos para que el rectángulo de concreto sea lo más grande posible
            padding = 8
            w_disp = self.width - (padding * 2)
            h_disp = self.height - (padding * 2)
            
            if w_disp <= 0 or h_disp <= 0:
                return

            escala = min(w_disp / self.b, h_disp / self.h)
            viga_w = self.b * escala
            viga_h = self.h * escala
            
            viga_x = self.x + (self.width - viga_w) / 2
            viga_y = self.y + (self.height - viga_h) / 2

            # 1. Contorno exterior del concreto
            Color(*self.estado_color)
            Line(rectangle=(viga_x, viga_y, viga_w, viga_h), width=4.0)

            # 2. Estribo interior
            recubrimiento = max(4.0, 0.1 * viga_w)
            estribo_x = viga_x + recubrimiento
            estribo_y = viga_y + recubrimiento
            estribo_w = viga_w - (recubrimiento * 2)
            estribo_h = viga_h - (recubrimiento * 2)

            if estribo_w > 10 and estribo_h > 10:
                Color(0.4, 0.6, 0.85, 1)
                Line(rectangle=(estribo_x, estribo_y, estribo_w, estribo_h), width=2.0)

            # 3. Puntos de acero inferior más finos y estilizados
            radio = max(3.5, min(6.5, estribo_w / (self.num_barras_inf * 4.0)))
            Color(0.95, 0.98, 1.0, 1)
            
            y_pos = estribo_y + 4
            
            if self.num_barras_inf == 2:
                xs_inf = [estribo_x + 5, estribo_x + estribo_w - (radio * 2) - 5]
            else:
                ancho_util = estribo_w - 10 - (radio * 2)
                paso_inf = ancho_util / (self.num_barras_inf - 1)
                xs_inf = [estribo_x + 5 + (i * paso_inf) for i in range(self.num_barras_inf)]

            for x_i in xs_inf:
                Ellipse(pos=(x_i, y_pos), size=(radio * 2, radio * 2))


class PantallaCaratula(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=24, spacing=20)
        
        tarjeta = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=24, spacing=15, radius=[20])
        
        lbl_titulo = Label(
            text="[b]STRUCTURAL DASHBOARD[/b]\n[color=4EA8DE]DISEÑO DE VIGAS EN CONCRETO ARMADO[/color]",
            font_size='20sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            markup=True
        )
        lbl_titulo.bind(size=lbl_titulo.setter('text_size'))
        
        lbl_sub = Label(
            text="• Norma Técnica Peruana NTP E.060\n• Código ACI 318\n• Cálculo Exacto de Acero a Flexión",
            font_size='14sp',
            color=(0.7, 0.8, 0.9, 1),
            halign='center',
            valign='middle'
        )
        lbl_sub.bind(size=lbl_sub.setter('text_size'))

        tarjeta.add_widget(lbl_titulo)
        tarjeta.add_widget(lbl_sub)
        
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
        btn_entrar.bind(on_press=self.ir_a_calculo)

        layout.add_widget(BoxLayout(size_hint_y=0.15))
        layout.add_widget(tarjeta)
        layout.add_widget(btn_entrar)
        layout.add_widget(BoxLayout(size_hint_y=0.15))
        
        self.add_widget(layout)

    def ir_a_calculo(self, instance):
        self.manager.current = 'calculo'


class PantallaCalculo(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        root = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))

        # Barra Superior / Menú
        header_card = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='horizontal', padding=10, spacing=10, size_hint_y=None, height=50)
        btn_menu = Button(
            text="← MENÚ",
            font_size='12sp',
            bold=True,
            size_hint_x=0.3,
            background_normal='',
            background_color=(0.2, 0.25, 0.35, 1)
        )
        btn_menu.bind(on_press=self.regresar_caratula)
        header_card.add_widget(btn_menu)
        header_card.add_widget(Label(text="[b]PANEL DE CÁLCULO - VIGA[/b]", color=(1,1,1,1), markup=True, halign='center'))
        main_layout.add_widget(header_card)

        # Panel de Datos de Entrada
        form_card = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=12, spacing=8, size_hint_y=None)
        form_card.bind(minimum_height=form_card.setter('height'))

        form_card.add_widget(Label(text="Norma de Diseño:", font_size='13sp', bold=True, color=(0.8, 0.85, 0.9, 1), size_hint_y=None, height=20, halign="left"))
        self.norma = Spinner(
            text='NTP E.060 de Perú', 
            values=('NTP E.060 de Perú', 'Código ACI 318'), 
            size_hint_y=None, 
            height=40, 
            font_size='13sp',
            background_color=(0.15, 0.3, 0.5, 1)
        )
        form_card.add_widget(self.norma)

        grid = GridLayout(cols=2, spacing=8, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        fields = [
            ("Base b (cm) [Min 25]:", "30"),
            ("Altura h (cm):", "75"),
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
                color=(0.8, 0.85, 0.9, 1),
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=38
            )
            lbl.bind(size=lbl.setter('text_size'))
            
            inp = TextInput(
                text=default_val,
                multiline=False,
                input_filter='float',
                font_size='15sp',
                halign='center',
                background_color=(0.18, 0.22, 0.3, 1),
                foreground_color=(1, 1, 1, 1),
                size_hint_y=None,
                height=38,
                padding=[4, 6, 4, 6]
            )
            grid.add_widget(lbl)
            grid.add_widget(inp)
            self.inputs[label_text] = inp

        form_card.add_widget(grid)
        main_layout.add_widget(form_card)

        # Botón de cálculo
        btn_calcular = Button(
            text="▶ PROCESAR CÁLCULO DE ACERO",
            font_size='14sp',
            bold=True,
            background_normal='',
            background_color=(0.1, 0.65, 0.4, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=48
        )
        btn_calcular.bind(on_press=self.ejecutar_diseno)
        main_layout.add_widget(btn_calcular)

        # Bloque Gráfico Gigante Maximizado (altura de 400)
        self.viga_canvas = WidgetDeVigaGigante(size_hint_y=None, height=400)
        main_layout.add_widget(self.viga_canvas)

        # Tarjeta de Resultados Estilo Excel (Sin texto de cantidad de varillas)
        self.res_card = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=14, spacing=8, size_hint_y=None, height=200)
        
        self.resultado_label = Label(
            text="[color=667788]Ingrese los datos y presione [PROCESAR CÁLCULO][/color]",
            font_size='13sp',
            color=(0.9, 0.9, 0.9, 1),
            halign="left",
            valign="top",
            markup=True,
            size_hint_y=None,
            height=170
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
            b = float(self.inputs["Base b (cm) [Min 25]:"].text)
            
            if b < 25.0:
                self.resultado_label.text = f"[color=FF6B6B][b]❌ RESTRICCIÓN NORMATIVA (NTP E.060):[/b]\nLa base 'b' es {b} cm. El ancho mínimo es [b]25 cm[/b].[/color]"
                self.viga_canvas.actualizar_parametros(b, float(self.inputs["Altura h (cm):"].text), 2, cumple=False)
                return

            h = float(self.inputs["Altura h (cm):"].text)
            d = round(h - 6.0, 2)  # Peralte efectivo d = h - 6 con 2 decimales

            fc = float(self.inputs["Concreto f'c (Kg/cm²):"].text)
            fy = float(self.inputs["Acero fy (Kg/cm²):"].text)
            mu_tn = float(self.inputs["Momento Último Mu (Tn·m):"].text)
            phi = float(self.inputs["Factor de reducción ø:"].text)
            
            # K, w, rho con 4 decimales
            mu_kgcm = mu_tn * 100000.0
            k = round(mu_kgcm / (phi * fc * b * (d ** 2)), 4)
            
            if (1.0 - 2.36 * k) < 0:
                self.resultado_label.text = "[color=FF6B6B][b]❌ ERROR DE DISEÑO:[/b] Momento Mu excesivo para las dimensiones de la sección.[/color]"
                self.viga_canvas.actualizar_parametros(b, h, 2, cumple=False)
                return
                
            w = round((1.0 - math.sqrt(1.0 - 2.36 * k)) / 1.18, 4)
            rho = round(w * (fc / fy), 4)
            
            # As con 2 decimales
            as_calculado = round(rho * b * d, 2)
            
            # Acero Mínimo y Máximo
            rho_min = round((0.7 / 100.0) * math.sqrt(fc) / fy if "NTP E.060" in self.norma.text else (14.0 / fy), 4)
            as_min_norma = round(rho_min * b * d, 2)
            
            beta1 = 0.85 if fc <= 280 else max(0.85 - (0.05 * (fc - 280) / 70), 0.65)
            
            if "NTP E.060" in self.norma.text:
                rho_max = round(0.32 * beta1 * (fc / fy), 4)
                nombre_norma = "NTP E.060 de Perú"
            else:
                rho_max = round((0.85 * beta1 * fc / fy) * (0.003 / (0.003 + 0.004)), 4)
                nombre_norma = "ACI 318"
                
            as_max = round(rho_max * b * d, 2)
            as_diseno = round(max(as_calculado, as_min_norma), 2)
            
            # Cálculo interno de barras exclusivamente para renderizar los puntos finos en el gráfico gigante
            area_varilla = 1.99 
            num_inf = math.ceil(as_diseno / area_varilla)
            num_inf = max(2, num_inf)

            cumple = True
            if as_calculado > as_max:
                cumple = False

            self.viga_canvas.actualizar_parametros(b, h, num_inf, cumple=cumple)

            # Reporte limpio, directo y estrictamente con los datos de tus planillas Excel
            txt = f"[b][size=14sp][color=4EA8DE]RESULTADOS [{nombre_norma}][/color][/size][/b]\n"
            txt += f"• d (Peralte efectivo) = [b]{d:.2f} cm[/b] (h - 6)\n"
            txt += f"• K: [b]{k:.4f}[/b]  |  w: [b]{w:.4f}[/b]  |  ρ: [b]{rho:.4f}[/b]\n"
            txt += f"• ρmin: [b]{rho_min:.4f}[/b]  |  As min: [b]{as_min_norma:.2f} cm²[/b]\n"
            txt += f"• ρmax: [b]{rho_max:.4f}[/b]  |  As max: [b]{as_max:.2f} cm²[/b]\n"
            txt += f"[size=14sp]🔥 [color=FFFFFF]ACERO FINAL (As):[/color] [b][color=4EA8DE]{as_diseno:.2f} cm²[/color][/b][/size]"
            
            self.resultado_label.text = txt
        except Exception as e:
            self.resultado_label.text = f"[color=FF6B6B][b]❌ Error:[/b] {str(e)}[/color]"


class CalculadoraDisenoVigaApp(App):
    def build(self):
        self.title = 'Structural Dashboard - Viga Flexión'
        sm = ScreenManager()
        sm.add_widget(PantallaCaratula(name='caratula'))
        sm.add_widget(PantallaCalculo(name='calculo'))
        return sm


if __name__ == '__main__':
    CalculadoraDisenoVigaApp().run()
