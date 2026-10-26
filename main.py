import flet as ft
import math

# -----------------------------------------------------------------------------
# TABLA OFICIAL DE ACEROS LONGITUDINALES Y ESTRIBOS
# -----------------------------------------------------------------------------
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

def main(page: ft.Page):
    page.title = "Structural Dashboard - Concrete Beam Design"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    page.padding = 10
    page.scroll = ft.ScrollMode.AUTO

    # State variables
    current_norm = ft.Ref[str]()
    current_norm.current = "E.060"

    # Navigation bar
    nav_tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="1. Datos & Cuantías", icon=ft.icons.TUNE),
            ft.Tab(text="2. Momento (+)", icon=ft.icons.ADD_CIRCLE_OUTLINE),
            ft.Tab(text="3. Momento (-)", icon=ft.icons.REMOVE_CIRCLE_OUTLINE),
        ],
        expand=True,
    )

    # -----------------------------------------------------------------------------
    # HOJA 1: INPUT DATA & QUANTITIES
    # -----------------------------------------------------------------------------
    b_input = ft.TextField(label="Base b (cm) [Min 25]", value="30", width=180, border_radius=8, text_align=ft.TextAlign.CENTER)
    h_input = ft.TextField(label="Altura h (cm)", value="65", width=180, border_radius=8, text_align=ft.TextAlign.CENTER)
    fc_input = ft.TextField(label="Concreto f'c (kg/cm²)", value="210", width=180, border_radius=8, text_align=ft.TextAlign.CENTER)
    fy_input = ft.TextField(label="Acero fy (kg/cm²)", value="4200", width=180, border_radius=8, text_align=ft.TextAlign.CENTER)
    mu_pos_input = ft.TextField(label="Momento Mu (+) (Tn·m)", value="17.96", width=180, border_radius=8, text_align=ft.TextAlign.CENTER)
    mu_neg_input = ft.TextField(label="Momento Mu (-) (Tn·m)", value="25.14", width=180, border_radius=8, text_align=ft.TextAlign.CENTER)
    phi_input = ft.TextField(label="Factor ø (Flexión)", value="0.90", width=180, border_radius=8, text_align=ft.TextAlign.CENTER)

    modo_d_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="prediseno", label="Prediseño (d = h - 6 cm)"),
            ft.Radio(value="detallado", label="Detallado Riguroso (1 Capa)"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="prediseno"
    )

    acero_long_dropdown = ft.Dropdown(
        label="Ø Acero Tentativo Longitudinal",
        value="3/4\"",
        width=250,
        options=[ft.dropdown.Option(item[1], f"{item[1]} (ø = {item[3]} cm)") for item in TABLA_ACEROS if item[3] >= 1.27],
        visible=False
    )

    e060_sismo_check = ft.Checkbox(label="Aplicar ρmax sísmico (0.50 ρb)", value=False, visible=True)

    lbl_d_val = ft.Text("59.00 cm", size=18, weight=ft.FontWeight.BOLD, color="#38BDF8")
    lbl_estribo_detected = ft.Text("Estribo autoseleccionado: 3/8\" (0.95 cm)", size=12, color="#94A3B8")

    lbl_status_h1 = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
    card_results_h1 = ft.Column(spacing=8)

    def on_modo_d_change(e):
        acero_long_dropdown.visible = (modo_d_radio.value == "detallado")
        page.update()

    modo_d_radio.on_change = on_modo_d_change

    def calcular_hoja_1(e):
        try:
            b = float(b_input.value)
            h = float(h_input.value)
            fc = float(fc_input.value)
            fy = float(fy_input.value)
            mu_pos = float(mu_pos_input.value)
            mu_neg = float(mu_neg_input.value)
            phi = float(phi_input.value)

            # Validation constraint
            if b < 25.0:
                lbl_status_h1.value = "❌ ERROR: El ancho 'b' debe ser como mínimo 25.00 cm según norma."
                lbl_status_h1.color = "#EF4444"
                card_results_h1.controls.clear()
                page.update()
                return

            lbl_status_h1.value = "✓ CÁLCULOS ACTUALIZADOS CORRECTAMENTE"
            lbl_status_h1.color = "#06D6A0"

            # Calculation of 'd'
            if modo_d_radio.value == "prediseno":
                d = h - 6.0
                estribo_str = "N/A (Prediseño)"
            else:
                rec = 4.0
                phi_long_cm = 1.91
                for b_name, p_str, area_val, diam_val in TABLA_ACEROS:
                    if p_str == acero_long_dropdown.value:
                        phi_long_cm = diam_val
                        break
                
                if phi_long_cm >= 2.54:
                    diam_estribo = 1.27
                    estribo_str = "1/2\" (1.27 cm)"
                else:
                    diam_estribo = 0.95
                    estribo_str = "3/8\" (0.95 cm)"

                d = h - rec - diam_estribo - (phi_long_cm / 2.0)
                lbl_estribo_detected.value = f"Estribo autoseleccionado: {estribo_str}"

            lbl_d_val.value = f"{d:.2f} cm"

            # Beta 1 reduction logic
            if fc <= 280.0:
                beta1 = 0.85
            else:
                beta1 = max(0.85 - (0.05 * (fc - 280.0) / 70.0), 0.65)

            # Norm logic selection
            if current_norm.current == "E.060":
                rho_b = 0.85 * beta1 * (fc / fy) * (6000.0 / (fy + 6000.0))
                rho_min = (0.70 * math.sqrt(fc)) / fy
                factor_max = 0.50 if e060_sismo_check.value else 0.75
                rho_max = factor_max * rho_b
            else:
                rho_min = max((0.80 * math.sqrt(fc)) / fy, 14.0 / fy)
                rho_max = 0.32 * beta1 * (fc / fy)

            as_min = rho_min * b * d
            as_max = rho_max * b * d

            # Pos & Neg Moments
            k_p = (mu_pos * 100000.0) / (phi * fc * b * (d ** 2))
            w_p = (1.0 - math.sqrt(max(0.0, 1.0 - 2.36 * k_p))) / 1.18
            rho_p = w_p * fc / fy
            as_p = rho_p * b * d

            k_n = (mu_neg * 100000.0) / (phi * fc * b * (d ** 2))
            w_n = (1.0 - math.sqrt(max(0.0, 1.0 - 2.36 * k_n))) / 1.18
            rho_n = w_n * fc / fy
            as_n = rho_n * b * d

            # VSR vs VDR check
            state_p = "VSR (Viga Simplemente Reforzada)" if rho_min <= rho_p <= rho_max else "VDR (Viga Doblemente Reforzada)"
            state_n = "VSR (Viga Simplemente Reforzada)" if rho_min <= rho_n <= rho_max else "VDR (Viga Doblemente Reforzada)"

            card_results_h1.controls = [
                ft.Divider(),
                ft.Text("MÁXIMOS Y MÍNIMOS DE DISEÑO", size=16, weight=ft.FontWeight.BOLD, color="#38BDF8"),
                ft.Row([
                    ft.Text(f"• β1 (Whitney): {beta1:.4f}"),
                    ft.Text(f"• ρmin: {rho_min:.4f}  ──>  As min: {as_min:.2f} cm²", weight="bold", color="#38BDF8"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text(f"• Factor ρmax: {('ACI 0.32' if current_norm.current=='ACI 318' else ('0.50 Sís' if e060_sismo_check.value else '0.75 Standard'))}"),
                    ft.Text(f"• ρmax: {rho_max:.4f}  ──>  As max: {as_max:.2f} cm²", weight="bold", color="#38BDF8"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Text("VALIDACIÓN POR MOMENTO POSITIVO (+)", size=14, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Text(f"ρ calc: {rho_p:.4f} | As calc: {as_p:.2f} cm²"),
                    ft.Container(
                        content=ft.Text(state_p, weight="bold", color="#FFFFFF", size=12),
                        bgcolor="#06D6A0" if "VSR" in state_p else "#EF4444",
                        padding=6, border_radius=6
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Text("VALIDACIÓN POR MOMENTO NEGATIVO (-)", size=14, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Text(f"ρ calc: {rho_n:.4f} | As calc: {as_n:.2f} cm²"),
                    ft.Container(
                        content=ft.Text(state_n, weight="bold", color="#FFFFFF", size=12),
                        bgcolor="#06D6A0" if "VSR" in state_n else "#EF4444",
                        padding=6, border_radius=6
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ]

            # Update Hoja 2 & 3
            actualizar_hoja_2(b, h, d, fc, fy, mu_pos, phi, k_p, w_p, rho_p, as_p, state_p)
            actualizar_hoja_3(b, h, d, fc, fy, mu_neg, phi, k_n, w_n, rho_n, as_n, state_n)

            page.update()
        except ValueError:
            lbl_status_h1.value = "❌ ERROR: Ingrese valores numéricos válidos en todos los campos."
            lbl_status_h1.color = "#EF4444"
            page.update()

    # -----------------------------------------------------------------------------
    # DYNAMIC BEAM CANVAS DRAWING FUNCTION
    # -----------------------------------------------------------------------------
    def crear_canvas_viga(b, h, d, estado_text):
        scale = min(180.0 / b, 220.0 / h)
        w_px = b * scale
        h_px = h * scale
        x_center = (280.0 - w_px) / 2.0
        y_center = (250.0 - h_px) / 2.0

        is_ok = "VSR" in estado_text
        border_color = "#06D6A0" if is_ok else "#EF4444"

        # Canvas Elements
        elements = [
            # Concrete Outline
            ft.canvas.Rect(x=x_center, y=y_center, width=w_px, height=h_px, paint=ft.Paint(color=border_color, style=ft.PaintingStyle.STROKE, stroke_width=3)),
            # Stirrup
            ft.canvas.Rect(x=x_center + 10, y=y_center + 10, width=w_px - 20, height=h_px - 20, paint=ft.Paint(color="#38BDF8", style=ft.PaintingStyle.STROKE, stroke_width=1.5)),
            # Reinforcement Bars (Tension area - bottom)
            ft.canvas.Circle(x=x_center + 18, y=y_center + h_px - 18, radius=6, paint=ft.Paint(color="#0284C7", style=ft.PaintingStyle.FILL)),
            ft.canvas.Circle(x=x_center + w_px - 18, y=y_center + h_px - 18, radius=6, paint=ft.Paint(color="#0284C7", style=ft.PaintingStyle.FILL)),
            # Dimensions Labels
            ft.canvas.Text(x=x_center + (w_px/2) - 15, y=y_center + h_px + 5, text=f"b = {b:.0f} cm", style=ft.TextStyle(color="#94A3B8", size=11, weight=ft.FontWeight.BOLD)),
            ft.canvas.Text(x=x_center - 55, y=y_center + (h_px/2) - 5, text=f"h = {h:.0f} cm", style=ft.TextStyle(color="#94A3B8", size=11, weight=ft.FontWeight.BOLD)),
            ft.canvas.Text(x=x_center + w_px + 8, y=y_center + (h_px/2) - 5, text=f"d = {d:.1f} cm", style=ft.TextStyle(color="#38BDF8", size=11, weight=ft.FontWeight.BOLD)),
        ]

        return ft.Container(
            content=ft.cv.Canvas(elements, width=300, height=270),
            alignment=ft.alignment.center,
            bgcolor="#1E293B",
            border_radius=10,
            padding=10
        )

    # -----------------------------------------------------------------------------
    # HOJA 2: MOMENTO POSITIVO (+)
    # -----------------------------------------------------------------------------
    container_h2 = ft.Column(spacing=10)

    def actualizar_hoja_2(b, h, d, fc, fy, mu, phi, k, w, rho, as_calc, state_str):
        a_whitney = (as_calc * fy) / (0.85 * fc * b)
        
        container_h2.controls = [
            ft.Text("DISEÑO Y DETALLADO POR MOMENTO POSITIVO (+)", size=18, weight=ft.FontWeight.BOLD, color="#38BDF8"),
            ft.Row([
                ft.Column([
                    ft.Text(f"• Momento Mu (+): {mu:.2f} Tn·m"),
                    ft.Text(f"• Coeficiente K: {k:.4f}"),
                    ft.Text(f"• Cuantía Mecánica w: {w:.4f}"),
                    ft.Text(f"• Cuantía Requerida ρ: {rho:.4f}"),
                    ft.Text(f"• ÁREA REQUERIDA As: {as_calc:.2f} cm²", size=16, weight="bold", color="#38BDF8"),
                    ft.Text(f"• Bloque de Whitney (a): {a_whitney:.2f} cm", size=14, weight="bold", color="#F59E0B"),
                    ft.SizedBox(height=10),
                    ft.Container(
                        content=ft.Text(state_str, weight="bold", color="#FFFFFF"),
                        bgcolor="#06D6A0" if "VSR" in state_str else "#EF4444",
                        padding=10, border_radius=8
                    )
                ], expand=True),
                crear_canvas_viga(b, h, d, state_str)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]

    # -----------------------------------------------------------------------------
    # HOJA 3: MOMENTO NEGATIVO (-)
    # -----------------------------------------------------------------------------
    container_h3 = ft.Column(spacing=10)

    def actualizar_hoja_3(b, h, d, fc, fy, mu, phi, k, w, rho, as_calc, state_str):
        a_whitney = (as_calc * fy) / (0.85 * fc * b)

        container_h3.controls = [
            ft.Text("DISEÑO Y DETALLADO POR MOMENTO NEGATIVO (-)", size=18, weight=ft.FontWeight.BOLD, color="#38BDF8"),
            ft.Row([
                ft.Column([
                    ft.Text(f"• Momento Mu (-): {mu:.2f} Tn·m"),
                    ft.Text(f"• Coeficiente K: {k:.4f}"),
                    ft.Text(f"• Cuantía Mecánica w: {w:.4f}"),
                    ft.Text(f"• Cuantía Requerida ρ: {rho:.4f}"),
                    ft.Text(f"• ÁREA REQUERIDA As: {as_calc:.2f} cm²", size=16, weight="bold", color="#38BDF8"),
                    ft.Text(f"• Bloque de Whitney (a): {a_whitney:.2f} cm", size=14, weight="bold", color="#F59E0B"),
                    ft.SizedBox(height=10),
                    ft.Container(
                        content=ft.Text(state_str, weight="bold", color="#FFFFFF"),
                        bgcolor="#06D6A0" if "VSR" in state_str else "#EF4444",
                        padding=10, border_radius=8
                    )
                ], expand=True),
                crear_canvas_viga(b, h, d, state_str)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]

    # -----------------------------------------------------------------------------
    # COVER / CARÁTULA SCREEN & NORM SELECTION
    # -----------------------------------------------------------------------------
    def select_norm_and_start(norm_code):
        current_norm.current = norm_code
        e060_sismo_check.visible = (norm_code == "E.060")
        page.controls.clear()
        
        # Build layout with tabs
        page.add(
            ft.Column([
                ft.Row([
                    ft.Text("ConcreteDesign Pro", size=22, weight="bold", color="#FFFFFF"),
                    ft.Container(
                        content=ft.Text(f"NORMA ACTIVADA: {norm_code}", weight="bold", color="#FFFFFF", size=12),
                        bgcolor="#0284C7", padding=8, border_radius=6
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                nav_tabs,
                ft.Container(id="tab_content", content=view_hoja1(), expand=True)
            ], expand=True)
        )
        calcular_hoja_1(None)
        page.update()

    def on_tab_change(e):
        idx = nav_tabs.selected_index
        tab_container = page.controls[0].controls[2]
        if idx == 0:
            tab_container.content = view_hoja1()
        elif idx == 1:
            tab_container.content = view_hoja2()
        elif idx == 2:
            tab_container.content = view_hoja3()
        page.update()

    nav_tabs.on_change = on_tab_change

    def view_hoja1():
        return ft.Container(
            content=ft.Column([
                ft.Text("1. PARAMETROS Y CONFIGURACIÓN DE SECCIÓN", size=16, weight="bold", color="#38BDF8"),
                modo_d_radio,
                acero_long_dropdown,
                e060_sismo_check,
                ft.Divider(),
                ft.Row([b_input, h_input, fc_input, fy_input], alignment=ft.MainAxisAlignment.SPACE_EVENLY, wrap=True),
                ft.Row([mu_pos_input, mu_neg_input, phi_input], alignment=ft.MainAxisAlignment.SPACE_EVENLY, wrap=True),
                ft.Row([
                    ft.Text("Peralte Efectivo Calculado (d):", weight="bold"),
                    lbl_d_val,
                ], alignment=ft.MainAxisAlignment.CENTER),
                lbl_estribo_detected,
                ft.SizedBox(height=10),
                ft.ElevatedButton(
                    "EJECUTAR CÁLCULOS Y ACTUALIZAR",
                    icon=ft.icons.CALCULATE,
                    on_click=calcular_hoja_1,
                    style=ft.ButtonStyle(bgcolor="#0284C7", color="#FFFFFF", width=400, padding=18)
                ),
                lbl_status_h1,
                card_results_h1
            ], spacing=10),
            bgcolor="#1E293B", padding=20, border_radius=12
        )

    def view_hoja2():
        return ft.Container(content=container_h2, bgcolor="#1E293B", padding=20, border_radius=12)

    def view_hoja3():
        return ft.Container(content=container_h3, bgcolor="#1E293B", padding=20, border_radius=12)

    # -----------------------------------------------------------------------------
    # INITIAL LANDING PAGE (CARÁTULA)
    # -----------------------------------------------------------------------------
    landing_view = ft.Container(
        content=ft.Column([
            ft.Icon(ft.icons.ENGINEERING, size=90, color="#38BDF8"),
            ft.Text("STRUCTURAL DASHBOARD", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
            ft.Text("Diseño Profesional de Vigas por Flexión (VSR & VDR)", size=16, color="#94A3B8"),
            ft.SizedBox(height=20),
            ft.Text("SELECCIONE LA NORMA DE DISEÑO PARA INICIAR:", size=14, weight="bold", color="#38BDF8"),
            ft.Row([
                ft.ElevatedButton(
                    "NORMA NTP E.060",
                    icon=ft.icons.ASSIGNMENT,
                    on_click=lambda e: select_norm_and_start("E.060"),
                    style=ft.ButtonStyle(bgcolor="#0284C7", color="#FFFFFF", padding=20, shape=ft.RoundedRectangleBorder(radius=10))
                ),
                ft.ElevatedButton(
                    "CÓDIGO ACI 318",
                    icon=ft.icons.VERIFY,
                    on_click=lambda e: select_norm_and_start("ACI 318"),
                    style=ft.ButtonStyle(bgcolor="#3B82F6", color="#FFFFFF", padding=20, shape=ft.RoundedRectangleBorder(radius=10))
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
        expand=True,
        alignment=ft.alignment.center
    )

    page.add(landing_view)

if __name__ == "__main__":
    ft.app(target=main)
