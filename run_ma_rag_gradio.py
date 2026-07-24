

import gradio as gr
from app.run import run_query


PROJ_IDS = [str(i) for i in range(1, 45)]
INSTRUMENTS = ["UPDRS", "UPDRS + PDQ-8", "PDQ-8"]
PLAN_TYPES = ["single-session", "trajectory", "comparison", "cohort"]

SINGLE_SESSION_OPTIONS = [
    "What is the baseline status of proj id {pid} using {instrument}?",
    "Compare the baseline and latest visit of proj id {pid} using {instrument}.",
]

TRAJECTORY_OPTIONS = [
    "Show me the {instrument} trajectory of proj id {pid}.",
]

COMPARISON_OPTIONS = {
    "2": "Compare the disease progression on {instrument} between proj id {pid1} and proj id {pid2}.",
    "3": "Compare the disease progression on {instrument} between proj id {pid1}, proj id {pid2}, and proj id {pid3}.",
}

COHORT_CATEGORY_OPTIONS = [
    "score-extreme",
    "deterioration",
    "risk",
]

COHORT_PROMPT_OPTIONS = {
    "score-extreme": [
        "Which patient has the best {instrument} score?",
        "Which patient has the lowest {instrument} score?",
        "Which patient has the highest {instrument} score?",
    ],
    "deterioration": [
        "Across all participants, which patient deteriorates fastest on {instrument}?",
    ],
    "risk": [
        "Which proj id is at high risk of disease progression based on {instrument}?",
        "Which proj id is at low risk of disease progression based on {instrument}?",
    ],
}


def update_plan_ui(plan_type):
    if plan_type == "single-session":
        return (
            gr.update(choices=SINGLE_SESSION_OPTIONS, value=SINGLE_SESSION_OPTIONS[0], visible=True),
            gr.update(visible=False, value="2"),
            gr.update(visible=False, value="score-extreme"),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
        )

    if plan_type == "trajectory":
        return (
            gr.update(choices=TRAJECTORY_OPTIONS, value=TRAJECTORY_OPTIONS[0], visible=True),
            gr.update(visible=False, value="2"),
            gr.update(visible=False, value="score-extreme"),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
        )

    if plan_type == "comparison":
        return (
            gr.update(choices=["Compare selected patients"], value="Compare selected patients", visible=True),
            gr.update(visible=True, value="2"),
            gr.update(visible=False, value="score-extreme"),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=False),
        )

    if plan_type == "cohort":
        first_category = COHORT_CATEGORY_OPTIONS[0]
        first_prompt = COHORT_PROMPT_OPTIONS[first_category][0]
        return (
            gr.update(choices=COHORT_PROMPT_OPTIONS[first_category], value=first_prompt, visible=True),
            gr.update(visible=False, value="2"),
            gr.update(visible=True, value=first_category),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
        )


def update_comparison_count(compare_count):
    return (
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=str(compare_count) == "3"),
    )


def update_cohort_category(category):
    prompts = COHORT_PROMPT_OPTIONS.get(category, [])
    first = prompts[0] if prompts else None
    return gr.update(choices=prompts, value=first, visible=True)


def build_query(plan_type, instrument, prompt_template, compare_count, pid1, pid2, pid3):
    if not prompt_template or not str(prompt_template).strip():
        return ""

    if plan_type == "comparison":
        query = COMPARISON_OPTIONS[str(compare_count)]
        query = query.replace("{instrument}", str(instrument))
        query = query.replace("{pid1}", str(pid1))
        query = query.replace("{pid2}", str(pid2))
        if "{pid3}" in query:
            query = query.replace("{pid3}", str(pid3))
        return query

    query = str(prompt_template).replace("{instrument}", str(instrument))

    if "{pid}" in query:
        query = query.replace("{pid}", str(pid1))

    return query


