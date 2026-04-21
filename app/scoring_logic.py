# /app/scoring_logic.py

import math # Might be needed if more complex math arises later

# Define constants
TOTAL_SDGS = 17
MAX_SCORE_PER_SDG = 10

# Optional: Define SDG_INFO here if needed for names/colors within this function,
# otherwise, the route saving the SdgScore can handle joining with SdgGoal for that info.
# SDG_INFO = {
#     1:  { name: 'No Poverty',                 color: '#E5243B'},
#     # ... Add others if needed ...
# }

def calculate_scores_python(assessment_data):
    """
    Calculates SDG scores based on raw expert assessment input data.

    Args:
        assessment_data (dict): Parsed JSON data from the assessment form.
                                Example: {'sdg-1': {'inputs': {...}, 'notes': ''}, ...}

    Returns:
        list: A list of dictionaries, each representing an SDG score.
              Example: [{'number': 1, 'total_score': 9.0, 'notes': '...',
                         'direct_score': 9.0, 'bonus_score': 0.0}, ...]
              Returns an empty list if input is invalid.
    """
    if not isinstance(assessment_data, dict):
        # Or raise an error, depending on how you want to handle bad input
        print("Error: Invalid assessment_data input to calculate_scores_python")
        return []

    print(f"DEBUG: calculate_scores_python called with data keys: {list(assessment_data.keys())}")
    scores = []

    for i in range(1, TOTAL_SDGS + 1):
        # Handle flat form data structure instead of nested sdg-{i} structure
        # Form sends data like: sdg1_cost_reduction, sdg1_notes, etc.
        notes = assessment_data.get(f'sdg{i}_notes', '')
        
        # Inputs are directly in the assessment_data with sdg{i}_ prefix
        inputs = assessment_data  # Use the whole dict as inputs for backward compatibility

        direct_score = 0.0 # Use float for scores
        bonus_score = 0.0

        # --- Scoring Logic (Translated from JS - Finalized Version) ---
        try: # Add try-except for robustness within the loop
            if i == 1:
                # Scale: 0, 3, 5, 7, 9, 10
                value = inputs.get('sdg1_cost_reduction')
                if value == 'cost_reduc_2': direct_score = 3.0
                elif value == 'cost_reduc_3': direct_score = 5.0
                elif value == 'cost_reduc_4': direct_score = 7.0
                elif value == 'self_sufficient': direct_score = 9.0
                elif value == 'energy_producing': direct_score = 10.0

            elif i == 2:
                # Scale: 0, 2, 4, 6, 8, 10
                value = inputs.get('sdg2_food_integration')
                if value == 'study': direct_score = 2.0
                elif value == 'conversion': direct_score = 4.0
                elif value == 'community': direct_score = 6.0
                elif value == 'private': direct_score = 8.0
                elif value == 'production': direct_score = 10.0

            elif i == 3:
                # Scale: 0, 2, 4, 6, 8, 10 + Bonus
                # Input name from HTML: sdg3_health_summary (Value 0-5 or other)
                value = inputs.get('sdg3_health_summary')
                if value == '1': direct_score = 2.0
                elif value == '2': direct_score = 4.0
                elif value == '3': direct_score = 6.0
                elif value == '4': direct_score = 8.0
                elif value == '5': direct_score = 10.0
                # Bonus logic
                actions_checked = inputs.get('sdg3_actions', [])
                if value == '5' and isinstance(actions_checked, list) and len(actions_checked) >= 6:
                    bonus_score = 1.0

            elif i == 4:
                # Scale: 0, 2, 3, 5, 7, 10
                # Input name from HTML: sdg4_accessibility_summary (Value 0, study, 1-4, other)
                value = inputs.get('sdg4_accessibility_summary')
                if value == 'study': direct_score = 2.0
                elif value == '1': direct_score = 3.0
                elif value == '2': direct_score = 5.0
                elif value == '3': direct_score = 7.0
                elif value == '4': direct_score = 10.0

            elif i == 5:
                # Scale: 0, 2, 4, 6, 8, 10 + Bonus
                # Input name from HTML: sdg5_equality_summary (Value 0-5 or other)
                value = inputs.get('sdg5_equality_summary')
                if value == '1': direct_score = 2.0
                elif value == '2': direct_score = 4.0
                elif value == '3': direct_score = 6.0
                elif value == '4': direct_score = 8.0
                elif value == '5': direct_score = 10.0
                # Bonus logic
                actions_checked = inputs.get('sdg5_actions', [])
                if value == '5' and isinstance(actions_checked, list) and len(actions_checked) >= 5:
                    bonus_score = 1.0

            elif i == 6:
                # Scale: 0, 1.5, 3, 5, 7, 8.5, 10 (Keep existing)
                # Input name from HTML: sdg6_water_summary (Value 0-5, exceptional, other)
                value = inputs.get('sdg6_water_summary')
                if value == '1': direct_score = 1.5
                elif value == '2': direct_score = 3.0
                elif value == '3': direct_score = 5.0
                elif value == '4': direct_score = 7.0
                elif value == '5': direct_score = 8.5
                elif value == 'exceptional': direct_score = 10.0

            elif i == 7:
                # Scale: 0, 2, 4, 6, 8, 10 (Keep existing)
                # Input name from HTML: sdg7_renewable_impact (Value none, reduc_25/50/75, neutral, positive, other)
                value = inputs.get('sdg7_renewable_impact')
                if value == 'reduc_25': direct_score = 2.0
                elif value == 'reduc_50': direct_score = 4.0
                elif value == 'reduc_75': direct_score = 6.0
                elif value == 'neutral': direct_score = 8.0
                elif value == 'positive': direct_score = 10.0

            elif i == 8:
                # Two Parts, each 0-5 points. Scale: 0, 1, 2, 3, 4, 5 for each part.
                score_social = 0.0
                social_value = inputs.get('sdg8_social_summary') # Input name (Value 0-5, other)
                if social_value == '1': score_social = 1.0
                elif social_value == '2': score_social = 2.0
                elif social_value == '3': score_social = 3.0
                elif social_value == '4': score_social = 4.0
                elif social_value == '5': score_social = 5.0

                score_technical = 0.0
                technical_value = inputs.get('sdg8_technical_summary') # Input name (Value 0-5, other)
                if technical_value == '1': score_technical = 1.0
                elif technical_value == '2': score_technical = 2.0
                elif technical_value == '3': score_technical = 3.0
                elif technical_value == '4': score_technical = 4.0
                elif technical_value == '5': score_technical = 5.0

                direct_score = score_social + score_technical

            elif i == 9:
                # Scale: 0, 2, 4, 6, 8, 10
                # Input name from HTML: sdg9_innovation_summary (Value 0-5, other)
                value = inputs.get('sdg9_innovation_summary')
                if value == '1': direct_score = 2.0
                elif value == '2': direct_score = 4.0
                elif value == '3': direct_score = 6.0
                elif value == '4': direct_score = 8.0
                elif value == '5': direct_score = 10.0

            elif i == 10:
                # Scale: 0, 2, 4, 6, 8, 10
                # Input name from HTML: sdg10_inclusion_summary (Value 0-5, other)
                value = inputs.get('sdg10_inclusion_summary')
                if value == '1': direct_score = 2.0
                elif value == '2': direct_score = 4.0
                elif value == '3': direct_score = 6.0
                elif value == '4': direct_score = 8.0
                elif value == '5': direct_score = 10.0

            elif i == 11:
                 # Scale: 0, 2, 4, 6, 8, 10
                 # Input name from HTML: sdg11_measures (Value none, one, two, three, four, five, other)
                 value = inputs.get('sdg11_measures')
                 if value == 'one': direct_score = 2.0
                 elif value == 'two': direct_score = 4.0
                 elif value == 'three': direct_score = 6.0
                 elif value == 'four': direct_score = 8.0
                 elif value == 'five': direct_score = 10.0

            elif i == 12:
                 # Scale: 0, 2, 4, 6, 7.5, 9, 10
                 # Input name from HTML: sdg12_consumption_summary (Value 0-6, other)
                 value = inputs.get('sdg12_consumption_summary')
                 if value == '1': direct_score = 2.0
                 elif value == '2': direct_score = 4.0
                 elif value == '3': direct_score = 6.0
                 elif value == '4': direct_score = 7.5
                 elif value == '5': direct_score = 9.0
                 elif value == '6': direct_score = 10.0

            elif i == 13:
                 # Two Parts, each 0-5 points. Scale: 0, 1, 2, 3, 4, 5 for each part.
                 score_env = 0.0
                 env_value = inputs.get('sdg13_env_summary') # Input name (Value 0-5, other)
                 if env_value == '1': score_env = 1.0
                 elif env_value == '2': score_env = 2.0
                 elif env_value == '3': score_env = 3.0
                 elif env_value == '4': score_env = 4.0
                 elif env_value == '5': score_env = 5.0

                 score_carbon = 0.0
                 carbon_value = inputs.get('sdg13_carbon_reduction') # Input name (Value 0, 2, 3, 4, 5, negative, other)
                 if carbon_value == '2': score_carbon = 1.0
                 elif carbon_value == '3': score_carbon = 2.0
                 elif carbon_value == '4': score_carbon = 3.0
                 elif carbon_value == '5': score_carbon = 4.0
                 elif carbon_value == 'negative': score_carbon = 5.0

                 direct_score = score_env + score_carbon

            elif i == 14:
                # Scale: 0, 2, 4, 6, 8, 10
                # Input name from HTML: sdg14_pollution_summary (Value 0-5, other)
                value = inputs.get('sdg14_pollution_summary')
                if value == '1': direct_score = 2.0
                elif value == '2': direct_score = 4.0
                elif value == '3': direct_score = 6.0
                elif value == '4': direct_score = 8.0
                elif value == '5': direct_score = 10.0

            elif i == 15:
                 # Two Parts, each 0-5 points. Scale: 0, 1, 2, 3, 4, 5 for each part.
                 score_ecosystem = 0.0
                 eco_value = inputs.get('sdg15_ecosystem_summary') # Input name (Value 0-5, other)
                 if eco_value == '1': score_ecosystem = 1.0
                 elif eco_value == '2': score_ecosystem = 2.0
                 elif eco_value == '3': score_ecosystem = 3.0
                 elif eco_value == '4': score_ecosystem = 4.0
                 elif eco_value == '5': score_ecosystem = 5.0

                 score_artificialisation = 0.0
                 artif_value = inputs.get('sdg15_artificialisation_ratio') # Input name (Value 100, 80, 60, 40, 20, 0, other)
                 if artif_value == '80': score_artificialisation = 1.0
                 elif artif_value == '60': score_artificialisation = 2.0
                 elif artif_value == '40': score_artificialisation = 3.0
                 elif artif_value == '20': score_artificialisation = 4.0
                 elif artif_value == '0': score_artificialisation = 5.0

                 direct_score = score_ecosystem + score_artificialisation

            elif i == 16:
                # Scale: 0, 2, 4, 6, 8, 10
                # Input name from HTML: sdg16_peace_summary (Value 0-5, other)
                value = inputs.get('sdg16_peace_summary')
                if value == '1': direct_score = 2.0
                elif value == '2': direct_score = 4.0
                elif value == '3': direct_score = 6.0
                elif value == '4': direct_score = 8.0
                elif value == '5': direct_score = 10.0

            elif i == 17:
                 # Scale: 0, 2, 4, 6, 7.5, 9, 10
                 # Input name from HTML: sdg17_partnership_summary (Value 0-6, other)
                 value = inputs.get('sdg17_partnership_summary')
                 if value == '1': direct_score = 2.0
                 elif value == '2': direct_score = 4.0
                 elif value == '3': direct_score = 6.0
                 elif value == '4': direct_score = 7.5
                 elif value == '5': direct_score = 9.0
                 elif value == '6': direct_score = 10.0

            # --- Add logic for any SDGs beyond 17 if they exist ---

        except Exception as e:
             print(f"Error processing scoring logic for SDG {i}: {e}")
             # Keep scores at 0 if specific SDG logic fails
             direct_score = 0.0
             bonus_score = 0.0

        # --- Normalize/Cap Score ---
        # Apply bonus and cap at MAX_SCORE_PER_SDG
        total_score = direct_score + bonus_score
        # Ensure score doesn't exceed max (e.g., if direct is 10 and bonus is 1)
        total_score = min(total_score, MAX_SCORE_PER_SDG)
        # Ensure score is not negative
        total_score = max(total_score, 0.0)

        # --- Append Result ---
        score_entry = {
            'number': i,
            'total_score': round(total_score, 1), # Use the final capped score
            'notes': notes or '', # Ensure notes is a string
            # Include direct/bonus for potential storage or analysis
            'direct_score': round(direct_score, 1),
            'bonus_score': round(bonus_score, 1)
        }
        scores.append(score_entry)
        
        if total_score > 0:  # Only log if there's actually a score
            print(f"DEBUG: SDG {i} scored {total_score} (direct: {direct_score}, bonus: {bonus_score})")

    print(f"DEBUG: calculate_scores_python returning {len(scores)} scores with non-zero: {len([s for s in scores if s['total_score'] > 0])}")
    return scores

# Example Usage (for testing):
# if __name__ == '__main__':
#     test_data = {
#         'sdg-1': {'inputs': {'sdg1_cost_reduction': 'self_sufficient'}, 'notes': 'Good insulation'},
#         'sdg-3': {'inputs': {'sdg3_health_summary': '5', 'sdg3_actions': ['materials', 'air_quality', 'water_quality', 'lighting_quality', 'acoustic_comfort', 'soil_cleaning']}, 'notes': 'All done'},
#         'sdg-8': {'inputs': {'sdg8_social_summary': '3', 'sdg8_technical_summary': '4'}, 'notes': ''},
#         'sdg-13': {'inputs': {'sdg13_env_summary': '4', 'sdg13_carbon_reduction': 'negative'}, 'notes': 'Great work'},
#         # Add other SDGs as needed for testing
#     }
#     calculated = calculate_scores_python(test_data)
#     import json
#     print(json.dumps(calculated, indent=2))