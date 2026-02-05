import numpy as np
from backend.app.services.irt_engine import IRTEngine

def test_2pl_probability_calculation():
    """Test that probability math is correct (S-shape curve)"""
    engine = IRTEngine()
    
    # User ability 0, Item difficulty 0, Discrim 1 -> Prob should be 0.5
    theta = np.array([0.0, 0.0])
    a_values = [1.0, 0.0] # Math discrimination only
    b_value = 0.0
    
    prob = engine.mirt_2pl_probability(theta, a_values, b_value)
    assert 0.49 <= prob <= 0.51  # Float tolerance

def test_answer_checking_logic():
    """Test the answer checker"""
    engine = IRTEngine()
    options = ["Apple", "Banana", "Cherry", "Date"]
    
    # 1. Exact letter match (Standard case)
    assert engine.check_answer("B", "B", options) == True
    
    # 2. Case insensitive letter match
    assert engine.check_answer("b", "B", options) == True
    
    # 3. Wrong answer
    assert engine.check_answer("A", "B", options) == False
    
    # 4. NOTE: Your engine currently DOES NOT support full text input for user answers.
    # It requires the frontend to send "A", "B", etc.
    # If we send "Banana", it currently returns False. 
    # This assertion verifies that behavior is consistent.
    assert engine.check_answer("Banana", "B", options) == False

def test_theta_update_math():
    """Test that getting questions right increases Theta"""
    engine = IRTEngine()
    
    # Scenario: Student gets 3 hard math questions correct
    responses = [1, 1, 1]
    items = [
        {'a_values': [1.5, 0], 'b_value': 1.0}, # Hard Math
        {'a_values': [1.5, 0], 'b_value': 1.0},
        {'a_values': [1.5, 0], 'b_value': 1.0},
    ]
    
    theta, se = engine.update_theta_eap(responses, items)
    
    # Math ability (index 0) should be positive
    assert theta[0] > 0.0
    # Tech ability (index 1) should stay near 0 (since a_values[1] was 0)
    assert -0.5 < theta[1] < 0.5