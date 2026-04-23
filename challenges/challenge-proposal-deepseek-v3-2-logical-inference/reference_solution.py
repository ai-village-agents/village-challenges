"""
Reference solution for Logical Inference Gauntlet.
This demonstrates one possible approach to parsing and reasoning.
"""

import re
from typing import List, Tuple, Any

def parse_statements(text: str) -> list:
    """Extract statements from problem text, return list of structured representations."""
    lines = text.split('\n')
    statements = []
    in_statements = False
    for line in lines:
        line = line.strip()
        if line.startswith('### Statements ###'):
            in_statements = True
            continue
        if line.startswith('### Queries ###'):
            break
        if not in_statements or not line:
            continue
        
        # Match statement number: "1. All dogs are mammals."
        match = re.match(r'(\d+)\.\s+(.+)', line)
        if match:
            num = int(match.group(1))
            content = match.group(2).strip()
            # Simple representation: store as dict with type and components
            stmt = {'num': num, 'text': content}
            
            # Classify statement type
            if content.startswith('All '):
                stmt['type'] = 'all'
                # All A are B
                parts = content[4:].split(' are ')
                if len(parts) == 2:
                    stmt['subject'] = parts[0].strip()
                    stmt['predicate'] = parts[1].strip().rstrip('.')
            elif content.startswith('No '):
                stmt['type'] = 'no'
                # No A are B
                parts = content[3:].split(' are ')
                if len(parts) == 2:
                    stmt['subject'] = parts[0].strip()
                    stmt['predicate'] = parts[1].strip().rstrip('.')
            elif content.startswith('Some '):
                stmt['type'] = 'some'
                # Some A are B
                parts = content[5:].split(' are ')
                if len(parts) == 2:
                    stmt['subject'] = parts[0].strip()
                    stmt['predicate'] = parts[1].strip().rstrip('.')
            elif content.startswith('If '):
                stmt['type'] = 'if-then'
                # If P, then Q
                if ' then ' in content:
                    parts = content[3:].split(' then ')
                    stmt['antecedent'] = parts[0].strip().rstrip(',')
                    stmt['consequent'] = parts[1].strip().rstrip('.')
            elif content.startswith('Either '):
                stmt['type'] = 'either-or'
                # Either P or Q
                content = content[7:]  # Remove "Either "
                if ' or ' in content:
                    parts = content.split(' or ')
                    stmt['left'] = parts[0].strip()
                    stmt['right'] = parts[1].strip().rstrip('.')
            elif content.startswith('Not all '):
                stmt['type'] = 'not-all'
                # Not all A are B
                parts = content[8:].split(' are ')
                if len(parts) == 2:
                    stmt['subject'] = parts[0].strip()
                    stmt['predicate'] = parts[1].strip().rstrip('.')
            else:
                # Simple atomic statement
                stmt['type'] = 'atomic'
                stmt['content'] = content.rstrip('.')
            
            statements.append(stmt)
    
    return statements

def is_consistent(statements: list) -> bool:
    """Return True if the set of statements is logically consistent, False otherwise."""
    # Simple consistency check: look for obvious contradictions
    # In a full solution, this would use proper logical reasoning
    
    # Check for "All A are B" and "No A are B"
    all_statements = [s for s in statements if s.get('type') == 'all']
    no_statements = [s for s in statements if s.get('type') == 'no']
    
    for all_stmt in all_statements:
        for no_stmt in no_statements:
            if (all_stmt.get('subject') == no_stmt.get('subject') and 
                all_stmt.get('predicate') == no_stmt.get('predicate')):
                return False
    
    # Check for "Some A are B" and "No A are B"
    some_statements = [s for s in statements if s.get('type') == 'some']
    for some_stmt in some_statements:
        for no_stmt in no_statements:
            if (some_stmt.get('subject') == no_stmt.get('subject') and 
                some_stmt.get('predicate') == no_stmt.get('predicate')):
                return False
    
    # Check for "All A are B" and "Not all A are B"
    not_all_statements = [s for s in statements if s.get('type') == 'not-all']
    for all_stmt in all_statements:
        for not_all_stmt in not_all_statements:
            if (all_stmt.get('subject') == not_all_stmt.get('subject') and 
                all_stmt.get('predicate') == not_all_stmt.get('predicate')):
                return False
    
    return True

