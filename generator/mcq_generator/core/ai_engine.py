import os 
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.prompts import ChatPromptTemplate 
from generator.mcq_generator.schemas.mcq_schema import MCQBatchOutput, MCQCoreLLMOutput

# class MCQEngine: 
#     def __init__(self): 
#         self.llm = ChatGoogleGenerativeAI(
#             model = 'gemini-2.5-flash',
#             temperature = 0.4,
#             api_key = os.getenv("GEMINI_API_KEY")
#             ).with_structured_output(MCQBatchOutput)
        
#         self.prompt = ChatPromptTemplate.from_messages(
#             [
#                 ("system", "You are an expert AI educator in computer science and mathematics. "
#                        "Your task is to convert subjective/theory questions into high-quality "
#                        "multiple-choice questions (MCQs). Provide exactly 4 options (A, B, C, D) "
#                        "With exactly one correct answer. Distractors should target common student misconceptions."
#                        "Each MCQ in the batch must target a Bloom's Taxonomy level as specified. "
#                        "Where bloom levels, 1 = remember, 2= Understand, 3 = apply, 4 = analyze")
#                 ,
#                 ("human", "Domain: {domain} \n"
#                  "Concept Tag: {concept_tag} \n\n"
#                  "Target Bloom Levels for this batch: {levels_list}\n\n"
#                  "Original Subjective Question: \n {question_text} \n\n"
#                  "Original Marking Scheme (Use this to create highly accurate distractors if provided): \n{mark_schema}\n\n"
#                  "Convert this into MCQ format reflecting the targeted Bloom level."
#                  "Generate exactly one MCQ for each Bloom level requested.")
#             ])
        
#         #need to add the marking scheme and answer such as to help the llm to create the answer and distractors successfully 
        
#     async def generate_mcq_batch(self, domain: str, concept_tag: str, question_text: str,
#                             levels :list[int], mark_scheme: str = "Not provided") -> MCQBatchOutput:
#             """Invoke the LangChain pipeline to transform the question """
#             chain = self.prompt | self.llm 
            
#             safe_mark_schema = str(mark_scheme) if mark_scheme else "Not provided"
            
            
#             result = await chain.ainvoke({
#                 "domain" : domain, 
#                 "concept_tag": concept_tag, 
#                 "question_text" : question_text,
#                 "levels_list": levels, 
#                 "mark_schema": safe_mark_schema,
#             })
            
#             return result
        

class MCQEngine:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.4,   # Lower temp → more deterministic stems/answers
            api_key=os.getenv("GEMINI_API_KEY"),
        ).with_structured_output(MCQBatchOutput)

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert AI educator specializing in computer science and mathematics assessment design.

YOUR SOLE TASK: Transform a subjective question into MCQ stems and correct answers only.

STRICT RULES — VIOLATIONS WILL BREAK THE PIPELINE:
1. ❌ DO NOT generate distractors, wrong options, or any options labeled A/B/C/D.
2. ❌ DO NOT include option letters in the correct_answer field.
3. ❌ DO NOT produce a dictionary of options. The `options` field does not exist in your output schema.
4. ✅ Generate EXACTLY one MCQCoreLLMOutput per requested Bloom level.
5. ✅ The `correct_answer` must be a plain text string (e.g., "O(n log n)", not "A. O(n log n)").
6. ✅ The `explanation` must justify the correct answer pedagogically at the specified Bloom level.
7. ✅ Bloom levels: 1=Remember, 2=Understand, 3=Apply, 4=Analyze.
8. ✅ MAKE IT TRICKY & WITTY: The question stem and correct answer should require deep reasoning, not just surface-level rote memorization. Add depth, clever wording, and theoretical nuance based on the marking schema.

A separate specialized engine will generate all distractors. Your output is the foundation layer only."""
            ),
            (
                "human",
                """Domain: {domain}
Concept Tag: {concept_tag}
Target Bloom Levels for this batch: {levels_list}
Original Subjective Question:
{question_text}

Original Marking Scheme (use to ensure correct_answer accuracy):
{mark_schema}

Generate exactly one MCQCoreLLMOutput per Bloom level listed above.
Remember: correct_answer is plain text only — no option letters, no distractors."""
            ),
        ])

    async def generate_mcq_batch(
        self,
        domain: str,
        concept_tag: str,
        question_text: str,
        levels: list[int],
        mark_scheme: str = "Not provided",
    ) -> MCQBatchOutput:
        chain = self.prompt | self.llm
        result = await chain.ainvoke({
            "domain": domain,
            "concept_tag": concept_tag,
            "question_text": question_text,
            "levels_list": levels,
            "mark_schema": str(mark_scheme) if mark_scheme else "Not provided",
        })
        return result