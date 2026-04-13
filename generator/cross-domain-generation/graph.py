from langgraph.graph import StateGraph, START, END
from state import GraphState
from nodes.input_validator import input_validator
from nodes.scenario_generator import scenario_generator
from nodes.scenario_evaluator import scenario_evaluator
from nodes.question_type_classifier import question_type_classifier
from nodes.question_generator import question_generator
from nodes.student_agent import student_agent
from nodes.feedback_handler import feedback_handler
from nodes.pedagogical_prior_evaluator import pedagogical_prior_evaluator
from nodes.file_output import file_output




def after_validation(state: GraphState) -> str:
    if state.get("error"):
        return "__end__"
    return "scenario_generator"

def after_scenario_evaluator(state: GraphState) -> str:
    if state.get("error"):
        return "__end__"
    if state.get("top_scenario"):
        return "question_type_classifier"
    return "scenario_generator"

def after_question_type_classifier(state: GraphState) -> str:
    if state.get("error"):
        return "__end__"
    return "question_generator" 

def after_question_generator(state: GraphState) -> str:
    if state.get("error"):
        return "__end__"
    return "student_agent"

def after_student_agent(state: GraphState) -> str:
    if state.get("error"):
        return "__end__"
    
    attempts = state.get("student_attempts", [])

    solvable = [
        a for a in attempts if a["solvability"]["solvable"]
    ]

    if len(solvable)==0:
        if state.get("question_retry_count", 0) >=3:
            return "__end__"
        return "feedback_handler"
    return "pedagogical_prior_evaluator"

def after_pedagogical_prior_evaluator(state: GraphState) -> str:
    if state.get("error"):
        return "__end__"
    if state.get("evaluated_pairs"):
        return "file_output"
    return "question_generator"


def after_file_output(state:GraphState)-> str:
    if state.get("error"):
        return "__end__"
    return "__end__"


def build_graph():
    graph_builder = StateGraph(GraphState)
    
    # add nodes
    graph_builder.add_node("input_validator", input_validator)
    graph_builder.add_node("scenario_generator", scenario_generator)
    graph_builder.add_node("scenario_evaluator", scenario_evaluator)
    graph_builder.add_node("question_type_classifier", question_type_classifier)
    graph_builder.add_node("question_generator", question_generator)
    graph_builder.add_node("student_agent", student_agent)
    graph_builder.add_node("feedback_handler", feedback_handler)
    graph_builder.add_node("pedagogical_prior_evaluator", pedagogical_prior_evaluator)
    graph_builder.add_node("file_output", file_output)


    # create edges
    graph_builder.add_edge(START, "input_validator")
    graph_builder.add_conditional_edges("input_validator", after_validation, {
        "__end__" : END,
        "scenario_generator" : "scenario_generator"
    })
    graph_builder.add_edge("scenario_generator", "scenario_evaluator")
    graph_builder.add_conditional_edges("scenario_evaluator", after_scenario_evaluator, {
            "__end__" : END,
            "scenario_generator": "scenario_generator",
            "question_type_classifier":"question_type_classifier"
        }
    )
    graph_builder.add_conditional_edges("question_type_classifier", after_question_type_classifier, {
        "__end__" : END,
        "question_generator":"question_generator"
    })
    graph_builder.add_conditional_edges("question_generator", after_question_generator, {
        "__end__": END,
        "student_agent" : "student_agent"
    })
    graph_builder.add_conditional_edges("student_agent", after_student_agent, {
        "__end__" : END,
        "feedback_handler" : "feedback_handler",
        "pedagogical_prior_evaluator": "pedagogical_prior_evaluator"
    })
    graph_builder.add_edge("feedback_handler", "question_generator")

    graph_builder.add_conditional_edges("pedagogical_prior_evaluator", after_pedagogical_prior_evaluator, {
        "__end__":END,
        "question_generator" : "question_generator",
        "file_output" : "file_output"
    })

    graph_builder.add_conditional_edges(
        "file_output", after_file_output, {
            "__end__": END
        }
    )

    return graph_builder.compile()

graph = build_graph()