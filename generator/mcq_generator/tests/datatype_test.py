import asyncio 
import os 

from generator.mcq_generator.core.ai_engine  import MCQEngine 
from dotenv import load_dotenv
async def test_mcq_engine(): 
    load_dotenv()
    print("Initializing MCQ Engine")
    
    engine = MCQEngine() 
    
    print("Sending requests to Gemini..")
    
    result = await engine.generate_mcq( 
                                        domain = "Computer Science",
                                        concept_tag = "Data Structure", 
                                        question_text = "Explain the difference between a stack and a queue in terms of how elements are removed"
                                        )
    
    
    print("\n Success ! ouptut generated ")
    
    
    print(f"Data Type : {type(result)}")
    print(f"is a pydantic model {hasattr(result, "model_dump")}")
    
    if hasattr(result, 'model_dump_json'):
        print("\n=== JSON OUTPUT ===")
        print(result.model_dump_json(indent=2))
    else:
        print("\n=== DICT OUTPUT ===")
        print(result.dict())

if __name__ == "__main__":
    asyncio.run(test_mcq_engine())