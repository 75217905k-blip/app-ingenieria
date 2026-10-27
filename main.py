import math
import traceback
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.metrics import dp

# Intentamos importar KivyMD de forma segura
try:
    from kivymd.app import MDApp
    from kivymd.uix.screen import MDScreen
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.scrollview import MDScrollView
    from kivymd.uix.label import MDLabel
    from kivymd.uix.textfield import MDTextField
    from kivymd.uix.button import MDRaisedButton
    from kivymd.uix.card import MDCard
    KIVYMD_AVAILABLE = True
except Exception as e:
    KIVYMD_AVAILABLE = False
    INIT_ERROR = traceback.format_exc()

# --- BASE DE DATOS DE ACERO COMERCIAL ---
TABLA_ACEROS_CALCULO = {
    '3/8"':   {'d': 0.95, 'area': 0.71},
    '1/2"':   {'d': 1.27, 'area': 1.27},
    '5/8"':   {'d': 1.59, 'area': 1.98},
    '3/4"':   {'d': 1.91, 'area': 2.85},
    '1"':     {'d': 2.54, 'area': 5.07},
    '1 1/8"': {'d': 2.86, 'area': 6.42},
    '1 1/4"': {'d': 3.18, 'area': 7.94},
}

def verificar_ancho_disponible(n_total, diametros, b_cm, recubrimiento=4.0, d_estribo=0.95):
    if n_total <= 0:
        return True, 0.0
    sum_diametros = sum(TABLA_ACEROS_CALCULO[d]['d'] for d in diametros)
    max_d = max(TABLA_ACEROS_CALCULO[d]['d'] for d in diametros)
    s_min = max(2.54, max_d)
    separaciones = (n_total - 1) * s_min
    ancho_requerido = (2 * recubrimiento) + (2 * d_estribo) + sum_diametros + separaciones
    return ancho_requerido <= b_cm, ancho_requerido

def optimizar_distribucion_acero(As_requerido, As_min, b_cm):
    As_c_req = max(As_requerido / 3.0, As_min)
    mejores_opciones = []
    
    for nombre_d, info in TABLA_ACEROS_CALCULO.items():
        for n_cont in [2, 3]:
            area_cont = n_cont * info['area']
            if area_cont >= As_c_req:
                for nombre_baston, info_b in TABLA_ACEROS_CALCULO.items():
                    if info_b['d'] <= info['d']:
                        for n_baston in range(0, 5):
                            area_baston = n_baston * info_b['area']
                            area_total = area_cont + area_baston
                            if area_total >= As_requerido:
                                n_total = n_cont + n_baston
                                lista_d = [nombre_d]*n_cont + [nombre_baston]*n_baston
                                cumple_b, ancho_req = verificar_ancho_disponible(n_total, lista_d, b_cm)
                                if cumple_b:
                                    mejores_opciones.append({
                                        'cont_cant': n_cont,
                                        'cont_tipo': nombre_d,
                                        'baston_cant': n_baston,
                                        'baston_tipo': nombre_baston if n_baston > 0 else '-',
                                        'area_total': area_total,
                                        'exceso': area_total - As_requerido,
                                        'ancho_req': ancho_req,
                                        'n_total': n_total
                                    })
    if not mejores_opciones:
        return None
    mejores_opciones.sort(key=lambda x: x['exceso'])
    return mejores_opciones[0]


