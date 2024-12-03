from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from src.crews.tools.latex_tools import LatexFormatter
from src.crews.tools.mathml_validator_tool import MathMLValidatorTool
from src.models.math_models import MathExplanation

@CrewBase
class MathTutorCrew():
    """Math Teaching crew that simulates a teacher explaining while writing on a whiteboard"""

    @agent
    def math_teacher(self) -> Agent:
        return Agent(
            config=self.agents_config['math_teacher'],
            verbose=True
        )

    @agent
    def math_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['math_reviewer'],
            tools=[MathMLValidatorTool()],
            verbose=True
        )

    @task
    def generate_explanation(self) -> Task:
        return Task(
            config=self.tasks_config['generate_explanation'],
            output_pydantic=MathExplanation
        )

    @task
    def validate_mathml(self) -> Task:
        return Task(
            config=self.tasks_config['validate_mathml'],
            output_pydantic=MathExplanation
        )

    @task
    def optimize_visual_narrative(self) -> Task:
        return Task(
            config=self.tasks_config['optimize_visual_narrative'],
            output_pydantic=MathExplanation
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.math_teacher(), self.math_reviewer()],
            tasks=[
                self.generate_explanation(),
                self.optimize_visual_narrative()
                # self.validate_mathml()
            ],
            process=Process.sequential,
            verbose=True
        )
