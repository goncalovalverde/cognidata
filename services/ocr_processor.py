"""
OCR Processor Service for Toulouse-Pieron Test
Analyzes uploaded test images to automatically detect and count marked cells
"""
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ToulousePieronOCR:
    """OCR processor for Toulouse-Pieron attention tests"""
    
    def __init__(self):
        self.min_mark_density = 0.12  # Lower threshold for light pencil marks
        self.grid_detection_confidence_threshold = 0.7
        self.denoise_strength = 8  # Reduced to preserve light marks
    
    def analyze_image(self, image_path: str, expected_rows: int = None, 
                      expected_cols: int = None) -> Dict:
        """
        Analyze Toulouse-Pieron test image and detect marked cells
        
        Args:
            image_path: Path to the uploaded test image
            expected_rows: Optional - expected number of rows in grid
            expected_cols: Optional - expected number of columns in grid
            
        Returns:
            Dict with analysis results:
            {
                'success': bool,
                'total_cells_detected': int,
                'marked_cells': int,
                'confidence': float,
                'processed_image_path': str (optional),
                'error': str (optional)
            }
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {'success': False, 'error': 'Could not load image'}
            
            # Preprocess image
            processed = self._preprocess_image(image)
            
            # Detect grid structure
            grid_info = self._detect_grid(processed, expected_rows, expected_cols)
            if not grid_info['success']:
                return {
                    'success': False,
                    'error': 'Could not detect grid structure',
                    'confidence': 0.0
                }
            
            # Analyze each cell for marks
            analysis = self._analyze_cells(processed, grid_info)
            
            # Save processed image with markings (for debugging/feedback)
            processed_path = image_path.replace('.png', '_analyzed.png')
            self._save_annotated_image(image, analysis, grid_info, processed_path)
            
            return {
                'success': True,
                'total_cells_detected': analysis['total_cells'],
                'marked_cells': analysis['marked_count'],
                'unmarked_cells': analysis['unmarked_count'],
                'confidence': analysis['confidence'],
                'grid_rows': grid_info.get('rows', 0),
                'grid_cols': grid_info.get('cols', 0),
                'processed_image_path': processed_path,
                'cell_details': analysis['cells']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}',
                'confidence': 0.0
            }
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for analysis
        - Convert to grayscale
        - Apply denoising
        - Adaptive thresholding
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Adaptive thresholding to handle varying lighting
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        return thresh
    
    def _detect_grid(self, processed_image: np.ndarray, expected_rows: int = None,
                     expected_cols: int = None) -> Dict:
        """
        Detect grid structure. If dimensions are provided, use them directly.
        Otherwise, estimate based on image size.
        """
        try:
            height, width = processed_image.shape
            
            if expected_rows and expected_cols:
                # Use provided dimensions
                rows = expected_rows
                cols = expected_cols
                cell_height = height // rows
                cell_width = width // cols
            else:
                # Auto-detect (less reliable)
                best_fit = None
                best_score = 0
                
                for cell_size in range(20, 70, 5):
                    rows = height // cell_size
                    cols = width // cell_size
                    
                    if 10 <= rows <= 40 and 20 <= cols <= 50:
                        row_remainder = height % cell_size
                        col_remainder = width % cell_size
                        score = 1.0 - ((row_remainder + col_remainder) / (height + width))
                        
                        if score > best_score:
                            best_score = score
                            best_fit = {
                                'cell_size': cell_size,
                                'rows': rows,
                                'cols': cols
                            }
                
                if best_fit is None:
                    return {'success': False, 'error': 'Could not estimate grid dimensions'}
                
                rows = best_fit['rows']
                cols = best_fit['cols']
                cell_height = best_fit['cell_size']
                cell_width = best_fit['cell_size']
            
            # Calculate starting offsets to center the grid
            total_grid_height = rows * cell_height
            total_grid_width = cols * cell_width
            offset_y = (height - total_grid_height) // 2
            offset_x = (width - total_grid_width) // 2
            
            # Generate cell bounding boxes
            bboxes = []
            for row in range(rows):
                for col in range(cols):
                    x = offset_x + col * cell_width
                    y = offset_y + row * cell_height
                    # Add padding to avoid grid lines
                    padding = 3
                    bboxes.append((
                        x + padding,
                        y + padding,
                        cell_width - 2*padding,
                        cell_height - 2*padding
                    ))
            
            return {
                'success': True,
                'rows': rows,
                'cols': cols,
                'cell_width': cell_width,
                'cell_height': cell_height,
                'bboxes': bboxes,
                'offset_x': offset_x,
                'offset_y': offset_y
            }
            
        except Exception as e:
            logger.error(f"Grid detection error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _cluster_positions(self, positions: list, threshold: int) -> list:
        """Cluster similar positions (within threshold distance)"""
        if not positions:
            return []
        
        clusters = []
        current_cluster = [positions[0]]
        
        for pos in positions[1:]:
            if pos - current_cluster[-1] < threshold:
                current_cluster.append(pos)
            else:
                clusters.append(int(np.mean(current_cluster)))
                current_cluster = [pos]
        
        if current_cluster:
            clusters.append(int(np.mean(current_cluster)))
        
        return clusters
    
    def _analyze_cells(self, processed_image: np.ndarray, grid_info: Dict) -> Dict:
        """
        Analyze each detected cell to determine if it's marked
        
        Returns analysis with marked vs unmarked counts
        """
        marked_cells = []
        unmarked_cells = []
        confidences = []
        
        bboxes = grid_info['bboxes']
        
        for idx, (x, y, w, h) in enumerate(bboxes):
            # Extract cell region
            cell_roi = processed_image[y:y+h, x:x+w]
            
            # Calculate mark density (ratio of white pixels in thresholded image)
            total_pixels = w * h
            if total_pixels == 0:
                continue
            
            white_pixels = np.sum(cell_roi > 0)
            density = white_pixels / total_pixels
            
            # Determine if marked
            is_marked = density > self.min_mark_density
            
            # Calculate confidence (how far from threshold)
            confidence = abs(density - self.min_mark_density) / self.min_mark_density
            confidence = min(1.0, confidence)
            
            cell_info = {
                'index': idx,
                'bbox': (x, y, w, h),
                'density': density,
                'is_marked': is_marked,
                'confidence': confidence
            }
            
            if is_marked:
                marked_cells.append(cell_info)
            else:
                unmarked_cells.append(cell_info)
            
            confidences.append(confidence)
        
        # Overall confidence is average of individual confidences
        overall_confidence = np.mean(confidences) if confidences else 0.0
        
        return {
            'total_cells': len(bboxes),
            'marked_count': len(marked_cells),
            'unmarked_count': len(unmarked_cells),
            'confidence': round(overall_confidence, 2),
            'cells': {
                'marked': marked_cells,
                'unmarked': unmarked_cells
            }
        }
    
    def _save_annotated_image(self, original_image: np.ndarray, 
                             analysis: Dict, grid_info: Dict, output_path: str):
        """
        Save annotated image showing detected marks
        Green boxes = marked, Grid overlay in light blue
        """
        annotated = original_image.copy()
        
        # Draw grid overlay
        rows = grid_info['rows']
        cols = grid_info['cols']
        cell_width = grid_info['cell_width']
        cell_height = grid_info['cell_height']
        offset_x = grid_info['offset_x']
        offset_y = grid_info['offset_y']
        
        # Draw grid lines
        for row in range(rows + 1):
            y = offset_y + row * cell_height
            cv2.line(annotated, (offset_x, y), (offset_x + cols * cell_width, y), (200, 200, 100), 1)
        for col in range(cols + 1):
            x = offset_x + col * cell_width
            cv2.line(annotated, (x, offset_y), (x, offset_y + rows * cell_height), (200, 200, 100), 1)
        
        # Draw marked cells in green
        for cell in analysis['cells']['marked']:
            x, y, w, h = cell['bbox']
            cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 3)
            # Add confidence text
            conf = int(cell['confidence'] * 100)
            cv2.putText(annotated, f"{conf}%", (x+2, y+12), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 200, 0), 1)
        
        # Add summary text
        text = f"Marked: {analysis['marked_count']} / {analysis['total_cells']} ({analysis['confidence']*100:.0f}% conf)"
        cv2.putText(annotated, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                   0.8, (0, 255, 0), 2)
        
        grid_text = f"Grid: {rows}x{cols}"
        cv2.putText(annotated, grid_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, (100, 200, 200), 2)
        
        cv2.imwrite(output_path, annotated)


# Global instance
ocr_processor = ToulousePieronOCR()
