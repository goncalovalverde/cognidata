"""
Tower of London Test Calculator
Calculates movement ratings and performance metrics for the Tower of London test
"""
from typing import Dict, List


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
    
    def calculate(self, movement_counts: List[int]) -> Dict:
        """
        Calculate Tower of London test metrics
        
        Args:
            movement_counts: List of 10 movement counts (one per item)
            
        Returns:
            Dict with:
            {
                'item_results': [
                    {
                        'item': 1,
                        'movements_count': 5,
                        'minimum_movements': 4,
                        'movement_rating': 1,
                        'perfect': False
                    },
                    ...
                ],
                'total_perfect_solutions': 0,  # Count of perfect solutions (rating = 0)
                'total_movement_rating': 12,   # Sum of all movement ratings
                'valid': True,
                'errors': []
            }
        """
        results = {
            'item_results': [],
            'total_perfect_solutions': 0,
            'total_movement_rating': 0,
            'valid': True,
            'errors': []
        }
        
        # Validate input
        if not movement_counts or len(movement_counts) != 10:
            results['valid'] = False
            results['errors'].append('Debe proporcionar exactamente 10 elementos')
            return results
        
        # Calculate per-item metrics
        for item_num, movement_count in enumerate(movement_counts, start=1):
            minimum = self.MINIMUM_MOVEMENTS[item_num]
            
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
                'perfect': is_perfect
            })
            
            # Update totals
            if is_perfect:
                results['total_perfect_solutions'] += 1
            results['total_movement_rating'] += movement_rating
        
        return results


# Global calculator instance
calculator = TowerOfLondonCalculator()
