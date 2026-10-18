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

# TABLA DE ACEROS OFICIAL (Barra, Pulgadas, Area cm2, Diametro cm)
TABLA_ACEROS = [
    ("#2", "1/4\"", 0.32, 0.64),
    ("#3", "3/8\"", 0.71, 0.95),
    ("#4", "1/2\"", 1.27, 1.27),
    ("#5", "5/8\"", 1.98, 1.59),
    ("#6", "3/4\"", 2.85, 1.91),
    ("#8", "1\"", 5.07, 2.54),
    ("#9", "1 1/8\"", 6.42, 2.86),
    ("#10", "1 1/4\"", 7.94, 3.18)
]

class TarjetaDashboard(BoxLayout):
    def __init__(self, bg_color=(0.12, 0.15, 0.22, 1), radius=[14], **kwargs):
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


class WidgetDeVigaSimetrica(BoxLayout):
    """Widget gráfico interactivo con distribución simétrica de aceros."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.b = 30.0
        self.h = 65.0
        self.num_p = 2
        self.num_r = 0
        self.estado_color = (0.1, 0.75, 0.4, 1)
        self.bind(pos=self.actualizar_dibujo, size=self.actualizar_dibujo)

    def actualizar_parametros(self, b, h, num_p, num_r, cumple):
        self.b = max(15.0, float(b))
        self.h = max(20.0, float(h))
        self.num_p = max(2, int(num_p))
        self.num_r = max(0, int(num_r))
        self.estado_color = (0.1, 0.75, 0.4, 1) if cumple else (0.9, 0.3, 0.3, 1)
        self.actualizar_dibujo()

    def actualizar_dibujo(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.04, 0.06, 0.10, 1)
            Rectangle(pos=self.pos, size=self.size)

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

            # 1. Contorno del concreto
            Color(*self.estado_color)
            Line(rectangle=(viga_x, viga_y, viga_w, viga_h), width=3.0)

            # 2. Estribo interior
            recubrimiento = max(4.0, 0.1 * viga_w)
            estribo_x = viga_x + recubrimiento
            estribo_y = viga_y + recubrimiento
            estribo_w = viga_w - (recubrimiento * 2)
            estribo_h = viga_h - (recubrimiento * 2)

            if estribo_w > 10 and estribo_h > 10:
                Color(0.4, 0.6, 0.85, 1)
                Line(rectangle=(estribo_x, estribo_y, estribo_w, estribo_h), width=1.5)

            # 3. Distribución Simétrica: Principales en extremos
            total_b = self.num_p + self.num_r
            total_b = max(2, total_b)
            radio = max(3.5, min(6.5, estribo_w / (total_b * 4.0)))
            y_pos = estribo_y + 4
            
            ancho_util = estribo_w - 10 - (radio * 2)
            if total_b == 2:
                xs = [estribo_x + 5, estribo_x + estribo_w - (radio * 2) - 5]
                tipos = ['P', 'P']
            else:
                paso = ancho_util / (total_b - 1)
                xs = [estribo_x + 5 + (i * paso) for i in range(total_b)]
                tipos = ['R'] * total_b
                tipos[0] = 'P'
                tipos[-1] = 'P'
                p_colocados = 2
                idx = 1
                while p_colocados < self.num_p and idx < total_b - 1:
                    tipos[idx] = 'P'
                    tipos[-(idx+1)] = 'P'
                    p_colocados += 2
                    idx += 1

            for x_i, tipo in zip(xs, tipos):
                if tipo == 'P':
                    Color(0.2, 0.65, 1.0, 1)  # Azul principal
                else:
                    Color(1.0, 0.55, 0.1, 1)  # Naranja refuerzo
                Ellipse(pos=(x_i, y_pos), size=(radio * 2, radio * 2))


class PantallaCaratula(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=24, spacing=20)
        
        tarjeta = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=24, spacing=15, radius=[20])
        
        lbl_titulo = Label(
            text="[b]STRUCTURAL DASHBOARD[/b]\n[color=4EA8DE]DISEÑO DE VIGAS - VSR & DETALLADO[/color]",
            font_size='20sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            markup=True
        )
        lbl_titulo.bind(size=lbl_titulo.setter('text_size'))
        
        lbl_sub = Label(
            text="• Hoja 1: Datos, Coeficientes y Cuantías (Mín / Máx)\n• Hoja 2: Diseño por Momento Positivo (+)\n• Hoja 3: Diseño por Momento Negativo (-)",
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
        btn_entrar.bind(on_press=self.ir_a_hoja1)

        layout.add_widget(BoxLayout(size_hint_y=0.15))
        layout.add_widget(tarjeta)
        layout.add_widget(btn_entrar)
        layout.add_widget(BoxLayout(size_hint_y=0.15))
        
        self.add_widget(layout)

    def ir_a_hoja1(self, instance):
        self.manager.current = 'hoja1'


class BaseHojaScreen(Screen):
    """Clase base para mantener la navegación superior."""
    def __init__(self, titulo_hoja, **kwargs):
        super().__init__(**kwargs)
        self.root_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        nav_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=5)
        
        btn_h1 = Button(text="1. Coef. y Cuantías", background_color=(0.2, 0.3, 0.5, 1), background_normal='', bold=True, font_size='12sp')
        btn_h2 = Button(text="2. Momento (+)", background_color=(0.2, 0.3, 0.5, 1), background_normal='', bold=True, font_size='12sp')
        btn_h3 = Button(text="3. Momento (-)", background_color=(0.3, 0.5, 0.3, 1), background_normal='', bold=True, font_size='12sp')
        
        btn_h1.bind(on_press=lambda x: setattr(self.manager, 'current', 'hoja1'))
        btn_h2.bind(on_press=lambda x: setattr(self.manager, 'current', 'hoja2'))
        btn_h3.bind(on_press=lambda x: setattr(self.manager, 'current', 'hoja3'))
        
        nav_layout.add_widget(btn_h1)
        nav_layout.add_widget(btn_h2)
        nav_layout.add_widget(btn_h3)
        
        self.root_layout.add_widget(nav_layout)


class Hoja1DatosCoeficientes(BaseHojaScreen):
    """Hoja 1: Datos, Coeficientes y Cuantías Mínimas/Máximas."""
    def __init__(self, **kwargs):
        super().__init__("Hoja 1", **kwargs)
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        header = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='horizontal', padding=10, size_hint_y=None, height=45)
        header.add_widget(Label(text="[b]HOJA 1: DATOS, COEFICIENTES Y CUANTÍAS[/b]", color=(1,1,1,1), markup=True, halign='center'))
        content.add_widget(header)

        # Formulario de Entrada
        form_card = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=12, spacing=8, size_hint_y=None)
        form_card.bind(minimum_height=form_card.setter('height'))

        form_card.add_widget(Label(text="Norma de Diseño:", font_size='13sp', bold=True, color=(0.8, 0.85, 0.9, 1), size_hint_y=None, height=20, halign="left"))
        self.norma = Spinner(text='NTP E.060 de Perú', values=('NTP E.060 de Perú', 'Código ACI 318'), size_hint_y=None, height=40, font_size='13sp', background_color=(0.15, 0.3, 0.5, 1))
        form_card.add_widget(self.norma)

        grid = GridLayout(cols=2, spacing=8, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        fields = [
            ("Base b (cm) [Min 25]:", "25"),
            ("Altura h (cm):", "65"),
            ("Concreto f'c (Kg/cm²):", "280"),
            ("Acero fy (Kg/cm²):", "4200"),
            ("Momento Mu (+) (Tn·m):", "37.54"),
            ("Momento Mu (-) (Tn·m):", "17.54"),
            ("Factor de reducción ø:", "0.9")
        ]

        self.inputs = {}
        for label_text, default_val in fields:
            lbl = Label(text=label_text, font_size='13sp', bold=True, color=(0.8, 0.85, 0.9, 1), halign='left', valign='middle', size_hint_y=None, height=38)
            lbl.bind(size=lbl.setter('text_size'))
            inp = TextInput(text=default_val, multiline=False, input_filter='float', font_size='15sp', halign='center', background_color=(0.18, 0.22, 0.3, 1), foreground_color=(1, 1, 1, 1), size_hint_y=None, height=38, padding=[4, 6, 4, 6])
            grid.add_widget(lbl)
            grid.add_widget(inp)
            self.inputs[label_text] = inp

        form_card.add_widget(grid)
        content.add_widget(form_card)

        btn_calc = Button(text="▶ CALCULAR COEFICIENTES Y CUANTÍAS", font_size='14sp', bold=True, background_normal='', background_color=(0.1, 0.65, 0.4, 1), color=(1, 1, 1, 1), size_hint_y=None, height=48)
        btn_calc.bind(on_press=self.calcular_coeficientes)
        content.add_widget(btn_calc)

        self.res_card = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=14, spacing=8, size_hint_y=None, height=440)
        self.resultado_label = Label(text="[color=667788]Ingrese los datos y presione calcular para ver coeficientes y cuantías.[/color]", font_size='13sp', color=(0.9, 0.9, 0.9, 1), halign="left", valign="top", markup=True, size_hint_y=None, height=410)
        self.resultado_label.bind(size=self.resultado_label.setter('text_size'))
        self.res_card.add_widget(self.resultado_label)
        content.add_widget(self.res_card)

        scroll.add_widget(content)
        self.root_layout.add_widget(scroll)
        self.add_widget(self.root_layout)

    def calcular_coeficientes(self, instance):
        try:
            b = float(self.inputs["Base b (cm) [Min 25]:"].text)
            h = float(self.inputs["Altura h (cm):"].text)
            d = round(h - 6.0, 2)
            fc = float(self.inputs["Concreto f'c (Kg/cm²):"].text)
            fy = float(self.inputs["Acero fy (Kg/cm²):"].text)
            mu_pos = float(self.inputs["Momento Mu (+) (Tn·m):"].text)
            mu_neg = float(self.inputs["Momento Mu (-) (Tn·m):"].text)
            phi = float(self.inputs["Factor de reducción ø:"].text)
            is_e060 = "NTP E.060" in self.norma.text

            # 1. Coeficientes Mu(+) y Mu(-)
            k_p = round((mu_pos * 100000.0) / (phi * fc * b * (d ** 2)), 4)
            w_p = round((1.0 - math.sqrt(max(0.0, 1.0 - 2.36 * k_p))) / 1.18, 4)
            rho_p = round(w_p * fc / fy, 4)
            as_p = round(rho_p * b * d, 2)

            k_n = round((mu_neg * 100000.0) / (phi * fc * b * (d ** 2)), 4)
            w_n = round((1.0 - math.sqrt(max(0.0, 1.0 - 2.36 * k_n))) / 1.18, 4)
            rho_n = round(w_n * fc / fy, 4)
            as_n = round(rho_n * b * d, 2)

            # 2. Cuantías Límites y Áreas (Mínimo / Máximo) exactas a tus celdas de Excel
            rho_min = round((0.71 * math.sqrt(fc)) / fy if is_e060 else (14.0 / fy), 4)[cite: 28]
            as_min = round(rho_min * b * d, 2)[cite: 28]

            beta1 = 0.85 if fc <= 280 else max(0.85 - (0.05 * (fc - 280) / 70), 0.65)
            rho_max = round(0.32 * 0.85 * (fc / fy) if is_e060 else (0.85 * beta1 * fc / fy) * (0.003 / 0.007), 4)[cite: 28]
            as_max = round(rho_max * b * d, 2)[cite: 28]

            cumple_p = "CUMPLE" if rho_min < rho_p < rho_max else "NO CUMPLE"[cite: 28]
            cumple_n = "CUMPLE" if rho_min < rho_n < rho_max else "NO CUMPLE"[cite: 28]

            # Formato idéntico al cuadro de Excel de la figura
            txt = f"[b][size=13sp][color=4EA8DE]CÁLCULO DEL ÁREA DEL ACERO Y COEFICIENTES[/color][/size][/b]\n"
            txt += f"• Peralte efectivo d = [b]{d:.2f} cm[/b] (h - 6)\n"
            txt += f"  [color=AACCFF]Mu(+) -> K: {k_p:.4f} | w: {w_p:.4f} | ρ: {rho_p:.4f} | As: {as_p:.2f} cm²[/color]\n"
            txt += f"  [color=AACCFF]Mu(-) -> K: {k_n:.4f} | w: {w_n:.4f} | ρ: {rho_n:.4f} | As: {as_n:.2f} cm²[/color]\n\n"

            txt += f"[b][color=FFD166]── CÁLCULO CUANTÍA (MÍNIMO / MÁXIMO) ──[/color][/b]\n"[cite: 28]
            txt += f"  • [b]ρmin[/b]  = [b]{rho_min:.4f}[/b]\n"[cite: 28]
            txt += f"  • [b]As min[/b] = [b][color=4EA8DE]{as_min:.2f} cm²[/color][/b]\n"[cite: 28]
            txt += f"  • [b]ρmax[/b]  = [b]{rho_max:.4f}[/b]\n"[cite: 28]
            txt += f"  • [b]As max[/b] = [b][color=4EA8DE]{as_max:.2f} cm²[/color][/b]\n\n"[cite: 28]

            txt += f"[b][color=FFD166]── VALIDACIÓN DE CUANTÍAS ──[/color][/b]\n"
            txt += f"  • [b]Mu(+):[/b] {rho_min:.4f} < [b]{rho_p:.4f}[/b] < {rho_max:.4f}  ->  [b][color={'06D6A0' if cumple_p=='CUMPLE' else 'FF6B6B'}]{cumple_p}[/color][/b]\n"[cite: 28]
            txt += f"  • [b]Mu(-):[/b] {rho_min:.4f} < [b]{rho_n:.4f}[/b] < {rho_max:.4f}  ->  [b][color={'06D6A0' if cumple_n=='CUMPLE' else 'FF6B6B'}]{cumple_n}[/color][/b]"[cite: 28]

            self.resultado_label.text = txt
        except Exception as e:
            self.resultado_label.text = f"[color=FF6B6B][b]❌ Error:[/b] {str(e)}[/color]"


class Hoja2MomentoPositivo(BaseHojaScreen):
    """Hoja 2: Detallado y Diseño de Acero para Momento Positivo (+)."""
    def __init__(self, **kwargs):
        super().__init__("Hoja 2", **kwargs)
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        header = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='horizontal', padding=10, size_hint_y=None, height=45)
        header.add_widget(Label(text="[b]HOJA 2: DISEÑO Y DETALLADO - MOMENTO POSITIVO (+)[/b]", color=(1,1,1,1), markup=True, halign='center'))
        content.add_widget(header)

        btn_proc = Button(text="▶ PROCESAR DISEÑO MOMENTO (+)", font_size='14sp', bold=True, background_normal='', background_color=(0.1, 0.65, 0.4, 1), color=(1, 1, 1, 1), size_hint_y=None, height=48)
        btn_proc.bind(on_press=self.procesar_positivo)
        content.add_widget(btn_proc)

        self.viga_canvas = WidgetDeVigaSimetrica(size_hint_y=None, height=280)
        content.add_widget(self.viga_canvas)

        self.res_card = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=14, spacing=8, size_hint_y=None, height=380)
        self.resultado_label = Label(text="[color=667788]Presione el botón para procesar el momento positivo.[/color]", font_size='13sp', color=(0.9, 0.9, 0.9, 1), halign="left", valign="top", markup=True, size_hint_y=None, height=350)
        self.resultado_label.bind(size=self.resultado_label.setter('text_size'))
        self.res_card.add_widget(self.resultado_label)
        content.add_widget(self.res_card)

        scroll.add_widget(content)
        self.root_layout.add_widget(scroll)
        self.add_widget(self.root_layout)

    def buscar_combinacion(self, area_objetivo):
        mejor = None
        min_dif = 999999.0
        for barra, pulg, unit, diam in TABLA_ACEROS:
            for cant in range(2, 6):
                total = cant * unit
                if total >= area_objetivo:
                    dif = total - area_objetivo
                    if dif < min_dif:
                        min_dif = dif
                        mejor = (cant, barra, pulg, total, diam)
        return mejor if mejor else (2, "#8", "1\"", 10.14, 2.54)

    def procesar_positivo(self, instance):
        app = App.get_running_app()
        h1 = app.root.get_screen('hoja1')
        try:
            b = float(h1.inputs["Base b (cm) [Min 25]:"].text)
            h = float(h1.inputs["Altura h (cm):"].text)
            d = round(h - 6.0, 2)
            fc = float(h1.inputs["Concreto f'c (Kg/cm²):"].text)
            fy = float(h1.inputs["Acero fy (Kg/cm²):"].text)
            mu = float(h1.inputs["Momento Mu (+) (Tn·m):"].text)
            phi = float(h1.inputs["Factor de reducción ø:"].text)
            is_e060 = "NTP E.060" in h1.norma.text

            k = round((mu * 100000.0) / (phi * fc * b * (d ** 2)), 4)
            w = round((1.0 - math.sqrt(max(0.0, 1.0 - 2.36 * k))) / 1.18, 4)
            rho = round(w * fc / fy, 4)
            as_calc = round(rho * b * d, 2)

            rho_min = round((0.71 * math.sqrt(fc)) / fy if is_e060 else (14.0 / fy), 4)[cite: 28]
            as_min = round(rho_min * b * d, 2)[cite: 28]
            beta1 = 0.85 if fc <= 280 else max(0.85 - (0.05 * (fc - 280) / 70), 0.65)
            rho_max = round(0.32 * 0.85 * (fc / fy) if is_e060 else (0.85 * beta1 * fc / fy) * (0.003 / 0.007), 4)[cite: 28]
            as_max = round(rho_max * b * d, 2)[cite: 28]

            as_base = round(max(as_calc / 3.0, as_min), 2)
            cant_p, barra_p, pulg_p, area_p, diam_p = self.buscar_combinacion(as_base)

            as_remanente = max(0.0, as_calc - area_p)
            cant_r, barra_r, pulg_r, area_r, diam_r = (0, "N/A", "N/A", 0.0, 0.0) if as_remanente == 0 else self.buscar_combinacion(as_remanente)

            diam_estribo = 1.27 if diam_p > 2.54 else 0.95
            estribo_str = "1/2\" (1.27 cm)" if diam_p > 2.54 else "3/8\" (0.95 cm)"

            tot_barras = cant_p + (cant_r if as_remanente > 0 else 0)
            suma_d = (cant_p * diam_p) + ((cant_r if as_remanente > 0 else 0) * diam_r)
            max_d = max(diam_p, diam_r) if as_remanente > 0 else diam_p
            ancho_nec = (8.0) + (2.0 * diam_estribo) + suma_d + (max(0, tot_barras - 1) * max(2.54, max_d))
            ancho_cumple = ancho_nec <= b

            estado_cuant = "CUMPLE" if rho_min < rho < rho_max else "NO CUMPLE"[cite: 28]
            estado_b = "CUMPLE ESPACIO" if ancho_cumple else "EXCEDE ANCHO b"

            self.viga_canvas.actualizar_parametros(b, h, cant_p, cant_r if as_remanente > 0 else 0, cumple=(estado_cuant=="CUMPLE" and ancho_cumple))

            txt = f"[b][size=12sp][color=4EA8DE]DISEÑO MOMENTO POSITIVO (+)[/color][/size][/b]\n"
            txt += f"• As Total Req: [b]{as_calc:.2f} cm²[/b] | As Base: [b]{as_base:.2f} cm²[/b]\n"
            txt += f"🔵 [b]Principal:[/b] [color=4EA8DE]{cant_p} Ø {pulg_p}[/color] ([b]{area_p:.2f} cm²[/b])\n"
            if as_remanente > 0:
                txt += f"🟠 [b]Refuerzo:[/b] [color=FFA533]{cant_r} Ø {pulg_r}[/color] ([b]{area_r:.2f} cm²[/b])\n"
            txt += f"• Cuantía: [b][color={'06D6A0' if estado_cuant=='CUMPLE' else 'FF6B6B'}]{estado_cuant}[/color][/b]\n"[cite: 28]
            txt += f"• Estribo: [b]{estribo_str}[/b] | Ancho Nec: [b]{ancho_nec:.2f} cm[/b]\n"
            txt += f"• Verif b: [b][color={'06D6A0' if ancho_cumple else 'FF6B6B'}]{estado_b}[/color][/b]"
            
            self.resultado_label.text = txt
        except Exception as e:
            self.resultado_label.text = f"[color=FF6B6B][b]❌ Error:[/b] {str(e)}[/color]"


class Hoja3MomentoNegativo(BaseHojaScreen):
    """Hoja 3: Detallado y Diseño de Acero para Momento Negativo (-)."""
    def __init__(self, **kwargs):
        super().__init__("Hoja 3", **kwargs)
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        header = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='horizontal', padding=10, size_hint_y=None, height=45)
        header.add_widget(Label(text="[b]HOJA 3: DISEÑO Y DETALLADO - MOMENTO NEGATIVO (-)[/b]", color=(1,1,1,1), markup=True, halign='center'))
        content.add_widget(header)

        btn_proc = Button(text="▶ PROCESAR DISEÑO MOMENTO (-)", font_size='14sp', bold=True, background_normal='', background_color=(0.1, 0.65, 0.4, 1), color=(1, 1, 1, 1), size_hint_y=None, height=48)
        btn_proc.bind(on_press=self.procesar_negativo)
        content.add_widget(btn_proc)

        self.viga_canvas = WidgetDeVigaSimetrica(size_hint_y=None, height=280)
        content.add_widget(self.viga_canvas)

        self.res_card = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=14, spacing=8, size_hint_y=None, height=380)
        self.resultado_label = Label(text="[color=667788]Presione el botón para procesar el momento negativo.[/color]", font_size='13sp', color=(0.9, 0.9, 0.9, 1), halign="left", valign="top", markup=True, size_hint_y=None, height=350)
        self.resultado_label.bind(size=self.resultado_label.setter('text_size'))
        self.res_card.add_widget(self.resultado_label)
        content.add_widget(self.res_card)

        scroll.add_widget(content)
        self.root_layout.add_widget(scroll)
        self.add_widget(self.root_layout)

    def buscar_combinacion(self, area_objetivo):
        mejor = None
        min_dif = 999999.0
        for barra, pulg, unit, diam in TABLA_ACEROS:
            for cant in range(2, 6):
                total = cant * unit
                if total >= area_objetivo:
                    dif = total - area_objetivo
                    if dif < min_dif:
                        min_dif = dif
                        mejor = (cant, barra, pulg, total, diam)
        return mejor if mejor else (2, "#8", "1\"", 10.14, 2.54)

    def procesar_negativo(self, instance):
        app = App.get_running_app()
        h1 = app.root.get_screen('hoja1')
        try:
            b = float(h1.inputs["Base b (cm) [Min 25]:"].text)
            h = float(h1.inputs["Altura h (cm):"].text)
            d = round(h - 6.0, 2)
            fc = float(h1.inputs["Concreto f'c (Kg/cm²):"].text)
            fy = float(h1.inputs["Acero fy (Kg/cm²):"].text)
            mu = float(h1.inputs["Momento Mu (-) (Tn·m):"].text)
            phi = float(h1.inputs["Factor de reducción ø:"].text)
            is_e060 = "NTP E.060" in h1.norma.text

            k = round((mu * 100000.0) / (phi * fc * b * (d ** 2)), 4)
            w = round((1.0 - math.sqrt(max(0.0, 1.0 - 2.36 * k))) / 1.18, 4)
            rho = round(w * fc / fy, 4)
            as_calc = round(rho * b * d, 2)

            rho_min = round((0.71 * math.sqrt(fc)) / fy if is_e060 else (14.0 / fy), 4)[cite: 28]
            as_min = round(rho_min * b * d, 2)[cite: 28]
            beta1 = 0.85 if fc <= 280 else max(0.85 - (0.05 * (fc - 280) / 70), 0.65)
            rho_max = round(0.32 * 0.85 * (fc / fy) if is_e060 else (0.85 * beta1 * fc / fy) * (0.003 / 0.007), 4)[cite: 28]
            as_max = round(rho_max * b * d, 2)[cite: 28]

            as_base = round(max(as_calc / 3.0, as_min), 2)
            cant_p, barra_p, pulg_p, area_p, diam_p = self.buscar_combinacion(as_base)

            as_remanente = max(0.0, as_calc - area_p)
            cant_r, barra_r, pulg_r, area_r, diam_r = (0, "N/A", "N/A", 0.0, 0.0) if as_remanente == 0 else self.buscar_combinacion(as_remanente)

            diam_estribo = 1.27 if diam_p > 2.54 else 0.95
            estribo_str = "1/2\" (1.27 cm)" if diam_p > 2.54 else "3/8\" (0.95 cm)"

            tot_barras = cant_p + (cant_r if as_remanente > 0 else 0)
            suma_d = (cant_p * diam_p) + ((cant_r if as_remanente > 0 else 0) * diam_r)
            max_d = max(diam_p, diam_r) if as_remanente > 0 else diam_p
            ancho_nec = (8.0) + (2.0 * diam_estribo) + suma_d + (max(0, tot_barras - 1) * max(2.54, max_d))
            ancho_cumple = ancho_nec <= b

            estado_cuant = "CUMPLE" if rho_min < rho < rho_max else "NO CUMPLE"[cite: 28]
            estado_b = "CUMPLE ESPACIO" if ancho_cumple else "EXCEDE ANCHO b"

            self.viga_canvas.actualizar_parametros(b, h, cant_p, cant_r if as_remanente > 0 else 0, cumple=(estado_cuant=="CUMPLE" and ancho_cumple))

            txt = f"[b][size=12sp][color=4EA8DE]DISEÑO MOMENTO NEGATIVO (-)[/color][/size][/b]\n"
            txt += f"• As Total Req: [b]{as_calc:.2f} cm²[/b] | As Base: [b]{as_base:.2f} cm²[/b]\n"
            txt += f"🔵 [b]Principal:[/b] [color=4EA8DE]{cant_p} Ø {pulg_p}[/color] ([b]{area_p:.2f} cm²[/b])\n"
            if as_remanente > 0:
                txt += f"🟠 [b]Refuerzo:[/b] [color=FFA533]{cant_r} Ø {pulg_r}[/color] ([b]{area_r:.2f} cm²[/b])\n"
            txt += f"• Cuantía: [b][color={'06D6A0' if estado_cuant=='CUMPLE' else 'FF6B6B'}]{estado_cuant}[/color][/b]\n"[cite: 28]
            txt += f"• Estribo: [b]{estribo_str}[/b] | Ancho Nec: [b]{ancho_nec:.2f} cm[/b]\n"
            txt += f"• Verif b: [b][color={'06D6A0' if ancho_cumple else 'FF6B6B'}]{estado_b}[/color][/b]"
            
            self.resultado_label.text = txt
        except Exception as e:
            self.resultado_label.text = f"[color=FF6B6B][b]❌ Error:[/b] {str(e)}[/color]"


class CalculadoraDisenoVigaApp(App):
    def build(self):
        self.title = 'Structural Dashboard - Viga Hojas Separadas'
        sm = ScreenManager()
        sm.add_widget(PantallaCaratula(name='caratula'))
        sm.add_widget(Hoja1DatosCoeficientes(name='hoja1'))
        sm.add_widget(Hoja2MomentoPositivo(name='hoja2'))
        sm.add_widget(Hoja3MomentoNegativo(name='hoja3'))
        return sm


if __name__ == '__main__':
    CalculadoraDisenoVigaApp().run()
