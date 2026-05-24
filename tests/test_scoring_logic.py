# tests/test_scoring_logic.py
import pytest
from app.scoring_logic import calculate_scores_python


def test_invalid_input_returns_empty():
    assert calculate_scores_python("not a dict") == []
    assert calculate_scores_python(None) == []
    assert calculate_scores_python(42) == []


def test_empty_dict_returns_17_zeroed_sdgs():
    result = calculate_scores_python({})
    assert isinstance(result, list)
    assert len(result) == 17
    for entry in result:
        assert entry['total_score'] == 0.0
        assert entry['direct_score'] == 0.0
        assert entry['bonus_score'] == 0.0


def test_all_17_numbers_present():
    result = calculate_scores_python({})
    numbers = [r['number'] for r in result]
    assert numbers == list(range(1, 18))


def test_result_entry_has_required_keys():
    result = calculate_scores_python({})
    assert set(result[0].keys()) == {'number', 'total_score', 'notes', 'direct_score', 'bonus_score'}


def test_sdg1_self_sufficient():
    result = calculate_scores_python({'sdg1_cost_reduction': 'self_sufficient'})
    sdg1 = next(r for r in result if r['number'] == 1)
    assert sdg1['direct_score'] == 9.0
    assert sdg1['total_score'] == 9.0


def test_sdg1_energy_producing():
    result = calculate_scores_python({'sdg1_cost_reduction': 'energy_producing'})
    sdg1 = next(r for r in result if r['number'] == 1)
    assert sdg1['direct_score'] == 10.0


def test_sdg2_food_integration():
    result = calculate_scores_python({'sdg2_food_integration': 'production'})
    sdg2 = next(r for r in result if r['number'] == 2)
    assert sdg2['direct_score'] == 10.0


def test_notes_preserved():
    result = calculate_scores_python({'sdg3_health_summary': '2', 'sdg3_notes': 'important note'})
    sdg3 = next(r for r in result if r['number'] == 3)
    assert sdg3['notes'] == 'important note'
    assert sdg3['direct_score'] == 4.0


def test_notes_default_empty_string():
    result = calculate_scores_python({})
    for entry in result:
        assert entry['notes'] == ''


def test_sdg3_bonus_with_six_actions():
    actions = ['a', 'b', 'c', 'd', 'e', 'f']
    result = calculate_scores_python({'sdg3_health_summary': '5', 'sdg3_actions': actions})
    sdg3 = next(r for r in result if r['number'] == 3)
    assert sdg3['direct_score'] == 10.0
    assert sdg3['bonus_score'] == 1.0
    assert sdg3['total_score'] == 10.0  # capped at MAX_SCORE_PER_SDG=10


def test_sdg3_no_bonus_insufficient_actions():
    result = calculate_scores_python({'sdg3_health_summary': '5', 'sdg3_actions': ['a', 'b']})
    sdg3 = next(r for r in result if r['number'] == 3)
    assert sdg3['bonus_score'] == 0.0


def test_sdg7_renewable_positive():
    result = calculate_scores_python({'sdg7_renewable_impact': 'positive'})
    sdg7 = next(r for r in result if r['number'] == 7)
    assert sdg7['direct_score'] == 10.0


def test_sdg8_two_part_score():
    result = calculate_scores_python({'sdg8_social_summary': '3', 'sdg8_technical_summary': '4'})
    sdg8 = next(r for r in result if r['number'] == 8)
    assert sdg8['direct_score'] == 7.0  # 3.0 + 4.0


def test_sdg13_two_part_score():
    result = calculate_scores_python({'sdg13_env_summary': '5', 'sdg13_carbon_reduction': 'negative'})
    sdg13 = next(r for r in result if r['number'] == 13)
    assert sdg13['direct_score'] == 10.0  # 5.0 + 5.0


def test_sdg15_two_part_score():
    result = calculate_scores_python({'sdg15_ecosystem_summary': '3', 'sdg15_artificialisation_ratio': '40'})
    sdg15 = next(r for r in result if r['number'] == 15)
    assert sdg15['direct_score'] == 6.0  # 3.0 + 3.0


def test_sdg12_six_level_scale():
    result = calculate_scores_python({'sdg12_consumption_summary': '4'})
    sdg12 = next(r for r in result if r['number'] == 12)
    assert sdg12['direct_score'] == 7.5


def test_sdg17_partnership_level4():
    result = calculate_scores_python({'sdg17_partnership_summary': '4'})
    sdg17 = next(r for r in result if r['number'] == 17)
    assert sdg17['direct_score'] == 7.5


def test_score_never_exceeds_10():
    data = {f'sdg{i}_health_summary': '5' for i in range(1, 18)}
    data['sdg3_health_summary'] = '5'
    data['sdg3_actions'] = ['a', 'b', 'c', 'd', 'e', 'f']
    result = calculate_scores_python(data)
    for entry in result:
        assert entry['total_score'] <= 10.0


def test_score_never_negative():
    result = calculate_scores_python({})
    for entry in result:
        assert entry['total_score'] >= 0.0


def test_unknown_fields_ignored():
    result = calculate_scores_python({'not_an_sdg': 'garbage', 'sdg0_direct': 99, 'sdg99_foo': 'bar'})
    assert len(result) == 17
    for entry in result:
        assert entry['total_score'] == 0.0


def test_sdg6_exceptional_value():
    result = calculate_scores_python({'sdg6_water_summary': 'exceptional'})
    sdg6 = next(r for r in result if r['number'] == 6)
    assert sdg6['direct_score'] == 10.0


def test_sdg11_measures_five():
    result = calculate_scores_python({'sdg11_measures': 'five'})
    sdg11 = next(r for r in result if r['number'] == 11)
    assert sdg11['direct_score'] == 10.0
