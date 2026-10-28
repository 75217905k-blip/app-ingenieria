import math
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.core.text import Label as CoreLabel
from kivy.metrics import dp

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


# --- WIDGET DE DIBUJO TÉCNICO CON ACOTADO Y LÓGICA SA/CA ---
class BeamCanvasWidget(Widget):
    def __init__(self, **kwargs):
        super(BeamCanvasWidget, self).__init__(**kwargs)
        self.b_cm = 30.0
        self.h_cm = 65.0
        self.d_cm = 59.0
        self.modo_sa = True
        self.opt_inf = None
        self.cant_ca = 3
        self.diam_ca = '5/8"'
        self.bind(pos=self.actualizar_dibujo, size=self.actualizar_dibujo)

    def actualizar_datos(self, b, h, d, modo_sa, opt_inf, cant_ca=3, diam_ca='5/8"'):
        self.b_cm = b
        self.h_cm = h
        self.d_cm = d
        self.modo_sa = modo_sa
        self.opt_inf = opt_inf
        self.cant_ca = cant_ca
        self.diam_ca = diam_ca
        self.actualizar_dibujo()

    def actualizar_dibujo(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.1, 0.12, 0.16, 1)
            Rectangle(pos=self.pos, size=self.size)

            w, h = self.width, self.height
            if w <= 60 or h <= 60:
                return

            margen_x = 70
            margen_y = 50
            escala = min((w - margen_x * 2) / self.b_cm, (h - margen_y * 2) / self.h_cm)
            v_w = self.b_cm * escala
            v_h = self.h_cm * escala
            v_x = self.x + (w - v_w) / 2.0
            v_y = self.y + (h - v_h) / 2.0 + 10

            # Concreto
            Color(0.25, 0.3, 0.38, 1)
            Rectangle(pos=(v_x, v_y), size=(v_w, v_h))
            Color(0.8, 0.9, 1.0, 1)
            Line(rectangle=(v_x, v_y, v_w, v_h), width=2)

            # Estribo
            rec = 4.0 * escala
            est_x = v_x + rec
            est_y = v_y + rec
            est_w = v_w - (2 * rec)
            est_h = v_h - (2 * rec)
            if est_w > 0 and est_h > 0:
                Color(1.0, 0.6, 0.2, 1)
                Line(rectangle=(est_x, est_y, est_w, est_h), width=1.5)

            # REPRESENTACIÓN DE ACERO SEGÚN LA OPCIÓN ELEGIDA
            if self.modo_sa:
                Color(0.2, 0.8, 1.0, 1)
                punto_radio = 6
                cx_centro = v_x + v_w / 2.0
                cy_d = v_y + v_h - (self.d_cm * escala)
                Ellipse(pos=(cx_centro - punto_radio, cy_d - punto_radio), size=(punto_radio * 2, punto_radio * 2))
            else:
                if self.diam_ca in TABLA_ACEROS_CALCULO:
                    radio_inf = (TABLA_ACEROS_CALCULO[self.diam_ca]['d'] * escala) / 2.0
                    Color(0.9, 0.2, 0.2, 1)
                    n_inf = self.cant_ca
                    if n_inf > 0:
                        espacio_util = est_w - (2 * radio_inf)
                        paso = espacio_util / max(1, (n_inf - 1)) if n_inf > 1 else 0
                        for i in range(n_inf):
                            cx = est_x + radio_inf + (i * paso)
                            cy = est_y + radio_inf + 2
                            Ellipse(pos=(cx - radio_inf, cy - radio_inf), size=(radio_inf * 2, radio_inf * 2))

            # --- ACOTADO TÉCNICO (b, h, d) ---
            Color(0.7, 0.8, 0.9, 1)
            Line(points=[v_x, v_y - 10, v_x, v_y - 25], width=1)
            Line(points=[v_x + v_w, v_y - 10, v_x + v_w, v_y - 25], width=1)
            Line(points=[v_x, v_y - 18, v_x + v_w, v_y - 18], width=1)

            Line(points=[v_x - 10, v_y, v_x - 25, v_y], width=1)
            Line(points=[v_x - 10, v_y + v_h, v_x - 25, v_y + v_h], width=1)
            Line(points=[v_x - 18, v_y, v_x - 18, v_y + v_h], width=1)

            d_escala_y = v_y + v_h - (self.d_cm * escala)
            Color(0.2, 0.9, 0.5, 1)
            Line(points=[v_x + v_w + 10, v_y + v_h, v_x + v_w + 25, v_y + v_h], width=1)
            Line(points=[v_x + v_w + 10, d_escala_y, v_x + v_w + 25, d_escala_y], width=1)
            Line(points=[v_x + v_w + 18, v_y + v_h, v_x + v_w + 18, d_escala_y], width=1, dash_offset=2)

        self.dibujar_texto(f"b = {self.b_cm:.1f} cm", v_x + v_w / 2.0 - 30, v_y - 38)
        self.dibujar_texto(f"h = {self.h_cm:.1f} cm", v_x - 55, v_y + v_h / 2.0 - 10)
        self.dibujar_texto(f"d = {self.d_cm:.1f} cm", v_x + v_w + 28, v_y + v_h / 2.0 - 10)

    def dibujar_texto(self, texto, x, y):
        label = CoreLabel(text=texto, font_size=12, color=(1, 1, 1, 1))
        label.refresh()
        texture = label.texture
        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(texture=texture, pos=(x, y), size=texture.size)


