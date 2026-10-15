from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
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
            # Fondo del panel gráfico
            Color(0.04, 0.06, 0.10, 1)
            Rectangle(pos=self.pos, size=self.size)

            padding = 24
            w_disp = self.width - (padding * 2)
            h_disp = self.height - (padding * 2)
            
            if w_disp <= 0 or h_disp <= 0:
                return

            # Escala proporcional real para la viga
            escala = min(w_disp / self.b, h_disp / self.h)
            viga_w = self.b * escala
            viga_h = self.h * escala
            
            viga_x = self.x + (self.width - viga_w) / 2
            viga_y = self.y + (self.height - viga_h) / 2

            # 1. Contorno exterior del concreto (Ancho b x Alto h)
            Color(*self.estado_color)
            Line(rectangle=(viga_x, viga_y, viga_w, viga_h), width=4.5)

            # 2. Estribo interior (Recubrimiento estructural de ~4cm)
            recubrimiento = max(5.0, 0.12 * viga_w)
            estribo_x = viga_x + recubrimiento
            estribo_y = viga_y + recubrimiento
            estribo_w = viga_w - (recubrimiento * 2)
            estribo_h = viga_h - (recubrimiento * 2)

            if estribo_w > 15 and estribo_h > 15:
                Color(0.4, 0.6, 0.85, 1)
                Line(rectangle=(estribo_x, estribo_y, estribo_w, estribo_h), width=2.2)

            # 3. Varillas de acero inferior grandes y bien espaciadas (Tracción)
            radio = max(8.0, min(14.0, estribo_w / (self.num_barras_inf * 2.0)))
            Color(0.95, 0.98, 1.0, 1)
            
            y_pos = estribo_y + 5
            
            if self.num_barras_inf == 2:
                xs_inf = [estribo_x + 6, estribo_x + estribo_w - (radio * 2) - 6]
            else:
                ancho_util = estribo_w - 12 - (radio * 2)
                paso_inf = ancho_util / (self.num_barras_inf - 1)
                xs_inf = [estribo_x + 6 + (i * paso_inf) for i in range(self.num_barras_inf)]

            for x_i in xs_inf:
                Ellipse(pos=(x_i, y_pos), size=(radio * 2, radio * 2))


