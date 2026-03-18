import os 
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.prompts import ChatPromptTemplate 
from generator.mcq_generator.schemas.mcq_schema import MCQoutput, MCQBatchOutput

class MCQEngine: 
    def __init__(self): 
        self.llm = ChatGoogleGenerativeAI(
            model = 'gemini-2.5-flash',
            temperature = 0.5,
            api_key = os.getenv("GEMINI_API_KEY")
            ).with_structured_output(MCQBatchOutput)
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an expert AI educator in computer science and mathematics. "
                       "Your task is to convert subjective/theory questions into high-quality "
                       "multiple-choice questions (MCQs). Provide exactly 4 options (A, B, C, D) "
                       "With exactly one correct answer. Distractors should target common student misconceptions."
                       "Each MCQ in the batch must target a Bloom's Taxonomy level as specified. "
                       "Where bloom levels, 1 = remember, 2= Understand, 3 = apply, 4 = analyze")
                ,
                ("human", "Domain: {domain} \n"
                 "Concept Tag: {concept_tag} \n\n"
                 "Target Bloom Levels for this batch: {levels_list}\n\n"
                 "Original Subjective Question: \n {question_text} \n\n"
                 "Original Marking Scheme (Use this to create highly accurate distractors if provided): \n{mark_schema}\n\n"
                 "Convert this into MCQ format reflecting the targeted Bloom level."
                 "Generate exactly one MCQ for each Bloom level requested.")
            ])
        
        #need to add the marking scheme and answer such as to help the llm to create the answer and distractors successfully 
        
    async def generate_mcq_batch(self, domain: str, concept_tag: str, question_text: str,
                            levels :list[int], mark_scheme: str = "Not provided") -> MCQBatchOutput:
            """Invoke the LangChain pipeline to transform the question """
            chain = self.prompt | self.llm 
            
            safe_mark_schema = str(mark_scheme) if mark_scheme else "Not provided"
            
            
            result = await chain.ainvoke({
                "domain" : domain, 
                "concept_tag": concept_tag, 
                "question_text" : question_text,
                "levels_list": levels, 
                "mark_schema": safe_mark_schema,
            })
            
            return result
        