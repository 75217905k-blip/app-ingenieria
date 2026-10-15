from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import math

class CalculadoraDisenoViga(App):
    def build(self):
        self.title = 'Diseño de Vigas - Cuantías'
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        
        root = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', padding=15, spacing=8, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        layout.add_widget(Label(text="DISEÑO DE VIGA (FALLA DÚCTIL)", font_size=20, bold=True, color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=35))
        
        layout.add_widget(Label(text="Norma de Diseño:", color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=18, halign="left"))
        self.norma = Spinner(text='Norma Peruana NTE E.060', values=('Norma Peruana NTE E.060', 'Código ACI 318'), size_hint_y=None, height=40, background_color=(0.15, 0.45, 0.7, 1))
        layout.add_widget(self.norma)
        
        self.b_input = self.crear_campo(layout, "Base b (cm):", "30")
        self.h_input = self.crear_campo(layout, "Altura h (cm):", "75")
        self.d_input = self.crear_campo(layout, "Peralte efectivo d (cm):", "69")
        self.fc_input = self.crear_campo(layout, "Concreto f'c (Kg/cm²):", "210")
        self.fy_input = self.crear_campo(layout, "Acero fy (Kg/cm²):", "4200")
        self.mu_input = self.crear_campo(layout, "Momento Último Mu (Tn·m):", "30")
        self.phi_input = self.crear_campo(layout, "Factor de reducción ø:", "0.9")
        
        btn_calcular = Button(text="CALCULAR ACERO", font_size=16, bold=True, background_color=(0.1, 0.6, 0.2, 1), size_hint_y=None, height=45)
        btn_calcular.bind(on_press=self.ejecutar_diseno)
        layout.add_widget(btn_calcular)
        
        self.resultado_label = Label(text="Resultados aparecerán aquí", font_size=15, color=(0, 0, 0, 1), halign="left", valign="top", size_hint_y=None, height=300)
        self.resultado_label.bind(size=self.resultado_label.setter('text_size'))
        layout.add_widget(self.resultado_label)
        
        root.add_widget(layout)
        return root

    def crear_campo(self, layout, texto_label, por_defecto):
        layout.add_widget(Label(text=texto_label, color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=18, halign="left"))
        txt_input = TextInput(text=por_defecto, input_filter='float', multiline=False, size_hint_y=None, height=36)
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
                self.resultado_label.text = "❌ ERROR: El momento Mu es excesivo para la sección."
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
            
            txt = f"📋 RESULTADOS [{nombre_norma}]:\n\n"
            txt += f"• Parámetro K: {k:.4f}\n• Parámetro w: {w:.4f}\n• Cuantía (ρ): {rho:.4f}\n\n"
            txt += f"• Acero Calculado: {as_calculado:.2f} cm²\n• Acero Mínimo: {as_min_norma:.2f} cm²\n• Acero Máximo: {as_max:.2f} cm²\n\n"
            txt += f"🔥 ACERO FINAL: {as_diseno:.2f} cm²\n\n"
            
            if as_calculado < as_min_norma:
                txt += "⚠️ NOTA: Se asignó el Acero Mínimo por norma."
            elif as_calculado > as_max:
                txt += "❌ ALERTA: ¡SECCIÓN SOBREFORZADA! Supera el máximo."
            else:
                txt += "✅ DISEÑO CORRECTO: Cumple con la cuantía."
                
            self.resultado_label.text = txt
        except Exception as e:
            self.resultado_label.text = f"❌ Error: {str(e)}"

if __name__ == '__main__':
    CalculadoraDisenoViga().run()