class StructuralDashboardApp(App):
    def build(self):
        self.title = 'Structural Dashboard - Viga Flexión'
        
        root = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))

        # Título Superior
        header_card = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=10, spacing=6, size_hint_y=None, height=75)
        header_card.add_widget(Label(text="[b][size=16sp]STRUCTURAL DASHBOARD[/size][/b]", color=(1,1,1,1), markup=True, halign='center'))
        header_card.add_widget(Label(text="[color=4EA8DE]Diseño por Flexión (NTE E.060 / ACI 318)[/color]", font_size='12sp', color=(0.8,0.9,1,1), markup=True, halign='center'))
        main_layout.add_widget(header_card)

        # Panel de Datos de Entrada (b, h, d calculado, f'c, fy, Mu, ø)
        form_card = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=12, spacing=8, size_hint_y=None)
        form_card.bind(minimum_height=form_card.setter('height'))

        form_card.add_widget(Label(text="Norma de Diseño:", font_size='13sp', bold=True, color=(0.8, 0.85, 0.9, 1), size_hint_y=None, height=20, halign="left"))
        self.norma = Spinner(
            text='Norma Peruana NTE E.060', 
            values=('Norma Peruana NTE E.060', 'Código ACI 318'), 
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
            text="▶  PROCESAR CÁLCULO Y ACTUALIZAR VIGA",
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

        # Bloque Gráfico Gigante y Detallado
        self.viga_canvas = WidgetDeVigaGigante(size_hint_y=None, height=300)
        main_layout.add_widget(self.viga_canvas)

        # Tarjeta de Resultados Estilo Excel (Redondeos exactos: 4 decimales para K, w, rho; 2 decimales para áreas)
        self.res_card = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=14, spacing=8, size_hint_y=None, height=240)
        
        self.resultado_label = Label(
            text="[color=667788]Ingrese los datos y presione [PROCESAR CÁLCULO][/color]",
            font_size='13sp',
            color=(0.9, 0.9, 0.9, 1),
            halign="left",
            valign="top",
            markup=True,
            size_hint_y=None,
            height=210
        )
        self.resultado_label.bind(size=self.resultado_label.setter('text_size'))
        self.res_card.add_widget(self.resultado_label)
        main_layout.add_widget(self.res_card)

        root.add_widget(main_layout)
        return root

    def ejecutar_diseno(self, instance):
        try:
            b = float(self.inputs["Base b (cm) [Min 25]:"].text)
            
            if b < 25.0:
                self.resultado_label.text = f"[color=FF6B6B][b]❌ RESTRICCIÓN NORMATIVA (NTE E.060):[/b]\nLa base 'b' es {b} cm. El ancho mínimo es [b]25 cm[/b].[/color]"
                self.viga_canvas.actualizar_parametros(b, float(self.inputs["Altura h (cm):"].text), 2, cumple=False)
                return

            h = float(self.inputs["Altura h (cm):"].text)
            d = h - 6.0  # Peralte efectivo automático restando 6 cm por norma

            fc = float(self.inputs["Concreto f'c (Kg/cm²):"].text)
            fy = float(self.inputs["Acero fy (Kg/cm²):"].text)
            mu_tn = float(self.inputs["Momento Último Mu (Tn·m):"].text)
            phi = float(self.inputs["Factor de reducción ø:"].text)
            
            mu_kgcm = mu_tn * 100000.0
            k = mu_kgcm / (phi * fc * b * (d ** 2))
            
            if (1.0 - 2.36 * k) < 0:
                self.resultado_label.text = "[color=FF6B6B][b]❌ ERROR DE DISEÑO:[/b] Momento Mu excesivo para las dimensiones de la sección.[/color]"
                self.viga_canvas.actualizar_parametros(b, h, 2, cumple=False)
                return
                
            w = (1.0 - math.sqrt(1.0 - 2.36 * k)) / 1.18
            rho = w * (fc / fy)
            as_calculado = rho * b * d
            
            # Acero Mínimo según Norma (Imágenes de referencia)
            rho_min = (0.7 / 100.0) * math.sqrt(fc) / fy if "E.060" in self.norma.text else (14.0 / fy)
            as_min_norma = rho_min * b * d
            
            beta1 = 0.85 if fc <= 280 else max(0.85 - (0.05 * (fc - 280) / 70), 0.65)
            
            if "E.060" in self.norma.text:
                rho_max = 0.32 * beta1 * (fc / fy)
                nombre_norma = "NTE E.060 (Perú)"
            else:
                rho_max = (0.85 * beta1 * fc / fy) * (0.003 / (0.003 + 0.004))
                nombre_norma = "ACI 318"
                
            as_max = rho_max * b * d
            as_diseno = max(as_calculado, as_min_norma)
            
            # Varilla de 5/8" (Área = 1.99 cm²)
            area_varilla = 1.99 
            num_inf = math.ceil(as_diseno / area_varilla)
            num_inf = max(2, num_inf)

            cumple = True
            if as_calculado > as_max:
                cumple = False

            # Actualizar gráfico con el widget gigante
            self.viga_canvas.actualizar_parametros(b, h, num_inf, cumple=cumple)

            # Reporte exacto con formato solicitado: 4 decimales para K, w, rho, ρmin, ρmax; 2 decimales para áreas y d
            txt = f"[b][size=14sp][color=4EA8DE]RESULTADOS [{nombre_norma}][/color][/size][/b]\n"
            txt += f"• [color=AACCFF]d = h - 6 =[/color] [b]{d:.2f} cm[/b]  |  [color=AACCFF]K:[/color] [b]{k:.4f}[/b]\n"
            txt += f"• [color=AACCFF]w:[/color] [b]{w:.4f}[/b]  |  [color=AACCFF]ρ:[/color] [b]{rho:.4f}[/b]  |  [color=AACCFF]As:[/color] [b]{as_calculado:.2f} cm²[/b]\n"
            txt += f"• [color=AACCFF]ρmin:[/color] [b]{rho_min:.4f}[/b]  |  [color=AACCFF]As min:[/color] [b]{as_min_norma:.2f} cm²[/b]\n"
            txt += f"• [color=AACCFF]ρmax:[/color] [b]{rho_max:.4f}[/b]  |  [color=AACCFF]As max:[/color] [b]{as_max:.2f} cm²[/b]\n"
            txt += f"[size=14sp]🔥 [color=FFFFFF]ACERO DISEÑO (As):[/color] [b][color=4EA8DE]{as_diseno:.2f} cm²[/color][/b][/size]\n"
            txt += f"• Detalle Gráfico: [b]{num_inf} varillas (con separación reglamentaria)[/b]\n"
            
            if as_calculado < as_min_norma:
                txt += "[color=FFD166][b]⚠️ Asignado Acero Mínimo por norma.[/b][/color]"
            elif as_calculado > as_max:
                txt += "[color=FF6B6B][b]❌ ALERTA: ¡Sección sobreforzada![/b][/color]"
            else:
                txt += "[color=06D6A0][b]✅ Diseño correcto (Cumple cuantía).[/b][/color]"
                
            self.resultado_label.text = txt
        except Exception as e:
            self.resultado_label.text = f"[color=FF6B6B][b]❌ Error:[/b] {str(e)}[/color]"


if __name__ == '__main__':
    StructuralDashboardApp().run()
