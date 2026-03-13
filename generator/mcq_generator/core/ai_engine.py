import os 
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.prompts import ChatPromptTemplate 
from generator.mcq_generator.schemas.mcq_schema import MCQoutput 

class MCQEngine: 
    def __init__(self): 
        self.llm = ChatGoogleGenerativeAI(
            model = 'gemini-2.5-flash',
            temperature = 0.3,
            api_key = os.getenv("GEMINI_API_KEY")
            ).with_structured_output(MCQoutput)
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an expert AI educator in computer science and mathematics. "
                       "Your task is to convert subjective/theory questions into high-quality "
                       "multiple-choice questions (MCQs). Provide exactly 4 options (A, B, C, D) "
                       "with exactly one correct answer. Distractors should target common student misconceptions.")
                ,
                ("human", "Domain: {domain} \n"
                 "Concept Tat: {concept_tag} \n\n"
                 "Original Subjective Question: \n {question_text} \n\n"
                 "Convert this into MCQ format")
            ])
        
        #need to add the marking scheme and answer such as to help the llm to create the answer and distractors successfully 
        
        async def generate_mcq(self, domain: str, concept_tag: str, question_text: str) -> MCQoutput:
            """Invoke the LangChain pipeline to transform the question """
            chain = self.prompt | self.llm 
            result = await chain.ainvoke({
                "domain" : domain, 
                "concept_tag": concept_tag, 
                "question_text" : question_text
            })
            
            return result
        