# --- WIDGET DE DIBUJO TÉCNICO ---
class BeamCanvasWidget(Widget):
    def __init__(self, **kwargs):
        super(BeamCanvasWidget, self).__init__(**kwargs)
        self.b_cm = 30.0
        self.h_cm = 60.0
        self.opt_inf = None
        self.opt_sup = None
        self.bind(pos=self.actualizar_dibujo, size=self.actualizar_dibujo)

    def actualizar_datos(self, b, h, opt_inf, opt_sup):
        self.b_cm = b
        self.h_cm = h
        self.opt_inf = opt_inf
        self.opt_sup = opt_sup
        self.actualizar_dibujo()

    def actualizar_dibujo(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.1, 0.12, 0.16, 1)
            Rectangle(pos=self.pos, size=self.size)

            w, h = self.width, self.height
            if w <= 20 or h <= 20:
                return

            escala = min((w - 50) / self.b_cm, (h - 50) / self.h_cm)
            v_w = self.b_cm * escala
            v_h = self.h_cm * escala
            v_x = self.x + (w - v_w) / 2.0
            v_y = self.y + (h - v_h) / 2.0

            Color(0.3, 0.35, 0.42, 1)
            Rectangle(pos=(v_x, v_y), size=(v_w, v_h))
            Color(0.8, 0.9, 1.0, 1)
            Line(rectangle=(v_x, v_y, v_w, v_h), width=2)

            rec = 4.0 * escala
            est_x = v_x + rec
            est_y = v_y + rec
            est_w = v_w - (2 * rec)
            est_h = v_h - (2 * rec)
            if est_w > 0 and est_h > 0:
                Color(1.0, 0.6, 0.2, 1)
                Line(rectangle=(est_x, est_y, est_w, est_h), width=1.5)

            if self.opt_inf:
                n_inf = self.opt_inf['n_total']
                tipo_inf = self.opt_inf['cont_tipo']
                radio_inf = (TABLA_ACEROS_CALCULO[tipo_inf]['d'] * escala) / 2.0
                Color(0.9, 0.2, 0.2, 1)
                if n_inf > 0:
                    espacio_util = est_w - (2 * radio_inf)
                    paso = espacio_util / max(1, (n_inf - 1)) if n_inf > 1 else 0
                    for i in range(n_inf):
                        cx = est_x + radio_inf + (i * paso)
                        cy = est_y + radio_inf + 2
                        Ellipse(pos=(cx - radio_inf, cy - radio_inf), size=(radio_inf * 2, radio_inf * 2))

            if self.opt_sup:
                n_sup = self.opt_sup['n_total']
                tipo_sup = self.opt_sup['cont_tipo']
                radio_sup = (TABLA_ACEROS_CALCULO[tipo_sup]['d'] * escala) / 2.0
                Color(0.2, 0.8, 0.9, 1)
                if n_sup > 0:
                    espacio_util = est_w - (2 * radio_sup)
                    paso = espacio_util / max(1, (n_sup - 1)) if n_sup > 1 else 0
                    for i in range(n_sup):
                        cx = est_x + radio_sup + (i * paso)
                        cy = (est_y + est_h) - radio_sup - 2
                        Ellipse(pos=(cx - radio_sup, cy - radio_sup), size=(radio_sup * 2, radio_sup * 2))

