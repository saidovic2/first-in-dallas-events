"""Auto-run import without prompt"""
import sys

# Mock input to auto-answer 'yes'
original_input = input
def mock_input(prompt):
    print(prompt + "yes")
    return "yes"

# Replace input function
__builtins__.input = mock_input

# Import and run main
from import_ticketmaster_simple import main
main()
