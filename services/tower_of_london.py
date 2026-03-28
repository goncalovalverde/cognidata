"""
Tower of London Test Calculator
Calculates movement ratings and performance metrics for the Tower of London test
considering both movements and execution time
"""
from typing import Dict, List, Optional


class TowerOfLondonCalculator:
    """Calculates Tower of London test metrics"""
    
    # Minimum movements required to solve each item (predefined reference)
    MINIMUM_MOVEMENTS = {
        1: 4,
        2: 4,
        3: 5,
        4: 5,
        5: 5,
        6: 6,
        7: 6,
        8: 6,
        9: 7,
        10: 7
    }
    
    def calculate(self, movement_counts: List[int], time_seconds: Optional[List[int]] = None) -> Dict:
        """
        Calculate Tower of London test metrics
        
        Args:
            movement_counts: List of 10 movement counts (one per item)
            time_seconds: Optional list of 10 time values in seconds (one per item)
            
        Returns:
            Dict with metrics and composite_raw_score for NEURONORMA
        """
        results = {
            'item_results': [],
            'total_perfect_solutions': 0,
            'total_movement_rating': 0,
            'total_time_seconds': 0,
            'execution_efficiency': 1.0,
            'composite_raw_score': 0,  # For NEURONORMA scoring
            'valid': True,
            'errors': []
        }
        
        # Validate input
        if not movement_counts or len(movement_counts) != 10:
            results['valid'] = False
            results['errors'].append('Debe proporcionar exactamente 10 elementos')
            return results
        
        # Default time_seconds if not provided
        if time_seconds is None:
            time_seconds = [0] * 10
        
        # Calculate per-item metrics
        for item_num, movement_count in enumerate(movement_counts, start=1):
            minimum = self.MINIMUM_MOVEMENTS[item_num]
            time_val = time_seconds[item_num - 1] if item_num <= len(time_seconds) else 0
            
            # Validate movement count >= minimum
            if movement_count < minimum:
                results['valid'] = False
                results['errors'].append(
                    f'Ítem {item_num}: {movement_count} movimientos es menor que '
                    f'el mínimo requerido ({minimum})'
                )
            
            # Calculate movement rating
            movement_rating = movement_count - minimum
            is_perfect = movement_rating == 0
            
            results['item_results'].append({
                'item': item_num,
                'movements_count': movement_count,
                'minimum_movements': minimum,
                'movement_rating': movement_rating,
                'perfect': is_perfect,
                'time_seconds': time_val
            })
            
            # Update totals
            if is_perfect:
                results['total_perfect_solutions'] += 1
            results['total_movement_rating'] += movement_rating
            results['total_time_seconds'] += time_val
        
        # Calculate execution efficiency based on time (0.5 to 1.0 factor)
        # Considers if times are reasonable (not too fast, not too slow)
        if results['total_time_seconds'] > 0:
            avg_time = results['total_time_seconds'] / 10
            # Ideal average time around 40-60 seconds per item
            # Deduct efficiency if too fast (<20s) or too slow (>120s)
            if avg_time < 20:
                results['execution_efficiency'] = 0.95  # Too fast - possible rushing
            elif avg_time > 120:
                results['execution_efficiency'] = 0.90  # Too slow - possible struggle
            else:
                # Scale from 0.95 to 1.0 for reasonable times
                results['execution_efficiency'] = 0.95 + (0.05 * (1 - abs(avg_time - 50) / 70))
        
        # Calculate composite raw score for NEURONORMA
        # Composite = base movement score + time penalty
        # Movement score: already calculated as total_movement_rating
        # Time factor: penalty based on deviation from optimal (300-1000s total)
        base_score = results['total_movement_rating']
        
        if results['total_time_seconds'] > 0:
            total_time = results['total_time_seconds']
            # Optimal range: 300-1000 seconds (30-100 per item)
            # Penalty increases outside this range
            if total_time < 300:  # Very fast (rushing)
                # Fast penalty: +20% extra to movement score
                time_penalty = base_score * 0.20
            elif total_time > 1000:  # Very slow (struggling)
                # Slow penalty: +40% extra to movement score
                time_penalty = base_score * 0.40
            else:  # Optimal range
                # Minimal penalty, scale from 0-5% based on deviation
                mid_point = 650  # Center of optimal range
                deviation = abs(total_time - mid_point) / mid_point
                time_penalty = base_score * min(0.05 * deviation, 0.05)
        else:
            time_penalty = 0
        
        # Composite score for NEURONORMA
        results['composite_raw_score'] = base_score + time_penalty
        
        return results


# Global calculator instance
calculator = TowerOfLondonCalculator()