if KIVYMD_AVAILABLE:
    class VigaMDApp(MDApp):
        def build(self):
            try:
                self.theme_cls.theme_style = "Dark"
                self.theme_cls.primary_palette = "Blue"

                screen = MDScreen()
                scroll = MDScrollView()
                
                layout = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15), size_hint_y=None)
                layout.bind(minimum_height=layout.setter('height'))

                layout.add_widget(MDLabel(text="Diseño y Detallado de Vigas - VSR", halign="center", bold=True, size_hint_y=None, height=dp(40)))

                card_inputs = MDCard(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None, height=dp(420), elevation=2)
                card_inputs.add_widget(MDLabel(text="Parámetros de Diseño", bold=True, size_hint_y=None, height=dp(30)))

                self.input_b = MDTextField(text="30", label="Base b (cm)", mode="fill")
                card_inputs.add_widget(self.input_b)

                self.input_h = MDTextField(text="60", label="Peralte h (cm)", mode="fill")
                card_inputs.add_widget(self.input_h)

                self.input_fc = MDTextField(text="210", label="f'c (kg/cm²)", mode="fill")
                card_inputs.add_widget(self.input_fc)

                self.input_fy = MDTextField(text="4200", label="fy (kg/cm²)", mode="fill")
                card_inputs.add_widget(self.input_fy)

                self.input_mu_pos = MDTextField(text="15.0", label="Mu (+) (Tn.m)", mode="fill")
                card_inputs.add_widget(self.input_mu_pos)

                self.input_mu_neg = MDTextField(text="22.0", label="Mu (-) (Tn.m)", mode="fill")
                card_inputs.add_widget(self.input_mu_neg)

                layout.add_widget(card_inputs)

                btn_calcular = MDRaisedButton(text="Ejecutar Diseño y Dibujar Sección", size_hint_x=1, on_press=self.calcular_diseno, elevation=3)
                layout.add_widget(btn_calcular)

                card_canvas = MDCard(orientation='vertical', padding=dp(10), spacing=dp(5), size_hint_y=None, height=dp(260), elevation=2)
                card_canvas.add_widget(MDLabel(text="Sección Transversal de la Viga", bold=True, size_hint_y=None, height=dp(25)))
                
                self.canvas_widget = BeamCanvasWidget(size_hint_y=None, height=dp(210))
                card_canvas.add_widget(self.canvas_widget)
                layout.add_widget(card_canvas)

                card_res = MDCard(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None, height=dp(300), elevation=2)
                card_res.add_widget(MDLabel(text="Memoria de Cálculo Técnica", bold=True, size_hint_y=None, height=dp(30)))
                
                self.label_resultados = MDLabel(
                    text="Ingrese los datos y presione el botón superior para calcular y dibujar.", 
                    halign="left", 
                    valign="top"
                )
                self.label_resultados.bind(size=self.label_resultados.setter('text_size'))
                card_res.add_widget(self.label_resultados)
                
                layout.add_widget(card_res)

                scroll.add_widget(layout)
                screen.add_widget(scroll)
                return screen

            except Exception as e:
                from kivymd.uix.label import MDLabel
                return MDLabel(text=f"ERROR EN BUILD:\n{traceback.format_exc()}", halign="center")

        def calcular_diseno(self, instance):
            try:
                b = float(self.input_b.text)
                h = float(self.input_h.text)
                fc = float(self.input_fc.text)
                fy = float(self.input_fy.text)
                mu_pos = float(self.input_mu_pos.text)
                mu_neg = float(self.input_mu_neg.text)

                if b < 25:
                    self.label_resultados.text = "⚠️ Error: El ancho b debe ser mínimo 25 cm por norma."
                    return

                d = h - 6.0
                phi = 0.9
                rho_min = max(0.8 * math.sqrt(fc) / fy, 14.1 / fy)
                As_min = rho_min * b * d

                def resolver_flexion(mu_ton):
                    mu_kg_cm = mu_ton * 100000.0
                    k = mu_kg_cm / (phi * b * (d**2))
                    radical = 0.7225 - (1.7 * k / fc)
                    if radical < 0:
                        return None
                    omega = 0.85 - math.sqrt(radical)
                    return omega * (fc / fy) * b * d

                As_pos = resolver_flexion(mu_pos)
                As_gov_pos = max(As_pos if As_pos else As_min, As_min)
                opt_pos = optimizar_distribucion_acero(As_gov_pos, As_min, b)

                As_neg = resolver_flexion(mu_neg)
                As_gov_neg = max(As_neg if As_neg else As_min, As_min)
                opt_neg = optimizar_distribucion_acero(As_gov_neg, As_min, b)

                armado_inf = f"{opt_pos['cont_cant']}φ{opt_pos['cont_tipo']} + {opt_pos['baston_cant']}φ{opt_pos['baston_tipo']}" if opt_pos else "N/D"
                armado_sup = f"{opt_neg['cont_cant']}φ{opt_neg['cont_tipo']} + {opt_neg['baston_cant']}φ{opt_neg['baston_tipo']}" if opt_neg else "N/D"

                self.canvas_widget.actualizar_datos(b, h, opt_pos, opt_neg)

                reporte = (
                    f"• Geometría: b={b}cm | h={h}cm | d={d:.1f}cm\n"
                    f"• Materiales: f'c={fc} | fy={fy} | As_min={As_min:.2f} cm²\n\n"
                    f"1. ACERO POSITIVO (+) [Inferior]:\n"
                    f"   - Requerido: {As_pos:.2f} cm² | Gobernaje: {As_gov_pos:.2f} cm²\n"
                    f"   - Armado: {armado_inf} (Área: {opt_pos['area_total']:.2f} cm² ➔ CUMPLE)\n\n"
                    f"2. ACERO NEGATIVO (-) [Superior]:\n"
                    f"   - Requerido: {As_neg:.2f} cm² | Gobernaje: {As_gov_neg:.2f} cm²\n"
                    f"   - Armado: {armado_sup} (Área: {opt_neg['area_total']:.2f} cm² ➔ CUMPLE)\n\n"
                    f"3. ESTRIBOS: 1φ3/8\" @ 0.05, 10 @ 0.10, resto @ 0.20m"
                )
                self.label_resultados.text = reporte

            except Exception as ex:
                self.label_resultados.text = f"❌ Error en los datos: {str(ex)}"
else:
    class VigaMDApp(App):
        def build(self):
            from kivy.uix.label import Label
            return Label(text=f"ERROR DE IMPORTACION KIVYMD:\n{INIT_ERROR}")

if __name__ == '__main__':
    VigaMDApp().run()
