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


class WidgetDeVigaGigante(BoxLayout):
    """Widget gráfico interactivo para visualizar la sección y diferenciar acero principal vs refuerzo."""
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

            # 1. Contorno exterior del concreto
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

            # 3. Puntos de acero diferenciados (Principal = Azul brillante, Refuerzo = Naranja/Ámbar)
            total_b = self.num_p + self.num_r
            total_b = max(2, total_b)
            radio = max(3.5, min(6.5, estribo_w / (total_b * 4.0)))
            y_pos = estribo_y + 4
            
            if total_b == 2:
                xs = [estribo_x + 5, estribo_x + estribo_w - (radio * 2) - 5]
                tipos = ['P', 'P'][:total_b]
            else:
                ancho_util = estribo_w - 10 - (radio * 2)
                paso_inf = ancho_util / (total_b - 1)
                xs = [estribo_x + 5 + (i * paso_inf) for i in range(total_b)]
                tipos = ['P'] * self.num_p + ['R'] * self.num_r
                while len(tipos) < total_b:
                    tipos.append('R')
                tipos = tipos[:total_b]

            for x_i, tipo in zip(xs, tipos):
                if tipo == 'P':
                    Color(0.2, 0.65, 1.0, 1)  # Azul para Acero Longitudinal Principal
                else:
                    Color(1.0, 0.55, 0.1, 1)  # Naranja para Acero de Refuerzo Remanente
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
            text="• Selección Óptima de Acero (Principal + Refuerzo)\n• Criterio Automático de Estribos y Espaciamientos\n• Verificación Geométrica Rigurosa en Ancho 'b'",
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
        header_card.add_widget(Label(text="[b]PANEL DE CÁLCULO - VIGA VSR[/b]", color=(1,1,1,1), markup=True, halign='center'))
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
            ("Altura h (cm):", "65"),
            ("Concreto f'c (Kg/cm²):", "280"),
            ("Acero fy (Kg/cm²):", "4200"),
            ("Momento Mu (+) (Tn·m):", "37.54"),
            ("Momento Mu (-) (Tn·m):", "25.14"),
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
            text="▶ PROCESAR CÁLCULO Y DETALLADO",
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

        # Bloque Gráfico Gigante
        self.viga_canvas = WidgetDeVigaGigante(size_hint_y=None, height=340)
        main_layout.add_widget(self.viga_canvas)

        # Tarjeta de Resultados Organizada (Cuadro Dinámico Agrandado)
        self.res_card = TarjetaDashboard(bg_color=(0.1, 0.14, 0.22, 1), orientation='vertical', padding=14, spacing=8, size_hint_y=None, height=720)
        
        self.resultado_label = Label(
            text="[color=667788]Ingrese los datos y presione [PROCESAR CÁLCULO][/color]",
            font_size='13sp',
            color=(0.9, 0.9, 0.9, 1),
            halign="left",
            valign="top",
            markup=True,
            size_hint_y=None,
            height=690
        )
        self.resultado_label.bind(size=self.resultado_label.setter('text_size'))
        self.res_card.add_widget(self.resultado_label)
        main_layout.add_widget(self.res_card)

        root.add_widget(main_layout)
        self.add_widget(root)

    def regresar_caratula(self, instance):
        self.manager.current = 'caratula'

    def buscar_combinacion_optima(self, area_objetivo):
        """Busca en la tabla de aceros la combinación óptima que supere el área objetivo de forma cercana."""
        mejor_comb = None
        min_diferencia = 999999.0
        
        for barra, pulg, area_unit, diam in TABLA_ACEROS:
            for cant in range(2, 6):
                area_total = cant * area_unit
                if area_total >= area_objetivo:
                    dif = area_total - area_objetivo
                    if dif < min_diferencia:
                        min_diferencia = dif
                        mejor_comb = (cant, barra, pulg, area_total, diam)
        
        if not mejor_comb:
            mejor_comb = (2, "#8", "1\"", 10.14, 2.54)
        return mejor_comb

    def calcular_flexion_cadena_excel(self, mu_tn, b, h, d, fc, fy, phi, is_norma_e060):
        mu_kgcm = mu_tn * 100000.0
        k = round(mu_kgcm / (phi * fc * b * (d ** 2)), 4)
        
        disc = 1.0 - 2.36 * k
        if disc < 0:
            return None, "Error: Mu excesivo"
            
        w = round((1.0 - math.sqrt(disc)) / 1.18, 4)
        rho = round(w * fc / fy, 4)
        as_calc = round(rho * b * d, 2)
        
        rho_min = round((0.71 * math.sqrt(fc)) / fy if is_norma_e060 else (14.0 / fy), 4)
        as_min = round(rho_min * b * d, 2)
        
        beta1 = 0.85 if fc <= 280 else max(0.85 - (0.05 * (fc - 280) / 70), 0.65)
        if is_norma_e060:
            rho_max = round(0.32 * 0.85 * (fc / fy), 4)
        else:
            rho_max = round((0.85 * beta1 * fc / fy) * (0.003 / (0.003 + 0.004)), 4)
            
        as_max = round(rho_max * b * d, 2)
        
        as_continuo_req = round(as_calc / 3.0, 2)
        as_diseno = round(max(as_continuo_req, as_min), 2)
        
        cumple_cond = rho_min < rho < rho_max
        estado_txt = "CUMPLE" if cumple_cond else "NO CUMPLE"
        
        return k, w, rho, as_calc, rho_min, as_min, rho_max, as_max, as_continuo_req, as_diseno, estado_txt

    def ejecutar_diseno(self, instance):
        try:
            b = float(self.inputs["Base b (cm) [Min 25]:"].text)
            
            if b < 25.0:
                self.resultado_label.text = f"[color=FF6B6B][b]❌ RESTRICCIÓN NORMATIVA (NTP E.060):[/b]\nLa base 'b' es {b} cm. El ancho mínimo es [b]25 cm[/b].[/color]"
                self.viga_canvas.actualizar_parametros(b, float(self.inputs["Altura h (cm):"].text), 2, 0, cumple=False)
                return

            h = float(self.inputs["Altura h (cm):"].text)
            d = round(h - 6.0, 2)

            fc = float(self.inputs["Concreto f'c (Kg/cm²):"].text)
            fy = float(self.inputs["Acero fy (Kg/cm²):"].text)
            mu_pos_tn = float(self.inputs["Momento Mu (+) (Tn·m):"].text)
            mu_neg_tn = float(self.inputs["Momento Mu (-) (Tn·m):"].text)
            phi = float(self.inputs["Factor de reducción ø:"].text)
            
            is_e060 = "NTP E.060" in self.norma.text
            nombre_norma = "NTP E.060 de Perú" if is_e060 else "ACI 318"

            # Momento Positivo (+)
            res_pos = self.calcular_flexion_cadena_excel(mu_pos_tn, b, h, d, fc, fy, phi, is_e060)
            if res_pos[1] == "Error: Mu excesivo":
                self.resultado_label.text = "[color=FF6B6B][b]❌ ERROR:[/b] Momento Mu (+) excesivo para la sección.[/color]"
                return
            k_pos, w_pos, rho_pos, as_calc_pos, rho_min_val, as_min_val, rho_max_val, as_max_val, as_cont_pos, as_dis_pos, estado_pos = res_pos

            # Detallado de Acero Positivo (Principal y Refuerzo)
            cant_p, barra_p, pulg_p, area_p, diam_p = self.buscar_combinacion_optima(as_dis_pos)
            
            # Acero remanente de refuerzo
            as_remanente = max(0.0, as_calc_pos - area_p)
            if as_remanente > 0:
                cant_r, barra_r, pulg_r, area_r, diam_r = self.buscar_combinacion_optima(as_remanente)
            else:
                cant_r, barra_r, pulg_r, area_r, diam_r = 0, "N/A", "N/A", 0.0, 0.0

            # Criterio automático de estribos según diámetro longitudinal principal (> 1" -> 1/2", sino -> 3/8")
            if diam_p > 2.54:
                estribo_str = "1/2\" (1.27 cm)"
                diam_estribo = 1.27
            else:
                estribo_str = "3/8\" (0.95 cm)"
                diam_estribo = 0.95

            # VERIFICACIÓN GEOMÉTRICA RIGUROSA EN ANCHO b:
            recubrimiento = 4.0
            num_p = cant_p
            num_r = cant_r if as_remanente > 0 else 0
            total_barras_capa = num_p + num_r
            
            suma_diametros_aceros = (num_p * diam_p) + (num_r * diam_r)
            max_diam_barra = max(diam_p, diam_r) if num_r > 0 else diam_p
            espaciamiento_libre = max(2.54, max_diam_barra)
            num_espacios = max(0, total_barras_capa - 1)
            suma_espaciamientos = num_espacios * espaciamiento_libre

            ancho_necesario = (2.0 * recubrimiento) + (2.0 * diam_estribo) + suma_diametros_aceros + suma_espaciamientos
            
            ancho_cumple = ancho_necesario <= b
            estado_ancho = "CUMPLE ESPACIO" if ancho_cumple else "EXCEDE ANCHO b (Ajustar sección)"

            # Momento Negativo (-)
            res_neg = self.calcular_flexion_cadena_excel(mu_neg_tn, b, h, d, fc, fy, phi, is_e060)
            k_neg, w_neg, rho_neg, as_calc_neg, _, _, _, _, as_cont_neg, as_dis_neg, estado_neg = res_neg

            # Actualizar gráfico viga (Pasando cantidad principal y cantidad de refuerzo para colorearlos diferente)
            cumple_general = (estado_pos == "CUMPLE") and (estado_neg == "CUMPLE") and ancho_cumple
            self.viga_canvas.actualizar_parametros(b, h, num_p, num_r, cumple=cumple_general)

            # Reporte Visual Organizado y Amplio
            txt = f"[b][size=13sp][color=4EA8DE]DETALLADO Y DISEÑO DE ACERO [{nombre_norma}][/color][/size][/b]\n"
            txt += f"[color=AACCFF]Peralte d = {d:.2f} cm  |  Ancho b = {b:.1f} cm[/color]\n"
            txt += f"[color=FFD166]── LÍMITES NORMATIVOS ──[/color]\n"
            txt += f"  • As min = [b]{as_min_val:.2f} cm²[/b]  |  As max = [b]{as_max_val:.2f} cm²[/b]\n\n"
            
            txt += f"[b][color=FFD166]── ACERO POSITIVO (+) ──[/color][/b]\n"
            txt += f"  • As Total Req: [b]{as_calc_pos:.2f} cm²[/b] | As Base Req: [b]{as_dis_pos:.2f} cm²[/b]\n"
            txt += f"  🔵 [b]Principal:[/b] [color=4EA8DE]{cant_p} Ø {pulg_p}[/color] = [b]{area_p:.2f} cm²[/b]\n"
            if as_remanente > 0:
                txt += f"  🟠 [b]Refuerzo:[/b] [color=FFA533]{cant_r} Ø {pulg_r}[/color] = [b]{area_r:.2f} cm²[/b] (Remanente: {as_remanente:.2f} cm²)\n"
            txt += f"  • Estado Cuantía: [b][color={'06D6A0' if estado_pos=='CUMPLE' else 'FF6B6B'}]{estado_pos}[/color][/b]\n\n"

            txt += f"[b][color=FFD166]── GEOMETRÍA Y ESPACIAMIENTO EN ANCHO b ──[/color][/b]\n"
            txt += f"  • Estribo Seleccionado: [b]{estribo_str}[/b]\n"
            txt += f"  • Ancho Requerido: [b]{ancho_necesario:.2f} cm[/b] (Disponible: {b} cm)\n"
            txt += f"  • Verificación: [b][color={'06D6A0' if ancho_cumple else 'FF6B6B'}]{estado_ancho}[/color][/b]"
            
            self.resultado_label.text = txt
        except Exception as e:
            self.resultado_label.text = f"[color=FF6B6B][b]❌ Error:[/b] {str(e)}[/color]"


class CalculadoraDisenoVigaApp(App):
    def build(self):
        self.title = 'Structural Dashboard - Viga Flexión & Detallado'
        sm = ScreenManager()
        sm.add_widget(PantallaCaratula(name='caratula'))
        sm.add_widget(PantallaCalculo(name='calculo'))
        return sm


if __name__ == '__main__':
    CalculadoraDisenoVigaApp().run()
