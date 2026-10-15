from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line, Ellipse
import math

# Color de fondo general
Window.clearcolor = (0.95, 0.96, 0.98, 1)

class WidgetDeViga(BoxLayout):
    """Widget personalizado para dibujar la sección transversal de la viga de forma dinámica."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.b = 30.0
        self.h = 75.0
        self.estado_color = (0.05, 0.55, 0.35, 1) # Verde por defecto
        self.bind(pos=self.actualizar_dibujo, size=self.actualizar_dibujo)

    def actualizar_parametros(self, b, h, cumple):
        self.b = max(10.0, float(b))
        self.h = max(10.0, float(h))
        # Si cumple es True -> Verde, si es False -> Rojo
        self.estado_color = (0.05, 0.55, 0.35, 1) if cumple else (0.85, 0.2, 0.2, 1)
        self.actualizar_dibujo()

    def actualizar_dibujo(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Fondo blanco interno de la tarjeta de dibujo
            Color(1, 1, 1, 1)
            Rectangle(pos=self.pos, size=self.size)

            # Calcular escala para centrar la viga en el espacio asignado
            padding = 45
            w_disp = self.width - (padding * 2)
            h_disp = self.height - (padding * 2)
            
            if w_disp <= 0 or h_disp <= 0:
                return

            # Relación de aspecto para mantener proporciones reales
            escala = min(w_disp / self.b, h_disp / self.h)
            
            viga_w = self.b * escala
            viga_h = self.h * escala
            
            viga_x = self.x + (self.width - viga_w) / 2
            viga_y = self.y + (self.height - viga_h) / 2

            # 1. Dibujar contorno de concreto de la viga
            Color(*self.estado_color)
            Line(rectangle=(viga_x, viga_y, viga_w, viga_h), width=3)

            # Estribo interior aproximado
            estribo_margen = 8
            if viga_w > (estribo_margen * 2) and viga_h > (estribo_margen * 2):
                Color(0.4, 0.4, 0.4, 1)
                Line(rectangle=(viga_x + estribo_margen, viga_y + estribo_margen, 
                                viga_w - (estribo_margen * 2), viga_h - (estribo_margen * 2)), width=1.5)

            # 2. Dibujar barras de acero inferiores y superiores (representación visual)
            radio_barra = 5
            # Acero Superior (2 barras)
            Color(0.2, 0.2, 0.2, 1)
            Ellipse(pos=(viga_x + estribo_margen + 4, viga_y + viga_h - estribo_margen - 14), size=(radio_barra*2, radio_barra*2))
            Ellipse(pos=(viga_x + viga_w - estribo_margen - 14, viga_y + viga_h - estribo_margen - 14), size=(radio_barra*2, radio_barra*2))

            # Acero Inferior (3 barras)
            Ellipse(pos=(viga_x + estribo_margen + 4, viga_y + estribo_margen + 4), size=(radio_barra*2, radio_barra*2))
            Ellipse(pos=(viga_x + viga_w/2 - radio_barra, viga_y + estribo_margen + 4), size=(radio_barra*2, radio_barra*2))
            Ellipse(pos=(viga_x + viga_w - estribo_margen - 14, viga_y + estribo_margen + 4), size=(radio_barra*2, radio_barra*2))


class CalculadoraDisenoViga(App):
    def build(self):
        self.title = 'Diseño de Vigas - Cuantías'
        
        root = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        layout = BoxLayout(orientation='vertical', padding=16, spacing=14, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # Título Principal
        layout.add_widget(Label(
            text="DISEÑO DE VIGA (FALLA DÚCTIL)", 
            font_size='18sp', 
            bold=True, 
            color=(0.1, 0.15, 0.25, 1), 
            size_hint_y=None, 
            height=40
        ))
        
        # Selector de Norma
        layout.add_widget(Label(text="Norma de Diseño:", font_size='15sp', bold=True, color=(0.2, 0.25, 0.3, 1), size_hint_y=None, height=22, halign="left"))
        self.norma = Spinner(
            text='Norma Peruana NTE E.060', 
            values=('Norma Peruana NTE E.060', 'Código ACI 318'), 
            size_hint_y=None, 
            height=44, 
            font_size='15sp',
            background_color=(0.08, 0.18, 0.36, 1)
        )
        layout.add_widget(self.norma)
        
        # Campos de entrada
        self.b_input = self.crear_campo(layout, "Base b (cm):", "30")
        self.h_input = self.crear_campo(layout, "Altura h (cm):", "75")
        self.d_input = self.crear_campo(layout, "Peralte efectivo d (cm):", "69")
        self.fc_input = self.crear_campo(layout, "Concreto f'c (Kg/cm²):", "210")
        self.fy_input = self.crear_campo(layout, "Acero fy (Kg/cm²):", "4200")
        self.mu_input = self.crear_campo(layout, "Momento Último Mu (Tn·m):", "30")
        self.phi_input = self.crear_campo(layout, "Factor de reducción ø:", "0.9")
        
        # Botón de Cálculo
        btn_calcular = Button(
            text="CALCULAR ACERO", 
            font_size='17sp', 
            bold=True, 
            background_normal='',
            background_color=(0.05, 0.55, 0.35, 1), 
            color=(1, 1, 1, 1),
            size_hint_y=None, 
            height=50
        )
        btn_calcular.bind(on_press=self.ejecutar_diseno)
        layout.add_widget(btn_calcular)

        # ---------------- WIDGET GRÁFICO DE LA VIGA ----------------
        layout.add_widget(Label(text="CORTE TRANSVERSAL DINÁMICO:", font_size='14sp', bold=True, color=(0.2, 0.25, 0.3, 1), size_hint_y=None, height=20, halign="left"))
        self.viga_canvas = WidgetDeViga(size_hint_y=None, height=180)
        layout.add_widget(self.viga_canvas)
        
        # Etiqueta de Resultados
        self.resultado_label = Label(
            text="[color=666666]Ingrese los parámetros y presione CALCULAR ACERO[/color]", 
            font_size='15sp', 
            color=(0.1, 0.1, 0.1, 1), 
            halign="left", 
            valign="top", 
            markup=True,
            size_hint_y=None, 
            height=260
        )
        self.resultado_label.bind(size=self.resultado_label.setter('text_size'))
        layout.add_widget(self.resultado_label)
        
        root.add_widget(layout)
        return root

    def crear_campo(self, layout, texto_label, por_defecto):
        layout.add_widget(Label(text=texto_label, font_size='15sp', bold=True, color=(0.2, 0.25, 0.3, 1), size_hint_y=None, height=22, halign="left"))
        txt_input = TextInput(
            text=por_defecto, 
            input_filter='float', 
            multiline=False, 
            font_size='16sp',
            halign='center',
            size_hint_y=None, 
            height=42
        )
        layout.add_widget(txt_input)
        return txt_input

    def ejecutar_diseno(self, instance):
        try:
            b = float(self.b_input.text)
            h = float(self.h_input.text)
            d = float(self.d_input.text)
            fc = float(self.fc_input.text)
            fy = float(self.fy_input.text)
            mu_tn = float(self.mu_input.text)
            phi = float(self.phi_input.text)
            
            mu_kgcm = mu_tn * 100000.0
            k = mu_kgcm / (phi * fc * b * (d ** 2))
            
            if (1.0 - 2.36 * k) < 0:
                self.resultado_label.text = "[color=D32F2F][b]❌ ERROR:[/b] El momento Mu es excesivo para las dimensiones de la sección.[/color]"
                self.viga_canvas.actualizar_parametros(b, h, cumple=False)
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
            
            # Validar estado para el color del gráfico
            cumple = True
            if as_calculado > as_max:
                cumple = False

            # Actualizar dibujo de la viga en pantalla
            self.viga_canvas.actualizar_parametros(b, h, cumple=cumple)

            # Construir texto de resultados enriquecido
            txt = f"[b][size=16sp][color=0F172A]RESULTADOS [{nombre_norma}]:[/color][/size][/b]\n\n"
            txt += f"• Parámetro K: [b]{k:.4f}[/b]\n"
            txt += f"• Parámetro w: [b]{w:.4f}[/b]\n"
            txt += f"• Cuantía (ρ): [b]{rho:.4f}[/b]\n\n"
            txt += f"• Acero Calculado: [b]{as_calculado:.2f} cm²[/b]\n"
            txt += f"• Acero Mínimo: [b]{as_min_norma:.2f} cm²[/b]\n"
            txt += f"• Acero Máximo: [b]{as_max:.2f} cm²[/b]\n\n"
            txt += f"[size=17sp]🔥 [color=0F172A]ACERO FINAL:[/color] [b][color=1E3A8A]{as_diseno:.2f} cm²[/color][/b][/size]\n\n"
            
            if as_calculado < as_min_norma:
                txt += "[color=D4AF37][b]⚠️ NOTA: Se asignó el Acero Mínimo por norma.[/b][/color]"
            elif as_calculado > as_max:
                txt += "[color=D32F2F][b]❌ ALERTA: ¡SECCIÓN SOBREFORZADA! Excede el máximo.[/b][/color]"
            else:
                txt += "[color=388E3C][b]✅ DISEÑO CORRECTO: Cumple con la cuantía.[/b][/color]"
                
            self.resultado_label.text = txt
        except Exception as e:
            self.resultado_label.text = f"[color=D32F2F][b]❌ Error en los datos:[/b] {str(e)}[/color]"

if __name__ == '__main__':
    CalculadoraDisenoViga().run()
