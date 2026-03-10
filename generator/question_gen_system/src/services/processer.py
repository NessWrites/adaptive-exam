from generator.question_gen_system.src.schemas.items_schema import QuestionRow



def split_question(llm_response, domain, unit, topic,context, level):

    questions = llm_response.questions

    rows = [
        QuestionRow(
        domain = domain,
        topic = topic,
        unit = unit,
        context = context,
        bloom_level = level,
        question = q
        )
        for q in questions
    ]

    return rows



# creating question batch
def create_batches(rows, batch_size=60):
    for i in range(0, len(rows), batch_size):
        yield rows[i:i+ batch_size]


