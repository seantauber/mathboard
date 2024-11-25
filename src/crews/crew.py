from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from src.crews.tools.latex_tools import LatexFormatter
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
            verbose=True
        )

    @task
    def generate_explanation(self) -> Task:
        return Task(
            config=self.tasks_config['generate_explanation'],
            output_pydantic=MathExplanation
        )

    @task
    def validate_latex(self) -> Task:
        return Task(
            config=self.tasks_config['validate_latex'],
            output_pydantic=MathExplanation
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.math_teacher()],
            tasks=[self.generate_explanation()],
            process=Process.sequential,
            verbose=True
        )

    def _update_task_contexts(self, query: str) -> None:
        """Set the user query in task contexts"""
        for task_name in self.tasks_config:
            self.tasks_config[task_name]['context'] = {
                'user_query': query
            }

    async def process_math_query(self, query: str) -> dict:
        """Process a math query through the crew workflow"""
        try:
            # Set the query in task contexts
            self._update_task_contexts(query)

            # Run the crew
            result = await self.crew.kickoff()
            
            # Format any LaTeX in the result
            formatter = LatexFormatter()
            for step in result['steps']:
                step['math'] = formatter._run(step['math'])
            
            return result

        except Exception as e:
            print(f"Error in math crew: {e}")
            return {
                "error": True,
                "message": str(e)
            }