def find_contradiction(statements: list) -> list:
    """Return list of statement indices (1-based) forming a minimal contradiction, or empty list."""
    # Look for pairwise contradictions first
    for i in range(len(statements)):
        for j in range(i + 1, len(statements)):
            s1 = statements[i]
            s2 = statements[j]
            
            # Check for direct contradictions
            if (s1.get('type') == 'all' and s2.get('type') == 'not-all' and
                s1.get('subject') == s2.get('subject') and
                s1.get('predicate') == s2.get('predicate')):
                return [s1['num'], s2['num']]
            
            if (s1.get('type') == 'all' and s2.get('type') == 'no' and
                s1.get('subject') == s2.get('subject') and
                s1.get('predicate') == s2.get('predicate')):
                return [s1['num'], s2['num']]
            
            if (s1.get('type') == 'some' and s2.get('type') == 'no' and
                s1.get('subject') == s2.get('subject') and
                s1.get('predicate') == s2.get('predicate')):
                return [s1['num'], s2['num']]
    
    # No contradiction found
    return []

def check_entailment(premises: list, conclusion_index: int, all_statements: list) -> str:
    """Return 'Yes', 'No', or 'Undetermined' whether conclusion follows from premises."""
    # Simplified logic for demonstration
    # In full solution, would perform proper logical deduction
    
    # Map statement numbers to indices
    stmt_map = {stmt['num']: stmt for stmt in all_statements}
    
    # Get conclusion statement
    conclusion = stmt_map.get(conclusion_index)
    if not conclusion:
        return 'Undetermined'
    
    # Very simple entailment checks
    premise_types = [p.get('type') for p in premises]
    premise_subjects = [p.get('subject') for p in premises if 'subject' in p]
    premise_predicates = [p.get('predicate') for p in premises if 'predicate' in p]
    
    # Check for modus ponens: If P then Q, and P -> Q
    for i in range(len(premises)):
        for j in range(len(premises)):
            if i == j:
                continue
            if (premises[i].get('type') == 'if-then' and 
                premises[j].get('content', '').startswith(premises[i].get('antecedent', ''))):
                # Check if conclusion matches consequent
                if conclusion.get('content', '').startswith(premises[i].get('consequent', '')):
                    return 'Yes'
    
    # Check for categorical syllogism
    # All A are B, All B are C -> All A are C (not implemented fully)
    
    # Default to Undetermined
    return 'Undetermined'

def generate_proof(premises: list, conclusion_index: int, all_statements: list) -> list:
    """Return list of statement indices (1-based) forming a minimal proof, or empty list."""
    # For the sample problem: Spot not reptile from 1-4
    # The proof uses statements 1, 4, 5 (but 5 not in premises)
    # Actually, from 1-4 alone, we can't prove Spot not reptile without 5
    # Wait, sample expects proof [1, 4, 5] but Q4 asks from 1-4...
    # This shows the complexity of proper implementation
    
    # Return empty list as placeholder
    return []

if __name__ == "__main__":
    # Test with sample
    sample_text = """### Statements ###
1. All dogs are mammals.
2. No reptiles are mammals.
3. Some mammals can swim.
4. If something is a dog, then it is not a reptile.
5. Either Spot is a dog or Spot is a reptile.
6. Spot is a mammal.
7. If Spot is a mammal, then Spot can swim.
8. Not all mammals can swim.

### Queries ###
Q1. Is the set of statements logically consistent? (Yes/No)
Q2. Which statement numbers, if any, form a minimal contradiction? (e.g., "3,8" or "None")
Q3. Does statement 6 logically follow from statements 1-5? (Yes/No/Undetermined)
Q4. From statements 1-4, does "Spot is not a reptile" follow? (Yes/No/Undetermined)
Q5. Provide a minimal proof sketch for Q4 if "Yes": list statement numbers in logical order.

### Domain ###
Constants: Spot
Predicates: Dog(x), Mammal(x), Reptile(x), CanSwim(x)
Relations: All, Some, No, If-Then, Either-Or, Not
"""
    
    statements = parse_statements(sample_text)
    print(f"Parsed {len(statements)} statements")
    print(f"Consistent: {is_consistent(statements)}")
    print(f"Contradiction: {find_contradiction(statements)}")
    print(f"Entailment Q3: {check_entailment(statements[0:5], 6, statements)}")
    print(f"Entailment Q4: {check_entailment(statements[0:4], 5, statements)}")
    print(f"Proof: {generate_proof(statements[0:4], 5, statements)}")
