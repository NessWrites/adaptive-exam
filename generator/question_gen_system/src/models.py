from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ARRAY
from sqlalchemy.sql import func 
from generator.question_gen_system.src.database import Base 


class SubjectiveQuestion(Base):
    __tablename__ = "subjective_questions"
    
    #identity 
    id = Column(Integer, primary_key= True, index= True, autoincrement = True) 
    domain = Column(String(50), nullable = False, index = True)  #eg: math
    unit = Column(String(100), nullable = False)
    topic = Column(String(100), nullable = False)
    bloom_level = Column(Integer, nullable = False) 
    
    
    #content , we combine scenario and "final question" into one text for the front end 
    question_text = Column(Text, nullable = False) 
    
    concept_id = Column(String(100))
    skeleton_used = Column(Text) 
    
    
    #grading data(for auto-grader)
    correct_answer = Column(Text, nullable = False) 
    #step by step solution 
    solution_steps = Column(JSON, nullable= False) 
    
    #irt parameters for adaptive testing 
    a_value = Column(Float, default = 1.0) 
    b_value = Column(Float, default= 0.0 ) 
    calibration_status = Column(String(20), default = "pretest") #pretest vs original 
    
    created_at = Column(DateTime(timezone= True), server_default = func.now())
    
    
    