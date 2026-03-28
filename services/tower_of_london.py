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
            Dict with:
            {
                'item_results': [
                    {
                        'item': 1,
                        'movements_count': 5,
                        'minimum_movements': 4,
                        'movement_rating': 1,
                        'perfect': False,
                        'time_seconds': 45
                    },
                    ...
                ],
                'total_perfect_solutions': 0,
                'total_movement_rating': 12,
                'total_time_seconds': 450,
                'execution_efficiency': 0.95,  # Based on time quality
                'valid': True,
                'errors': []
            }
        """
        results = {
            'item_results': [],
            'total_perfect_solutions': 0,
            'total_movement_rating': 0,
            'total_time_seconds': 0,
            'execution_efficiency': 1.0,
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
        
        return results


# Global calculator instance
calculator = TowerOfLondonCalculator()

