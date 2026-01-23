import sys
import os

# Add the do_methods_here! folder to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'do_methods_here!'))

# Import from Claudia.py
from Claudia import BasicQueryEngine
from impl import CategoryQueryHandler, JournalQueryHandler

que = BasicQueryEngine()
que.getEntityById("Artificial Intelligence")
que.addJournalHandler(jou_qh)


result_q3 = que.getEntityById("Artificial Intelligence")
result_q4 = que.getEntityById("2532-8816")
result_q5 = que.getEntityById("NonExistentID")  # Testing with a non-existent ID
result_q6 = que.getEntityById("1234-5678")  # Testing with an ID that could belong to multiple entities
result_q7 = que.getEntityById("Medicine")  # Testing with a category ID