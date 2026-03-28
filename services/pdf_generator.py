"""
Generador de informes PDF neuropsicológicos
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import plotly.graph_objects as go
import os
from typing import Dict, List
import tempfile


class NeuroPsychReport:
    """Generador de informes PDF para evaluaciones neuropsicológicas"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados"""
        
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            leading=14
        ))
        
        # Pie de página
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))
    
    def generate_report(
        self,
        patient_data: Dict,
        test_sessions: List[Dict],
        output_filename: str = None
    ) -> str:
        """
        Generar informe PDF completo
        
        Args:
            patient_data: Datos del paciente (id, edad, educación, lateralidad)
            test_sessions: Lista de sesiones de test con resultados
            output_filename: Nombre del archivo de salida (opcional)
        
        Returns:
            Ruta al archivo PDF generado
        """
        
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            patient_id = patient_data.get('id', 'unknown')[:8]
            output_filename = f"informe_{patient_id}_{timestamp}.pdf"
        
        filepath = os.path.join(self.output_dir, output_filename)
        
        # Crear documento
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Contenido del informe
        story = []
        
        # Encabezado
        story.extend(self._build_header(patient_data))
        story.append(Spacer(1, 0.5*cm))
        
        # Datos demográficos
        story.extend(self._build_demographics(patient_data))
        story.append(Spacer(1, 0.5*cm))
        
        # Resultados de tests
        story.extend(self._build_test_results(test_sessions))
        story.append(Spacer(1, 0.5*cm))
        
        # Resumen y perfil cognitivo
        story.extend(self._build_summary(test_sessions))
        
        # Pie de página
        story.append(Spacer(1, 1*cm))
        story.extend(self._build_footer())
        
        # Generar PDF
        doc.build(story)
        
        return filepath
    
    def _build_header(self, patient_data: Dict) -> List:
        """Construir encabezado del informe"""
        elements = []
        
        # Título
        title = Paragraph(
            "INFORME NEUROPSICOLÓGICO",
            self.styles['CustomTitle']
        )
        elements.append(title)
        
        # Fecha de emisión
        fecha = datetime.now().strftime("%d/%m/%Y")
        fecha_para = Paragraph(
            f"<i>Fecha de emisión: {fecha}</i>",
            self.styles['CustomBody']
        )
        elements.append(fecha_para)
        
        return elements
    
    def _build_demographics(self, patient_data: Dict) -> List:
        """Construir sección de datos demográficos"""
        elements = []
        
        # Subtítulo
        subtitle = Paragraph(
            "Datos del Paciente",
            self.styles['CustomHeading']
        )
        elements.append(subtitle)
        
        # Tabla de datos
        data = [
            ['ID Paciente:', patient_data.get('id', 'N/A')[:12] + '...'],
            ['Edad:', f"{patient_data.get('age', 'N/A')} años"],
            ['Escolaridad:', f"{patient_data.get('education_years', 'N/A')} años"],
            ['Lateralidad:', patient_data.get('laterality', 'N/A').capitalize()]
        ]
        
        table = Table(data, colWidths=[5*cm, 10*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        
        elements.append(table)
        
        return elements
    
    def _build_test_results(self, test_sessions: List[Dict]) -> List:
        """Construir sección de resultados de tests"""
        elements = []
        
        # Subtítulo
        subtitle = Paragraph(
            "Resultados de Evaluación",
            self.styles['CustomHeading']
        )
        elements.append(subtitle)
        
        if not test_sessions:
            no_data = Paragraph(
                "<i>No hay datos de tests disponibles</i>",
                self.styles['CustomBody']
            )
            elements.append(no_data)
            return elements
        
        # Tabla resumen de todos los tests
        table_data = [['Test', 'Fecha', 'PB', 'PE', 'Percentil', 'Clasificación']]
        
        for session in test_sessions:
            test_type = session.get('test_type', 'N/A')
            fecha = session.get('date', 'N/A')
            if isinstance(fecha, datetime):
                fecha = fecha.strftime("%d/%m/%Y")
            
            raw_data = session.get('raw_data', {})
            scores = session.get('calculated_scores', {})
            
            # Puntuación bruta (depende del test)
            pb = self._extract_main_score(test_type, raw_data)
            
            # Puntuaciones normativas
            pe = scores.get('puntuacion_escalar', 'N/A')
            percentil = scores.get('percentil', 'N/A')
            if isinstance(percentil, (int, float)):
                percentil = f"{percentil:.1f}"
            
            clasificacion = scores.get('clasificacion', 'N/A')
            
            # Color según clasificación
            row_data = [test_type, fecha, str(pb), str(pe), str(percentil), clasificacion]
            table_data.append(row_data)
        
        # Crear tabla
        col_widths = [3.5*cm, 2.5*cm, 1.5*cm, 1.5*cm, 2*cm, 3*cm]
        table = Table(table_data, colWidths=col_widths)
        
        # Estilos de tabla
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]
        
        # Colorear clasificaciones
        for i, session in enumerate(test_sessions, start=1):
            clasificacion = session.get('calculated_scores', {}).get('clasificacion', '')
            if clasificacion == 'Superior':
                table_style.append(('BACKGROUND', (5, i), (5, i), colors.HexColor('#d1fae5')))
            elif clasificacion == 'Normal':
                table_style.append(('BACKGROUND', (5, i), (5, i), colors.HexColor('#dbeafe')))
            elif clasificacion == 'Limítrofe':
                table_style.append(('BACKGROUND', (5, i), (5, i), colors.HexColor('#fef3c7')))
            elif clasificacion == 'Deficitario':
                table_style.append(('BACKGROUND', (5, i), (5, i), colors.HexColor('#fee2e2')))
        
        table.setStyle(TableStyle(table_style))
        elements.append(table)
        
        # Detalles de cada test
        elements.append(Spacer(1, 0.5*cm))
        
        for session in test_sessions:
            elements.extend(self._build_test_detail(session))
            elements.append(Spacer(1, 0.3*cm))
        
        return elements
    
    def _build_test_detail(self, session: Dict) -> List:
        """Construir detalles de un test específico"""
        elements = []
        
        test_type = session.get('test_type', 'Test')
        
        # Subtítulo del test
        test_title = Paragraph(
            f"<b>{test_type}</b>",
            self.styles['Normal']
        )
        elements.append(test_title)
        
        # Observaciones cualitativas
        qualitative = session.get('qualitative_data', {})
        if qualitative and any(qualitative.values()):
            obs_text = "<i>Observaciones: </i>"
            
            if qualitative.get('observaciones_proceso'):
                obs_text += qualitative['observaciones_proceso']
            
            if qualitative.get('checklist'):
                checklist = qualitative['checklist']
                obs_items = [f"{k}: {v}" for k, v in checklist.items() if v]
                if obs_items:
                    obs_text += " | " + ", ".join(obs_items)
            
            obs_para = Paragraph(obs_text, self.styles['CustomBody'])
            elements.append(obs_para)
        
        return elements
    
    def _build_summary(self, test_sessions: List[Dict]) -> List:
        """Construir resumen y análisis del perfil cognitivo"""
        elements = []
        
        if not test_sessions:
            return elements
        
        # Subtítulo
        subtitle = Paragraph(
            "Perfil Cognitivo",
            self.styles['CustomHeading']
        )
        elements.append(subtitle)
        
        # Calcular estadísticas
        pes = [s.get('calculated_scores', {}).get('puntuacion_escalar', 0) 
               for s in test_sessions 
               if s.get('calculated_scores', {}).get('puntuacion_escalar')]
        
        percentiles = [s.get('calculated_scores', {}).get('percentil', 0) 
                       for s in test_sessions 
                       if s.get('calculated_scores', {}).get('percentil')]
        
        if pes:
            mean_pe = sum(pes) / len(pes)
            mean_percentil = sum(percentiles) / len(percentiles) if percentiles else 0
            
            summary_text = f"""
            El paciente completó {len(test_sessions)} pruebas neuropsicológicas. 
            La puntuación escalar media es <b>{mean_pe:.1f}</b> (PE), 
            correspondiente al percentil <b>{mean_percentil:.1f}</b>.
            """
            
            summary_para = Paragraph(summary_text, self.styles['CustomBody'])
            elements.append(summary_para)
            
            # Áreas destacadas
            if pes:
                max_pe = max(pes)
                min_pe = min(pes)
                
                max_idx = pes.index(max_pe)
                min_idx = pes.index(min_pe)
                
                best_test = test_sessions[max_idx].get('test_type', 'N/A')
                worst_test = test_sessions[min_idx].get('test_type', 'N/A')
                
                highlights = f"""
                <br/><br/>
                <b>Área de mayor rendimiento:</b> {best_test} (PE={max_pe})<br/>
                <b>Área de menor rendimiento:</b> {worst_test} (PE={min_pe})
                """
                
                highlights_para = Paragraph(highlights, self.styles['CustomBody'])
                elements.append(highlights_para)
        
        return elements
    
    def _build_footer(self) -> List:
        """Construir pie de página"""
        elements = []
        
        footer_text = """
        <i>Este informe ha sido generado automáticamente. Los datos son confidenciales 
        y están sujetos al RGPD. Documento sin firmas digitales.</i>
        """
        
        footer = Paragraph(footer_text, self.styles['Footer'])
        elements.append(footer)
        
        return elements
    
    def _extract_main_score(self, test_type: str, raw_data: Dict) -> str:
        """Extraer puntuación bruta principal según tipo de test"""
        
        if test_type == 'TMT-A' or test_type == 'TMT-B':
            return raw_data.get('tiempo_segundos', 'N/A')
        
        elif test_type == 'TAVEC':
            ensayos = raw_data.get('ensayos', [])
            if ensayos:
                return sum(ensayos)
            return 'N/A'
        
        elif test_type == 'Fluidez-FAS':
            return raw_data.get('total', 'N/A')
        
        elif test_type in ['Rey-Copia', 'Rey-Memoria']:
            return raw_data.get('puntuacion_bruta', 'N/A')
        
        elif test_type == 'Toulouse-Pieron':
            return raw_data.get('productividad_neta', 'N/A')
        
        elif test_type == 'Torre de Londres':
            return f"{raw_data.get('total_movement_rating', 0)} pts"
        
        return 'N/A'


# Instancia global del generador
pdf_generator = NeuroPsychReport()
