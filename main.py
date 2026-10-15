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


class WidgetDeViga(BoxLayout):
    """Widget gráfico interactivo que dibuja la sección de concreto, estribos y acero real (tracción y compresión)."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.b = 30.0
        self.h = 75.0
        self.num_barras_inf = 3  # Tracción inferior
        self.num_barras_sup = 2  # Compresión / Montaje superior (Mínimo normativo: 2)
        self.estado_color = (0.1, 0.75, 0.4, 1)
        self.bind(pos=self.actualizar_dibujo, size=self.actualizar_dibujo)

    def actualizar_parametros(self, b, h, num_inf, num_sup, cumple):
        self.b = max(10.0, float(b))
        self.h = max(10.0, float(h))
        self.num_barras_inf = max(2, int(num_inf)) # Mínimo 2 varillas por norma
        self.num_barras_sup = max(2, int(num_sup)) # Mínimo 2 varillas de montaje arriba
        self.estado_color = (0.1, 0.75, 0.4, 1) if cumple else (0.9, 0.3, 0.3, 1)
        self.actualizar_dibujo()

    def actualizar_dibujo(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Fondo del panel gráfico
            Color(0.09, 0.12, 0.18, 1)
            Rectangle(pos=self.pos, size=self.size)

            padding = 30
            w_disp = self.width - (padding * 2)
            h_disp = self.height - (padding * 2)
            
            if w_disp <= 0 or h_disp <= 0:
                return

            escala = min(w_disp / self.b, h_disp / self.h)
            viga_w = self.b * escala
            viga_h = self.h * escala
            
            viga_x = self.x + (self.width - viga_w) / 2
            viga_y = self.y + (self.height - viga_h) / 2

            # 1. Contorno exterior de concreto
            Color(*self.estado_color)
            Line(rectangle=(viga_x, viga_y, viga_w, viga_h), width=3.5)

            # 2. Estribo interior
            estribo_m = 6
            if viga_w > (estribo_m * 2) and viga_h > (estribo_m * 2):
                Color(0.5, 0.6, 0.7, 1)
                Line(rectangle=(viga_x + estribo_m, viga_y + estribo_m, 
                                viga_w - (estribo_m * 2), viga_h - (estribo_m * 2)), width=1.5)

            # 3. Dibujo Dinámico de Acero Superior (Compresión / Montaje)
            radio = 4.5
            Color(0.9, 0.9, 0.9, 1) # Color acero
            
            # Distribución superior
            if self.num_barras_sup == 2:
                xs_sup = [viga_x + estribo_m + 3, viga_x + viga_w - estribo_m - 12]
            else:
                paso_sup = (viga_w - (estribo_m * 2) - 18) / (self.num_barras_sup - 1)
                xs_sup = [viga_x + estribo_m + 3 + (i * paso_sup) for i in range(self.num_barras_sup)]
            
            for x_s in xs_sup:
                Ellipse(pos=(x_s, viga_y + viga_h - estribo_m - 12), size=(radio*2, radio*2))

            # 4. Dibujo Dinámico de Acero Inferior (Tracción)
            if self.num_barras_inf == 2:
                xs_inf = [viga_x + estribo_m + 3, viga_x + viga_w - estribo_m - 12]
            else:
                paso_inf = (viga_w - (estribo_m * 2) - 18) / (self.num_barras_inf - 1)
                xs_inf = [viga_x + estribo_m + 3 + (i * paso_inf) for i in range(self.num_barras_inf)]

            for x_i in xs_inf:
                Ellipse(pos=(x_i, viga_y + estribo_m + 3), size=(radio*2, radio*2))


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
            text="• Norma Peruana NTE E.060\n• Código ACI 318\n• Detallado de Acero en Tracción y Compresión",
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
        btn_entrar.bind(on_press=self.ir_a_etapa1)

        layout.add_widget(BoxLayout(size_hint_y=0.15))
        layout.add_widget(tarjeta)
        layout.add_widget(btn_entrar)
        layout.add_widget(BoxLayout(size_hint_y=0.15))
        
        self.add_widget(layout)

    def ir_a_etapa1(self, instance):
        self.manager.current = 'etapa1'


class PantallaEtapa1(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        root = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        main_layout = BoxLayout(orientation='vertical', padding=14, spacing=14, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        lbl_step = Label(
            text="[color=4EA8DE][b]ETAPA 1 DE 2:[/b][/color] Parámetros Geométricos y Materiales",
            font_size='15sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=30,
            halign='left',
            markup=True
        )
        lbl_step.bind(size=lbl_step.setter('text_size'))
        main_layout.add_widget(lbl_step)

        form_card = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=14, spacing=12, size_hint_y=None)
        form_card.bind(minimum_height=form_card.setter('height'))

        form_card.add_widget(Label(text="Norma de Diseño:", font_size='14sp', bold=True, color=(0.8, 0.85, 0.9, 1), size_hint_y=None, height=20, halign="left"))
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
            ("Base b (cm) [Min 25]:", "30"),
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
                padding=[4, 8, 4, 8]
            )
            grid.add_widget(lbl)
            grid.add_widget(inp)
            self.inputs[label_text] = inp

        form_card.add_widget(grid)
        main_layout.add_widget(form_card)

        btn_siguiente = Button(
            text="PROCESAR Y VER RESULTADOS →",
            font_size='16sp',
            bold=True,
            background_normal='',
            background_color=(0.1, 0.65, 0.4, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=50
        )
        btn_siguiente.bind(on_press=self.calcular_y_avanzar)
        main_layout.add_widget(btn_siguiente)

        btn_volver = Button(
            text="← VOLVER AL MENÚ",
            font_size='14sp',
            background_normal='',
            background_color=(0.2, 0.25, 0.35, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=42
        )
        btn_volver.bind(on_press=self.regresar_caratula)
        main_layout.add_widget(btn_volver)

        root.add_widget(main_layout)
        self.add_widget(root)

    def regresar_caratula(self, instance):
        self.manager.current = 'caratula'

    def calcular_y_avanzar(self, instance):
        pantalla_res = self.manager.get_screen('etapa2')
        pantalla_res.ejecutar_calculos(self.inputs, self.norma.text)
        self.manager.current = 'etapa2'


class PantallaEtapa2(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        root = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        main_layout = BoxLayout(orientation='vertical', padding=14, spacing=14, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        lbl_step = Label(
            text="[color=4EA8DE][b]ETAPA 2 DE 2:[/b][/color] Resultados y Detallado de Acero",
            font_size='15sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=30,
            halign='left',
            markup=True
        )
        lbl_step.bind(size=lbl_step.setter('text_size'))
        main_layout.add_widget(lbl_step)

        # Gráfico dinámico con tracción y compresión
        self.viga_canvas = WidgetDeViga(size_hint_y=None, height=200)
        main_layout.add_widget(self.viga_canvas)

        self.res_card = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=14, spacing=8, size_hint_y=None)
        self.res_card.bind(minimum_height=self.res_card.setter('height'))

        self.resultado_label = Label(
            text="Esperando datos...",
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            halign="left",
            valign="top",
            markup=True,
            size_hint_y=None,
            height=280
        )
        self.resultado_label.bind(size=self.resultado_label.setter('text_size'))
        self.res_card.add_widget(self.resultado_label)
        main_layout.add_widget(self.res_card)

        btn_atras = Button(
            text="← MODIFICAR PARÁMETROS (ETAPA 1)",
            font_size='14sp',
            bold=True,
            background_normal='',
            background_color=(0.2, 0.3, 0.45, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=48
        )
        btn_atras.bind(on_press=self.regresar_etapa1)
        main_layout.add_widget(btn_atras)

        root.add_widget(main_layout)
        self.add_widget(root)

    def regresar_etapa1(self, instance):
        self.manager.current = 'etapa1'

    def ejecutar_calculos(self, inputs, norma_text):
        try:
            b = float(inputs["Base b (cm) [Min 25]:"].text)
            
            # RESTRICCIÓN NORMATIVA: Base mínima 25 cm
            if b < 25.0:
                self.resultado_label.text = f"[color=FF6B6B][b]❌ RESTRICCIÓN NORMATIVA (NTE E.060):[/b]\nLa base 'b' es {b} cm. El ancho mínimo permitido es [b]25 cm[/b]. Regrese a la Etapa 1.[/color]"
                self.viga_canvas.actualizar_parametros(b, float(inputs["Altura h (cm):"].text), 2, 2, cumple=False)
                return

            h = float(inputs["Altura h (cm):"].text)
            d = float(inputs["Peralte efectivo d (cm):"].text)
            fc = float(inputs["Concreto f'c (Kg/cm²):"].text)
            fy = float(inputs["Acero fy (Kg/cm²):"].text)
            mu_tn = float(inputs["Momento Último Mu (Tn·m):"].text)
            phi = float(inputs["Factor de reducción ø:"].text)
            
            mu_kgcm = mu_tn * 100000.0
            k = mu_kgcm / (phi * fc * b * (d ** 2))
            
            if (1.0 - 2.36 * k) < 0:
                self.resultado_label.text = "[color=FF6B6B][b]❌ ERROR:[/b] Momento Mu excesivo para las dimensiones de la sección.[/color]"
                self.viga_canvas.actualizar_parametros(b, h, 2, 2, cumple=False)
                return
                
            w = (1.0 - math.sqrt(1.0 - 2.36 * k)) / 1.18
            rho = w * (fc / fy)
            as_calculado = rho * b * d
            
            rho_min1 = (0.79 * math.sqrt(fc)) / fy
            rho_min2 = 14.0 / fy
            as_min_norma = max(rho_min1, rho_min2) * b * d
            
            beta1 = 0.85 if fc <= 280 else max(0.85 - (0.05 * (fc - 280) / 70), 0.65)
            rho_b = (0.85 * beta1 * fc / fy) * (6000 / (6000 + fy))
            
            if "E.060" in norma_text:
                rho_max = 0.75 * rho_b
                nombre_norma = "NTE E.060 (Perú)"
            else:
                rho_max = (0.85 * beta1 * fc / fy) * (0.003 / (0.003 + 0.004))
                nombre_norma = "ACI 318"
                
            as_max = rho_max * b * d
            as_diseno = max(as_calculado, as_min_norma)
            
            # Criterio ingenieril para calcular número de varillas (Asumimos varilla de 5/8" -> Área = 1.99 cm² o 3/4" -> 2.85 cm²)
            # Usaremos una aproximación práctica con varillas de 3/4" (2.85 cm²) o 5/8" (1.99 cm²) para el gráfico:
            area_varilla_inferior = 1.99 # Aprox varilla de 5/8" (1.27 cm de radio aprox o 1.58cm diámetro)
            num_inf = math.ceil(as_diseno / area_varilla_inferior)
            num_inf = max(2, num_inf) # Mínimo normativo de 2 varillas inferiores

            # Acero de compresión superior (por norma se coloca al menos un tercio del inferior o mínimo 2 varillas de montaje)
            num_sup = max(2, math.ceil(num_inf / 2))

            cumple = True
            if as_calculado > as_max:
                cumple = False

            # Actualizar dibujo con barras de tracción y compresión
            self.viga_canvas.actualizar_parametros(b, h, num_inf, num_sup, cumple=cumple)

            txt = f"[b][size=15sp][color=4EA8DE]RESULTADOS [{nombre_norma}]:[/color][/size][/b]\n\n"
            txt += f"• Parámetro K: [b]{k:.4f}[/b] | Parámetro w: [b]{w:.4f}[/b]\n"
            txt += f"• Acero Calculado: [b]{as_calculado:.2f} cm²[/b]\n"
            txt += f"• Acero Mínimo / Máximo: [b]{as_min_norma:.2f} / {as_max:.2f} cm²[/b]\n\n"
            txt += f"[size=16sp]🔥 [color=FFF]ACERO FINAL (Tracción):[/color] [b][color=4EA8DE]{as_diseno:.2f} cm²[/b][/size]\n"
            txt += f"• Detallado Gráfico: [b]{num_inf} varillas inf. (Tracción) | {num_sup} varillas sup. (Compresión)[/b]\n\n"
            
            if as_calculado < as_min_norma:
                txt += "[color=FFD166][b]⚠️ NOTA: Se asignó el Acero Mínimo por norma.[/b][/color]"
            elif as_calculado > as_max:
                txt += "[color=FF6B6B][b]❌ ALERTA: ¡SECCIÓN SOBREFORZADA! Excede el máximo.[/b][/color]"
            else:
                txt += "[color=06D6A0][b]✅ DISEÑO CORRECTO: Cumple con la cuantía y ductilidad.[/b][/color]"
                
            self.resultado_label.text = txt
        except Exception as e:
            self.resultado_label.text = f"[color=FF6B6B][b]❌ Error en los datos:[/b] {str(e)}[/color]"


class CalculadoraDisenoVigaApp(App):
    def build(self):
        self.title = 'Structural Dashboard - NTE E.060'
        sm = ScreenManager()
        sm.add_widget(PantallaCaratula(name='caratula'))
        sm.add_widget(PantallaEtapa1(name='etapa1'))
        sm.add_widget(PantallaEtapa2(name='etapa2'))
        return sm


if __name__ == '__main__':
    CalculadoraDisenoVigaApp().run()