def run_agent_from_ui(plan_type, instrument, prompt_template, compare_count, pid1, pid2, pid3):
    query = build_query(plan_type, instrument, prompt_template, compare_count, pid1, pid2, pid3)

    if not query.strip():
        return ["", "", "", "", "", "", "", "", "", ""]

    result = run_query(query)

    return [
        query,
        str(result.get("final_answer", "")),
        result.get("analysis_plan", ""),
        result.get("extracted_facts", ""),
        str(result.get("motor_response", "")),
        str(result.get("adl_response", "")),
        str(result.get("nonmotor_response", "")),
        str(result.get("qol_response", "")),
        str(result.get("comparison_response", "")),
        str(result.get("cohort_response", "")),
    ]


with gr.Blocks(title="MA-RAG Clinical Summary Interface") as demo:
    gr.Markdown("## MA-RAG Clinical Summary Interface")
    gr.Markdown("Choose a plan, then fill only the controls needed for that workflow.")

    with gr.Row():
        plan_type = gr.Dropdown(choices=PLAN_TYPES, value="single-session", label="Plan Type")
        instrument = gr.Dropdown(choices=INSTRUMENTS, value="UPDRS", label="Instrument")

    cohort_category = gr.Dropdown(
        choices=COHORT_CATEGORY_OPTIONS,
        value="score-extreme",
        label="Cohort Analysis Type",
        visible=False,
    )

    prompt_template = gr.Dropdown(
        choices=SINGLE_SESSION_OPTIONS,
        value=SINGLE_SESSION_OPTIONS[0],
        label="Prompt Template",
        visible=True,
    )

    compare_count = gr.Dropdown(
        choices=["2", "3"],
        value="2",
        label="Number of Patients to Compare",
        visible=False,
    )

    with gr.Row():
        pid1 = gr.Dropdown(choices=PROJ_IDS, value="1", label="Proj ID 1", visible=True)
        pid2 = gr.Dropdown(choices=PROJ_IDS, value="2", label="Proj ID 2", visible=False)
        pid3 = gr.Dropdown(choices=PROJ_IDS, value="3", label="Proj ID 3", visible=False)

    built_query = gr.Textbox(label="Final Query", lines=2, interactive=False, show_copy_button=True)

    with gr.Row():
        preview_btn = gr.Button("Preview Query")
        run_btn = gr.Button("Run Query", variant="primary")

    gr.Markdown("### Final Clinical Summary")
    final_output = gr.Markdown()

    with gr.Accordion("Analysis Plan", open=False):
        plan_output = gr.Textbox(lines=4, show_copy_button=True)

    with gr.Accordion("Extracted Facts", open=False):
        facts_output = gr.Textbox(lines=10, show_copy_button=True)

    with gr.Accordion("Motor Agent Output", open=False):
        motor_output = gr.Markdown()

    with gr.Accordion("ADL Agent Output", open=False):
        adl_output = gr.Markdown()

    with gr.Accordion("Non-Motor Agent Output", open=False):
        nonmotor_output = gr.Markdown()

    with gr.Accordion("QoL Agent Output", open=False):
        qol_output = gr.Markdown()

    with gr.Accordion("Comparison Agent Output", open=False):
        comparison_output = gr.Markdown()

    with gr.Accordion("Cohort Agent Output", open=False):
        cohort_output = gr.Markdown()

    plan_type.change(
        fn=update_plan_ui,
        inputs=plan_type,
        outputs=[prompt_template, compare_count, cohort_category, pid1, pid2, pid3],
    )

    compare_count.change(
        fn=update_comparison_count,
        inputs=compare_count,
        outputs=[pid1, pid2, pid3],
    )

    cohort_category.change(
        fn=update_cohort_category,
        inputs=cohort_category,
        outputs=prompt_template,
    )

    preview_btn.click(
        fn=build_query,
        inputs=[plan_type, instrument, prompt_template, compare_count, pid1, pid2, pid3],
        outputs=built_query,
    )

    run_btn.click(
        fn=run_agent_from_ui,
        inputs=[plan_type, instrument, prompt_template, compare_count, pid1, pid2, pid3],
        outputs=[
            built_query,
            final_output,
            plan_output,
            facts_output,
            motor_output,
            adl_output,
            nonmotor_output,
            qol_output,
            comparison_output,
            cohort_output,
        ],
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=True)
    
    
       