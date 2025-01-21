import json

def determine_difficulty(number):
    """
    Determines difficulty based on problem number using the rating table:
    1,2,7,8,9 = easy
    3,4,10,11,12 = medium
    5,6,13,14 = hard
    """
    if number in [1, 2, 7, 8, 9]:
        return 'easy'
    elif number in [3, 4, 10, 11, 12]:
        return 'medium'
    elif number in [5, 6, 13, 14]:
        return 'hard'
    return 'unknown'

def determine_sectioned_difficulty(number):
    """
    Determines difficulty for A/B sectioned problems:
    1,2 = easy
    3,4 = medium
    5,6 = hard
    """
    if number in [1, 2]:
        return 'easy'
    elif number in [3, 4]:
        return 'medium'
    elif number in [5, 6]:
        return 'hard'
    return 'unknown'

def classify_problems_from_json(json_file_path):
    counts = {
        'easy': 0,
        'medium': 0,
        'hard': 0,
        'unknown': 0
    }
    
    unknown_cases = []  # To store problematic IDs
    
    try:
        with open(json_file_path, 'r') as file:
            problems = json.load(file)
            
        for problem in problems:
            problem_id = problem.get('id')
            if not problem_id:
                continue
                
            try:
                year, second_part = problem_id.split('_')
                
                # Check if it's a sectioned problem (A/B format)
                if second_part.startswith('A') or second_part.startswith('B'):
                    number = int(second_part[1:])  # Extract number after A or B
                    difficulty = determine_sectioned_difficulty(number)
                else:
                    # Regular numbered problem
                    number = int(second_part)
                    difficulty = determine_difficulty(number)
                
                counts[difficulty] += 1
                
                # Store unknown cases with their details
                if difficulty == 'unknown':
                    unknown_cases.append({
                        'id': problem_id,
                        'second_part': second_part,
                        'type': problem.get('type', 'N/A'),
                        'answer_type': problem.get('answer_type', 'N/A')
                    })
                
            except (ValueError, IndexError):
                counts['unknown'] += 1
                unknown_cases.append({
                    'id': problem_id,
                    'error': 'parsing_error'
                })
                continue
                
    except FileNotFoundError:
        print(f"Error: Could not find file {json_file_path}")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in file")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("\nProblem Difficulty Distribution:")
    print(f"Easy problems: {counts['easy']}")
    print(f"Medium problems: {counts['medium']}")
    print(f"Hard problems: {counts['hard']}")
    total = sum(counts.values())
    print(f"Total problems: {total}")
    
    if unknown_cases:
        print("\nUnknown/Problematic Cases:")
        print("-" * 50)
        for case in unknown_cases:
            print(f"ID: {case['id']}")
            if 'error' in case:
                print(f"Error: {case['error']}")
            else:
                print(f"Second part: {case['second_part']}")
                print(f"Type: {case['type']}")
                print(f"Answer type: {case['answer_type']}")
            print("-" * 50)
    
    return counts, unknown_cases

if __name__ == "__main__":
    json_file_path = 'data/Putnam_AXIOM_Original_v3.json'
    classify_problems_from_json(json_file_path)