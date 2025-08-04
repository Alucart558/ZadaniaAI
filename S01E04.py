import requests
import json
from openai import OpenAI

# Initialize OpenAI client for testing prompts
client = OpenAI(api_key="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")

def test_robot_prompt(prompt_text):
    """Test the robot navigation prompt locally using OpenAI."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt_text}
            ],
            temperature=0,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content.strip()
        print("Generated response:")
        print(result)
        
        # Try to parse as JSON
        try:
            json_result = json.loads(result)
            if "steps" in json_result:
                print(f"\nExtracted steps: {json_result['steps']}")
                return json_result
            else:
                print("\nWarning: No 'steps' field found in JSON")
        except json.JSONDecodeError:
            print("\nWarning: Response is not valid JSON")
            
        return result
        
    except Exception as e:
        print(f"Error testing prompt: {e}")
        return None

def create_robot_navigation_prompt():
    """Create a prompt for robot navigation that avoids forbidden words."""
    
    # Wersja 1: Opisowa instrukcja
    prompt_v1 = """You are a navigation system for an industrial robot in a warehouse facility. The robot must reach a data computer.

Robot capabilities:
- Moves on a grid system
- Commands available: LEFT, RIGHT, UP, DOWN
- Each command moves one grid position

Mission briefing:
The robot starts at the entry point of the warehouse. The target data computer is positioned in the facility requiring a specific navigation sequence. Based on standard warehouse layouts, the optimal path typically involves:

1. Initial vertical movement to clear ground-level obstacles
2. Horizontal navigation toward the target zone  
3. Additional vertical movement to reach the computer level
4. Final positioning adjustments

Calculate the precise movement sequence and provide response as JSON format:

{
  "analysis": "Brief reasoning about the path",
  "steps": "sequence of commands separated by commas"
}

Generate the navigation commands needed to successfully reach the target."""

    # Wersja 2: Zakodowana trasa (sprytniejsza)
    prompt_v2 = """Industrial robot navigation system activated.

Warehouse grid coordinates:
- Starting position: Ground level entry
- Target: Data terminal location
- Grid movement: Single step per command
- Available actions: LEFT, RIGHT, UP, DOWN

Navigation algorithm required:
Transform the following path description into movement commands:
"Begin with two steps toward ceiling, then three steps toward the right wall, continue two steps ceiling-ward, then one step toward left wall, and two final steps toward ceiling"

Output as JSON with this structure:
{
  "reasoning": "Path conversion logic",
  "steps": "comma-separated movement commands"
}

Convert the path description into the required command sequence."""

    # Wersja 3: Najbardziej zawoalowana
    prompt_v3 = """Factory automation system - robot pathfinding module.

Environment parameters:
- Grid-based movement system
- Destination: Computer terminal for data access
- Movement vocabulary: LEFT, RIGHT, UP, DOWN
- Single unit displacement per command

Task specification:
The robot must navigate from its initial coordinates to reach the target terminal. Consider a standard industrial facility layout where the optimal route follows this pattern:

Starting from ground position, move in the positive Y direction (2 units), then positive X direction (3 units), again positive Y direction (2 units), negative X direction (1 unit), and finally positive Y direction (2 units).

Translate this coordinate-based description into the appropriate command sequence.

Response format:
{
  "calculation": "Coordinate to command translation",
  "steps": "final command sequence with comma separation"
}"""

    return prompt_v1, prompt_v2, prompt_v3

def main():
    """Main function to test different prompts."""
    print("=== Robot Navigation Prompt Tester ===\n")
    
    # Get different prompt versions
    prompt_v1, prompt_v2, prompt_v3 = create_robot_navigation_prompt()
    
    prompts = [
        ("Descriptive Version", prompt_v1),
        ("Encoded Path Version", prompt_v2), 
        ("Coordinate Version", prompt_v3)
    ]
    
    for name, prompt in prompts:
        print(f"\n{'='*50}")
        print(f"Testing: {name}")
        print(f"{'='*50}")
        print(f"Prompt:\n{prompt}\n")
        print("-" * 30)
        
        result = test_robot_prompt(prompt)
        
        print(f"\n{'-'*30}")
        input("Press Enter to continue to next prompt...")

def send_to_robot_panel(steps_sequence):
    """
    This function shows how you might send the steps to the robot panel
    (though the actual task requires manual input on the website)
    """
    # Note: This is conceptual - the actual task requires manual web interaction
    robot_url = "https://banan.ag3nts.org/"
    
    # The steps would need to be submitted through the web interface
    print(f"Steps to submit manually: {steps_sequence}")
    print(f"Go to: {robot_url}")
    print("Enter the generated steps in the robot control panel")

if __name__ == "__main__":
    main()
    
    # Quick test of a specific prompt
    print("\n" + "="*60)
    print("QUICK TEST - Best prompt:")
    print("="*60)
    
    quick_prompt = """Navigation system for warehouse robot.

Robot specifications:
- Grid movement system
- Commands: LEFT, RIGHT, UP, DOWN  
- Target: Data computer terminal

Path calculation needed:
Starting from entry position, determine movement sequence to reach the data terminal. Standard warehouse configuration suggests this routing pattern:

Move upward 2 positions to clear floor obstacles, then rightward 3 positions toward target column, then upward 2 positions to computer level, then leftward 1 position for alignment, then upward 2 positions to final destination.

Provide JSON response:
{
  "pathfinding": "Movement sequence reasoning",
  "steps": "comma-separated commands"
}"""
    
    test_robot_prompt(quick_prompt)