# --- PANTALLA 1: CARÁTULA DE INICIO ---
class CaratulaScreen(Screen):
    def __init__(self, **kwargs):
        super(CaratulaScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(20))
        
        lbl_titulo = Label(text="DISEÑO DE VIGAS", font_size=dp(30), bold=True, size_hint_y=None, height=dp(60), halign='center')
        lbl_subtitulo = Label(text="Módulo de Análisis y Detallado Estructural\nNorma Técnica Peruana NTP E.060", font_size=dp(15), halign='center', size_hint_y=None, height=dp(60))
        
        spacer = Widget()
        
        btn_ingresar = Button(text="INGRESAR AL SISTEMA ➔", font_size=dp(18), bold=True, size_hint_y=None, height=dp(60), background_color=(0.1, 0.5, 0.8, 1))
        btn_ingresar.bind(on_press=self.ir_a_calculadora)

        layout.add_widget(lbl_titulo)
        layout.add_widget(lbl_subtitulo)
        layout.add_widget(spacer)
        layout.add_widget(btn_ingresar)
        self.add_widget(layout)

    def ir_a_calculadora(self, instance):
        self.manager.current = 'pantalla_principal'


# --- PANTALLA PRINCIPAL CON PESTAÑAS Y CUADRO DE DATOS ---
class CalculadoraScreen(Screen):
    def __init__(self, **kwargs):
        super(CalculadoraScreen, self).__init__(**kwargs)
        root_layout = BoxLayout(orientation='vertical')

        # --- BARRA DE PESTAÑAS SUPERIOR ---
        nav_layout = GridLayout(cols=3, size_hint_y=None, height=dp(45))
        
        self.btn_tab1 = Button(text="1. Coef. y Cuantías", background_color=(0.15, 0.25, 0.45, 1))
        self.btn_tab2 = Button(text="2. Momento (+)", background_color=(0.1, 0.2, 0.35, 1))
        self.btn_tab3 = Button(text="3. Momento (-)", background_color=(0.1, 0.2, 0.35, 1))

        self.btn_tab1.bind(on_press=lambda x: self.cambiar_pestana('tab1'))
        self.btn_tab2.bind(on_press=lambda x: self.cambiar_pestana('tab2'))
        self.btn_tab3.bind(on_press=lambda x: self.cambiar_pestana('tab3'))

        nav_layout.add_widget(self.btn_tab1)
        nav_layout.add_widget(self.btn_tab2)
        nav_layout.add_widget(self.btn_tab3)
        root_layout.add_widget(nav_layout)

        # --- GESTOR DE PANTALLAS (PESTAÑAS) ---
        self.sm = ScreenManager()

        # PESTAÑA 1: DATOS Y PARÁMETROS (ESTILO EXCEL 3 COLUMNAS)
        self.screen1 = Screen(name='tab1')
        scroll1 = ScrollView()
        layout1 = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(15), size_hint_y=None)
        layout1.bind(minimum_height=layout1.setter('height'))

        layout1.add_widget(Label(text="HOJA 1: DATOS Y PARÁMETROS DE DISEÑO", bold=True, font_size=16, size_hint_y=None, height=dp(30)))
        layout1.add_widget(Label(text="Norma de Diseño: NTP E.060 (McCormac / Morales)", font_size=13, size_hint_y=None, height=dp(22)))

        lbl_mod = Label(text="Seleccione la Modalidad de Cálculo:", halign='left', font_size=14, bold=True, size_hint_y=None, height=dp(22))
        lbl_mod.bind(size=lbl_mod.setter('text_size'))
        layout1.add_widget(lbl_mod)

        box_toggles = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        self.btn_sa = ToggleButton(text='OPCIÓN 1: SA\n(Sin Acero)', group='modo_d', state='down')
        self.btn_ca = ToggleButton(text='OPCIÓN 2: CA\n(Con Acero Long.)', group='modo_d')
        
        self.btn_sa.bind(on_press=self.actualizar_estado_modo)
        self.btn_ca.bind(on_press=self.actualizar_estado_modo)

        box_toggles.add_widget(self.btn_sa)
        box_toggles.add_widget(self.btn_ca)
        layout1.add_widget(box_toggles)

        # PANEL ACERO CA
        self.box_acero_ca_panel = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(85), spacing=dp(5), padding=dp(5))
        self.box_acero_ca_panel.add_widget(Label(text="⚙️ DATOS DEL ACERO LONGITUDINAL (Modo CA):", font_size=13, bold=True, color=(0.2, 0.7, 1, 1), size_hint_y=None, height=dp(20)))
        
        sub_grid_ca = GridLayout(cols=2, size_hint_y=None, height=dp(45), spacing=dp(10))
        sub_grid_ca.add_widget(Label(text="Cant. de barras:", font_size=12, halign='right'))
        self.ti_ca_cant = TextInput(text="3", multiline=False)
        sub_grid_ca.add_widget(self.ti_ca_cant)
        
        sub_grid_ca.add_widget(Label(text="Medida (øL):", font_size=12, halign='right'))
        self.spinner_ca_diam = Spinner(text='5/8"', values=list(TABLA_ACEROS_CALCULO.keys()))
        sub_grid_ca.add_widget(self.spinner_ca_diam)
        
        self.box_acero_ca_panel.add_widget(sub_grid_ca)
        layout1.add_widget(self.box_acero_ca_panel)
        self.box_acero_ca_panel.opacity = 0
        self.box_acero_ca_panel.disabled = True
        self.box_acero_ca_panel.height = 0

        header_grid = GridLayout(cols=3, size_hint_y=None, height=dp(35), spacing=dp(5))
        header_grid.add_widget(Label(text="Parámetro", bold=True, font_size=13))
        header_grid.add_widget(Label(text="Col. 2 (SA)", bold=True, font_size=13))
        header_grid.add_widget(Label(text="Col. 3 (CA)", bold=True, font_size=13))
        layout1.add_widget(header_grid)

        self.inputs_sa = {}
        self.inputs_ca = {}
        
        filas_datos = [
            ('b', 'b =', '30'),
            ('h', 'h =', '65'),
            ('d', 'd =', '59'),
            ('fc', "f'c =", '210'),
            ('fy', 'fy =', '4200'),
            ('mu_pos', 'Mu (+) =', '17.96'),
            ('mu_neg', 'Mu (-) =', '25.14'),
            ('phi', 'ø =', '0.9')
        ]

        for key, lbl_text, def_val in filas_datos:
            row_box = GridLayout(cols=3, size_hint_y=None, height=dp(45), spacing=dp(5))
            lbl = Label(text=lbl_text, font_size=14, bold=True, halign='left')
            lbl.bind(size=lbl.setter('text_size'))
            row_box.add_widget(lbl)
            
            ti_sa = TextInput(text=def_val, multiline=False)
            self.inputs_sa[key] = ti_sa
            row_box.add_widget(ti_sa)
            
            if key == 'd':
                ti_ca = TextInput(text='[Calculado]', multiline=False)
                ti_ca.disabled = True
                self.inputs_ca[key] = ti_ca
                row_box.add_widget(ti_ca)
            else:
                ti_ca = TextInput(text='-', multiline=False)
                ti_ca.disabled = True
                self.inputs_ca[key] = ti_ca
                row_box.add_widget(ti_ca)
                
            layout1.add_widget(row_box)

        btn_calc = Button(text="🧮 EJECUTAR DISEÑO Y DIBUJAR SECCIÓN", size_hint_y=None, height=dp(50), background_color=(0.1, 0.6, 0.3, 1))
        btn_calc.bind(on_press=self.ejecutar_calculos)
        layout1.add_widget(btn_calc)

        self.label_res1 = Label(text="Seleccione modalidad (SA o CA), rellene sus datos y presione calcular.", size_hint_y=None, height=dp(140), halign='left', valign='top')
        self.label_res1.bind(size=self.label_res1.setter('text_size'))
        layout1.add_widget(self.label_res1)

        scroll1.add_widget(layout1)
        self.screen1.add_widget(scroll1)
        self.sm.add_widget(self.screen1)

        # PESTAÑA 2: MOMENTO (+) CON TABLA DE CÁLCULO Y BLOQUE VSR/VDR INTEGRADO
        self.screen2 = Screen(name='tab2')
        scroll2 = ScrollView()
        layout2 = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10), size_hint_y=None)
        layout2.bind(minimum_height=layout2.setter('height'))
        
        layout2.add_widget(Label(text="HOJA 2: DISEÑO - MOMENTO POSITIVO (+)", bold=True, size_hint_y=None, height=dp(30)))
        
        self.canvas_widget = BeamCanvasWidget(size_hint_y=None, height=dp(220))
        layout2.add_widget(self.canvas_widget)

        self.label_tabla_pos = Label(
            text="[ TABLA DE CÁLCULO - MOMENTO POSITIVO ]\n• K = -\n• w = -\n• ρ = -\n• As = - cm²",
            size_hint_y=None, height=dp(130), halign='left', valign='top', font_size=14
        )
        self.label_tabla_pos.bind(size=self.label_tabla_pos.setter('text_size'))
        layout2.add_widget(self.label_tabla_pos)

        # Cuadro estructurado de Cuantías y VSR/VDR
        self.label_cuantia_pos = Label(
            text="┌──────────────────────────────────────────────┐\n"
                 "│        CÁLCULO CUANTÍA (MÍN / MÁX)           │\n"
                 "├──────────────────────────────────────────────┤\n"
                 "│ • ρmin = -          |  As min = - cm²        │\n"
                 "│ • ρmax = -          |  As max = - cm²        │\n"
                 "│ • Verif. (ρ y ρmax): -                       │\n"
                 "└──────────────────────────────────────────────┘",
            size_hint_y=None, height=dp(150), halign='left', valign='top', font_size=13
        )
        self.label_cuantia_pos.bind(size=self.label_cuantia_pos.setter('text_size'))
        layout2.add_widget(self.label_cuantia_pos)

        scroll2.add_widget(layout2)
        self.screen2.add_widget(scroll2)
        self.sm.add_widget(self.screen2)

        # PESTAÑA 3: MOMENTO (-) CON TABLA DE CÁLCULO Y BLOQUE VSR/VDR INTEGRADO
        self.screen3 = Screen(name='tab3')
        scroll3 = ScrollView()
        layout3 = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15), size_hint_y=None)
        layout3.bind(minimum_height=layout3.setter('height'))
        
        layout3.add_widget(Label(text="HOJA 3: DISEÑO - MOMENTO NEGATIVO (-)", bold=True, size_hint_y=None, height=dp(30)))
        
        self.label_tabla_neg = Label(
            text="[ TABLA DE CÁLCULO - MOMENTO NEGATIVO ]\n• K = -\n• w = -\n• ρ = -\n• As = - cm²",
            size_hint_y=None, height=dp(130), halign='left', valign='top', font_size=14
        )
        self.label_tabla_neg.bind(size=self.label_tabla_neg.setter('text_size'))
        layout3.add_widget(self.label_tabla_neg)

        # Cuadro estructurado de Cuantías y VSR/VDR
        self.label_cuantia_neg = Label(
            text="┌──────────────────────────────────────────────┐\n"
                 "│        CÁLCULO CUANTÍA (MÍN / MÁX)           │\n"
                 "├──────────────────────────────────────────────┤\n"
                 "│ • ρmin = -          |  As min = - cm²        │\n"
                 "│ • ρmax = -          |  As max = - cm²        │\n"
                 "│ • Verif. (ρ y ρmax): -                       │\n"
                 "└──────────────────────────────────────────────┘",
            size_hint_y=None, height=dp(150), halign='left', valign='top', font_size=13
        )
        self.label_cuantia_neg.bind(size=self.label_cuantia_neg.setter('text_size'))
        layout3.add_widget(self.label_cuantia_neg)
        
        layout3.add_widget(Label(text="[ DETALLE DE ESTRIBUCIÓN Y ARMADO ]\n• Estribos: 1φ3/8\" @ 0.05, 10 @ 0.10, resto @ 0.20m", size_hint_y=None, height=dp(80), halign='left', valign='top'))

        scroll3.add_widget(layout3)
        self.screen3.add_widget(scroll3)
        self.sm.add_widget(self.screen3)

        root_layout.add_widget(self.sm)
        return root_layout

    def actualizar_estado_modo(self, instance):
        if self.btn_sa.state == 'down':
            self.box_acero_ca_panel.opacity = 0
            self.box_acero_ca_panel.disabled = True
            self.box_acero_ca_panel.height = 0

            for k in self.inputs_sa:
                self.inputs_sa[k].disabled = False
                if self.inputs_sa[k].text == '-':
                    defaults = {'b':'30', 'h':'65', 'd':'59', 'fc':'210', 'fy':'4200', 'mu_pos':'17.96', 'mu_neg':'25.14', 'phi':'0.9'}
                    self.inputs_sa[k].text = defaults.get(k, '')
            for k in self.inputs_ca:
                self.inputs_ca[k].text = '-'
                self.inputs_ca[k].disabled = True
        else:
            self.box_acero_ca_panel.opacity = 1
            self.box_acero_ca_panel.disabled = False
            self.box_acero_ca_panel.height = dp(85)

            for k in self.inputs_sa:
                self.inputs_sa[k].text = '-'
                self.inputs_sa[k].disabled = True
            for k in self.inputs_ca:
                if k != 'd':
                    self.inputs_ca[k].disabled = False
                    if self.inputs_ca[k].text == '-':
                        defaults = {'b':'30', 'h':'65', 'fc':'210', 'fy':'4200', 'mu_pos':'17.96', 'mu_neg':'25.14', 'phi':'0.9'}
                        self.inputs_ca[k].text = defaults.get(k, '')
                else:
                    self.inputs_ca[k].text = '[Calculado]'
                    self.inputs_ca[k].disabled = True

    def cambiar_pestana(self, nombre_tab):
        self.sm.current = nombre_tab
        self.btn_tab1.background_color = (0.1, 0.2
