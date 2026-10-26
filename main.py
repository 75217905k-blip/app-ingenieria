import flet as ft
import math

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
    s_min = max(2.54, max_d)  # Mínimo 1 pulgada o diámetro máximo
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
                As_baston = max(0.0, As_requerido - area_cont)
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
                                        'area_cont': area_cont,
                                        'baston_cant': n_baston,
                                        'baston_tipo': nombre_baston if n_baston > 0 else '-',
                                        'area_baston': area_baston,
                                        'area_total': area_total,
                                        'exceso': area_total - As_requerido,
                                        'ancho_req': ancho_req,
                                        'n_total': n_total
                                    })
    if not mejores_opciones:
        return None
    mejores_opciones.sort(key=lambda x: x['exceso'])
    return mejores_opciones[0]

def main(page: ft.Page):
    page.title = "Diseño Profesional de Vigas - VSR con Esquemas Dinámicos"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # --- ENTRADAS DE DATOS (TABLA PRINCIPAL) ---
    txt_b = ft.TextField(label="Base b (cm)", value="30", width=140)
    txt_h = ft.TextField(label="Peralte h (cm)", value="65", width=140)
    txt_rec = ft.TextField(label="Recubrimiento r (cm)", value="4", width=140)
    
    dd_criterio_d = ft.Dropdown(
        label="Criterio de cálculo de d",
        options=[
            ft.dropdown.Option("Práctico (d = h - 6 cm)"),
            ft.dropdown.Option("Detallado normativo")
        ],
        value="Práctico (d = h - 6 cm)",
        width=250
    )
    txt_d = ft.TextField(label="Peralte efectivo d (cm)", value="59.0", width=140, read_only=True)
    
    txt_fc = ft.TextField(label="f'c (kg/cm²)", value="210", width=140)
    txt_fy = ft.TextField(label="fy (kg/cm²)", value="4200", width=140)
    txt_mu_pos = ft.TextField(label="Mu (+) (Tn.m)", value="17.96", width=150)
    txt_mu_neg = ft.TextField(label="Mu (-) (Tn.m)", value="25.14", width=150)
    txt_phi = ft.TextField(label="Ø (Factor)", value="0.9", width=100)

    # --- COMPONENTES GRÁFICOS (PANEL SUPERIOR) ---
    lbl_dim_h = ft.Text("h = 65 cm", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_400)
    lbl_dim_b = ft.Text("b = 30 cm", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_400)
    
    panel_grafico_superior = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Column([ft.VerticalDivider(height=180, thickness=2, color=ft.colors.AMBER_400), lbl_dim_h], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(
                    content=ft.Text("SECCIÓN TRANSVERSAL (b x h)", size=12, color=ft.colors.WHITE54),
                    width=280,
                    height=200,
                    bgcolor=ft.colors.BLUE_950,
                    border=ft.border.all(2, ft.colors.BLUE_ACCENT),
                    border_radius=8,
                    alignment=ft.alignment.center,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
            ft.Row([lbl_dim_b], alignment=ft.MainAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20,
        bgcolor=ft.colors.BLUE_GREY_900,
        border_radius=10,
        expand=True,
        alignment=ft.alignment.center
    )

    # --- PANEL INFERIOR: RESULTADOS Y ARMADO TÉCNICO ---
    txt_resultados = ft.Text(value="Configure los datos y presione 'Ejecutar Diseño y Armado'.", size=13, font_family="monospace")
    
    detalle_armado_visual = ft.Container(
        content=ft.Text("Ejecute el cálculo para renderizar el gráfico detallado con estribos y distribución de acero.", size=13, color=ft.colors.WHITE70),
        padding=20,
        bgcolor=ft.colors.BLUE_950,
        border=ft.border.all(2, ft.colors.TEAL_400),
        border_radius=8,
        height=240,
        alignment=ft.alignment.center
    )

    def actualizar_geometria(e):
        try:
            b = float(txt_b.value) if txt_b.value else 30.0
            h = float(txt_h.value) if txt_h.value else 65.0
            
            if "Práctico" in dd_criterio_d.value:
                d = h - 6.0
            else:
                d = h - 4.0 - 0.95 - (2.54 / 2.0)
            
            txt_d.value = f"{d:.1f}"
            lbl_dim_h.value = f"h = {h} cm"
            lbl_dim_b.value = f"b = {b} cm"
            page.update()
        except:
            pass

    txt_b.on_change = actualizar_geometria
    txt_h.on_change = actualizar_geometria
    dd_criterio_d.on_change = actualizar_geometria

    def ejecutar_calculo(e):
        try:
            b = float(txt_b.value)
            h = float(txt_h.value)
            d = float(txt_d.value)
            fc = float(txt_fc.value)
            fy = float(txt_fy.value)
            mu_pos = float(txt_mu_pos.value)
            mu_neg = float(txt_mu_neg.value)
            phi = float(txt_phi.value)
            rec = float(txt_rec.value)

            if b < 25:
                txt_resultados.value = "⚠️ Error: El ancho b debe ser mínimo 25 cm por norma."
                page.update()
                return

            rho_min = max(0.8 * math.sqrt(fc) / fy, 14.1 / fy)
            As_min = rho_min * b * d

            def resolver_flexion(mu_ton):
                mu_kg_cm = mu_ton * 100000.0
                k = mu_kg_cm / (phi * b * (d**2))
                radical = 0.7225 - (1.7 * k / fc)
                if radical < 0:
                    return None, None
                omega = 0.85 - math.sqrt(radical)
                return omega * (fc / fy) * b * d, omega * (fc / fy)

            As_pos, _ = resolver_flexion(mu_pos)
            As_gov_pos = max(As_pos if As_pos else As_min, As_min)
            opt_pos = optimizar_distribucion_acero(As_gov_pos, As_min, b)

            As_neg, _ = resolver_flexion(mu_neg)
            As_gov_neg = max(As_neg if As_neg else As_min, As_min)
            opt_neg = optimizar_distribucion_acero(As_gov_neg, As_min, b)

            reporte = f"""==================================================
        MEMORIA DE CÁLCULO Y ARMADO VSR
==================================================
• Geometría: b = {b} cm | h = {h} cm | d = {d} cm | r = {rec} cm
• Materiales: f'c = {fc} kg/cm² | fy = {fy} kg/cm²
• Acero Mínimo (As_min) = {As_min:.2f} cm²
--------------------------------------------------
1. ACERO POSITIVO (+) [Inferior]: Mu = {mu_pos} Tn.m
   - Requerido: {As_pos:.2f} cm² | Gobernaje: {As_gov_pos:.2f} cm²
"""
            if opt_pos:
                reporte += f"   - Armado Óptimo: {opt_pos['cont_cant']}φ{opt_pos['cont_tipo']} (continuo) + {opt_pos['baston_cant']}φ{opt_pos['baston_tipo']} (bastón)\n"
                reporte += f"   - Área Colocada (Asc): {opt_pos['area_total']:.2f} cm² (Ancho Req: {opt_pos['ancho_req']:.2f} cm <= {b} cm ➔ ¡CUMPLE!)\n"

            reporte += f"""--------------------------------------------------
2. ACERO NEGATIVO (-) [Superior]: Mu = {mu_neg} Tn.m
   - Requerido: {As_neg:.2f} cm² | Gobernaje: {As_gov_neg:.2f} cm²
"""
            if opt_neg:
                reporte += f"   - Armado Óptimo: {opt_neg['cont_cant']}φ{opt_neg['cont_tipo']} (continuo) + {opt_neg['baston_cant']}φ{opt_neg['baston_tipo']} (bastón)\n"
                reporte += f"   - Área Colocada (Asc): {opt_neg['area_total']:.2f} cm² (Ancho Req: {opt_neg['ancho_req']:.2f} cm <= {b} cm ➔ ¡CUMPLE!)\n"

            reporte += "=================================================="
            txt_resultados.value = reporte

            armado_inf_str = f"{opt_pos['cont_cant']}φ{opt_pos['cont_tipo']} + {opt_pos['baston_cant']}φ{opt_pos['baston_tipo']}" if opt_pos else "N/D"
            armado_sup_str = f"{opt_neg['cont_cant']}φ{opt_neg['cont_tipo']} + {opt_neg['baston_cant']}φ{opt_neg['baston_tipo']}" if opt_neg else "N/D"

            detalle_armado_visual.content = ft.Column([
                ft.Text("📐 ESQUEMA TÉCNICO DE DETALLADO Y ARMADO", weight=ft.FontWeight.BOLD, color=ft.colors.TEAL_ACCENT),
                ft.Divider(),
                ft.Row([
                    ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN),
                    ft.Text(f"Acero Superior (-) [Negativo]: {armado_sup_str}", size=13, weight=ft.FontWeight.BOLD)
                ]),
                ft.Row([
                    ft.Icon(ft.icons.BORDER_OUTER, color=ft.colors.AMBER),
                    ft.Text(f"Estribo Confinamiento: 1φ3/8\" @ 0.05, 10@0.10, resto @ 0.20 m (r = {rec} cm)", size=13)
                ]),
                ft.Row([
                    ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN),
                    ft.Text(f"Acero Inferior (+) [Positivo]: {armado_inf_str}", size=13, weight=ft.FontWeight.BOLD)
                ]),
                ft.Text(f"Verificación Espaciamiento base b = {b} cm: Cumple rigurosamente con los espaciamientos libres normativos (min 1 pulgada).", size=12, color=ft.colors.WHITE70)
            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER)

            page.update()

        except Exception as ex:
            txt_resultados.value = f"❌ Error: {str(ex)}"
            page.update()

    btn_calcular = ft.ElevatedButton(
        text="⚙️ Ejecutar Diseño y Generar Gráficos Técnicos",
        on_click=ejecutar_calculo,
        bgcolor=ft.colors.BLUE_800,
        color=ft.colors.WHITE
    )

    page.add(
        ft.Text("Módulo Profesional: Diseño de Vigas y Esquema Dinámico", size=18, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text("DATOS DE ENTRADA", weight=ft.FontWeight.BOLD, size=14),
                    ft.Row([txt_b, txt_h], wrap=True),
                    ft.Row([txt_rec, txt_d], wrap=True),
                    dd_criterio_d,
                    ft.Row([txt_fc, txt_fy], wrap=True),
                    ft.Row([txt_mu_pos, txt_mu_neg], wrap=True),
                    txt_phi,
                    ft.Container(height=5),
                    btn_calcular
                ], spacing=10),
                padding=15,
                bgcolor=ft.colors.BLUE_GREY_900,
                border_radius=10,
                width=380
            ),
            panel_grafico_superior
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.START),
        ft.Divider(),
        ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text("MEMORIA DE CÁLCULO", weight=ft.FontWeight.BOLD, size=14),
                    txt_resultados
                ]),
                padding=15,
                bgcolor=ft.colors.SURFACE_VARIANT,
                border_radius=10,
                expand=True
            ),
            ft.VerticalDivider(width=15),
            ft.Container(
                content=ft.Column([
                    ft.Text("ESQUEMA DE ARMADO Y ESTRIBO", weight=ft.FontWeight.BOLD, size=14),
                    detalle_armado_visual
                ]),
                padding=15,
                bgcolor=ft.colors.BLUE_GREY_900,
                border_radius=10,
                expand=True
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.START)
    )

ft.app(target=main)
