from openai import OpenAI
import os
from os.path import join, dirname
from dotenv import load_dotenv

from agent import DesignTeamAgents
from datetime import datetime
import csv


GATHER_USER_NEEDS_TURN_LIMIT = 3
GATHER_BUSINESS_ANALYSIS_TURN_LIMIT = 3
# GATHER_BUSINESS_ANALYSIS_WORD_LIMIT = 40
GATHER_ETHICAL_ADVICE_TURN_LIMIT = 3
GATHER_TECHNICAL_ANALYSIS_TURN_LIMIT = 3
GATHER_INTERACTION_DESIGN_TURN_LIMIT = 3

initial_question = {
    "BUSINESS_ANALYST": "Could you tell me your insights on the business goals and constraints of the design task?",
    "ETHICS_ADVISOR": "Could you tell me your insights on the ethical implications and constraints of the design task?",
    "DEVELOPER": "Could you tell me your insights on the technical feasibility and constraints of the design task?",
    "INTERACTION_DESIGNER": "Could you tell me your insights on the user interface and user experience of the design task?",
}

class GroupIntelligence:
    def __init__(self) -> None:
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)
        OPENAI_API_KEY_1 = os.environ.get("OPENAI_API_KEY_1") 
        # OPENAI_API_KEY_2 = os.environ.get("OPENAI_API_KEY_2") 
        # self.model = "gpt-3.5-turbo"
        self.model = "gpt-4o-mini"
        self.client = OpenAI(api_key=OPENAI_API_KEY_1)
        # self.client2 = OpenAI(api_key=OPENAI_API_KEY_2)
        self.thread_clarify_end_user = None
        self.thread_understand_user_needs = None
        self.thread_gather_business_analysis = None
        self.thread_pm = None # The main thread - Product Manager thread
        self.design_team_agents = None
        self.user_researcher_agent = None
        self.stakeholder_agent = None
        self.product_manager_agent = None
        self.business_analyst_agent = None
        self.ethics_advisor_agent = None
        self.developer_agent = None
        self.interation_designer_agent = None


        # create files for each thread
        current_time = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
        folder_name = f"data/{current_time}"
        os.makedirs(folder_name, exist_ok=True)

        # User persona
        self.file_name_history_clarify_end_user_persona = f"{folder_name}/history_clarify_end_user_persona.txt"
        with open(self.file_name_history_clarify_end_user_persona, 'w+') as file:
            pass
        
        # User needs
        self.file_name_history_gather_user_needs = f"{folder_name}/history_gather_user_needs.txt"
        with open(self.file_name_history_gather_user_needs, mode='w+') as file:
            pass
        self.file_name_summary_gather_user_needs = f"{folder_name}/summary_gather_user_needs.txt"
        with open(self.file_name_summary_gather_user_needs, mode='w+') as file:
            pass

        
        
 
    # === Step 1: Human input a rough design task ===
    def createDesignTask(self):
        # Human input a rough design task
        design_task = "Design an app that helps overweight people form a healthy lifestyle."
        # design_task = "Design an app that helps students take online couses."
        return design_task
    
    # === Step 2: User researcher receives the task and indicates the target users. ===
    def clarifyStakeholderIdentity(self, design_task):
        # Stakeholder receives the task and clarify their identity
        thread = self.client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": f"This is the <DESIGN_TASK>: {design_task}. Please indicate one typical user persona that strongly correlated to this design task. You must only answer the persona. No extra words."
                }
            ]
        )
        self.thread_clarify_end_user = thread
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.thread_clarify_end_user.id,
            assistant_id=self.user_researcher_agent.id,
            instructions="Please clarify the persona." 
        )

        if run.status == "completed":
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            print(f"Stakeholder persona: {messages.data[0].content[0].text.value}")
            self.log_conversation("Stakeholder persona", messages.data[0].content[0].text.value, self.file_name_history_clarify_end_user_persona)
            return messages.data[0].content[0].text.value
        else:
            print(f"Stakeholder identity run status: {run.status}")
        
    # === Step 3: User researcher probe the stakeholders and gather user needs. ===
    def gatherUserNeeds(self, design_task, end_user_persona, chat_turn_limit):
        thread = self.client.beta.threads.create(
            # messages=[
            #     {
            #         "role": "user",
            #         "content": f"""\
            #         You are a <USER> and I am a <USER_RESEARCHER>. Never flip roles! \
            #         I will interview you about your experience and needs to get context information and insights for the <DESIGN_TASK>: {design_task}.\
            #         """
            #     }
            # ]
        )
        self.thread_understand_user_needs = thread

        n = 0
        # User Researcher ask the first question to the stakeholder
        user_researcher_msg = "Could you tell me a little about yourself?" 
        self.log_conversation("User Researcher", user_researcher_msg, self.file_name_history_gather_user_needs)
        print(f"\n\nUser researcher: \n{user_researcher_msg}\n")

        # Stakeholder answers the first question from the user researcher
        user_researcher_message = self.client.beta.threads.messages.create(
            thread_id=self.thread_understand_user_needs.id,
            role="user",
            content=user_researcher_msg
        )

        run_stakeholder_answer = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.thread_understand_user_needs.id,
            assistant_id=self.stakeholder_agent.id,
            additional_instructions="Please keep giving me detailed and insightful answers."
        )
        if run_stakeholder_answer.status == "completed":
                stakeholder_message = self.client.beta.threads.messages.list(thread_id=self.thread_understand_user_needs.id)
                stakeholder_msg = stakeholder_message.data[0].content[0].text.value
                self.log_conversation("Stakeholder", stakeholder_msg, self.file_name_history_gather_user_needs)
                print(f"\nStakeholder: \n{stakeholder_msg}\n")
        else:
            print(f"In gatherUserNeeds, run_stakeholder_answer status: {run_stakeholder_answer.status}")

        while n < chat_turn_limit:
            n += 1

            # User Researcher ask questions to the stakeholder 
            run_user_researcher_ask = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread_understand_user_needs.id,
                assistant_id=self.user_researcher_agent.id,
                additional_instructions=stakeholder_msg # Regulate the format of the message if necessary
            )
            if run_user_researcher_ask.status == "completed":
                user_researcher_message = self.client.beta.threads.messages.list(thread_id=self.thread_understand_user_needs.id)
                user_researcher_msg = user_researcher_message.data[0].content[0].text.value
                self.log_conversation("User Researcher", user_researcher_msg, self.file_name_history_gather_user_needs)
                print(f"\nUser Researcher: \n{user_researcher_msg}\n")
            else:
                print(f"In gatherUserNeeds, run_user_researcher_ask status: {run_user_researcher_ask.status}")

            # Stakeholder answers the questions from the user researcher
            run_stakeholder_answer = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread_understand_user_needs.id,
                assistant_id=self.stakeholder_agent.id,
                additional_instructions=user_researcher_msg
            )
            if run_stakeholder_answer.status == "completed":
                stakeholder_message = self.client.beta.threads.messages.list(thread_id=self.thread_understand_user_needs.id)
                stakeholder_msg = stakeholder_message.data[0].content[0].text.value
                self.log_conversation("Stakeholder", stakeholder_msg, self.file_name_history_gather_user_needs)
                print(f"\nStakeholder: \n{stakeholder_msg}\n")
            else:
                print(f"In gatherUserNeeds, run_stakeholder_answer status: {run_stakeholder_answer.status}")
        
            print(f"\nGather User Needs Turn: {n}\n")
        
    def createPRD(self, pm_agent, design_task, file_name_user_study_summary=None, file_name_business_analysis_summary=None, file_name_technical_analysis_summary=None, file_name_ethical_analysis_summary=None, file_name_design_analysis_summary=None):
        thread_pm = self.client.beta.threads.create()
        pm_agent = self.design_team_agents.updateProductManagerFor("Client", pm_agent, design_task, file_name_user_study_summary, file_name_business_analysis_summary, file_name_technical_analysis_summary, file_name_ethical_analysis_summary, file_name_design_analysis_summary)
        self.product_manager_agent = pm_agent

        # product_manager_message = self.client.beta.threads.messages.create(
        #     thread_id=thread_pm.id,
        #     role="user",
        #     content="Please create a detailed and executable Product Requirement Document (PRD) based on the provided information."
        # )

        # Agent answers the detail of the analysis
        run_agent_answer = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread_pm.id,
            assistant_id=pm_agent.id,
            additional_instructions="Please create a detailed and executable Product Requirement Document (PRD) based on the provided information."
        )
        if run_agent_answer.status == "completed":
                agent_message = self.client.beta.threads.messages.list(thread_id=thread_pm.id)
                agent_msg = agent_message.data[0].content[0].text.value
                self.log_conversation(pm_agent.name, agent_msg, self.file_name_prd)
                print(f"\n{pm_agent.name}: \n{agent_msg}\n")
        else:
            print(f"In gatherAnalysisFrom, run_agent_answer status: {run_agent_answer.status}")



    # === Shared Functions ===
    def log_summary(self, summary, file_name):
        with open(file_name, mode='a') as file:
            file.write(summary)

    def log_conversation(self, role, message, file_name):
        with open(file_name, mode='a') as file:
            file.write(f"{datetime.now()}, {role}: \n{message}\n\n\n")

    def getSummaryFromProductManager(self, design_task, input_file_name, output_file_name):
        user_study_summary = None
        # load the file to the thread
        file = self.client.files.create(
            file=open(input_file_name, "rb"),
            purpose="assistants"
        )

        thread = self.client.beta.threads.create(
            messages=[{
                "role": "user",
                "content": f"You are a <PRODUCT_MANAGER>. Please provide a detailed summary of the user study conversation from the txt file. This summary should be insightful for the <DESIGN_TASK>: {design_task}. Only reply the summay. Do not add anything else!", 
                "attachments": [{
                    "file_id": file.id,
                    "tools": [{"type": "code_interpreter"}]
                }]
                
            }]
        )
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=self.product_manager_agent.id,
            # instructions="Please only provide a detailed summary of the user study. Do not add anything else."
        )

        if run.status == "completed":
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            user_study_summary = messages.data[0].content[0].text.value
            print(f"Productor Manager - Conversation Summary: {user_study_summary}")
        else:
            print(f"Product Manager - Conversation summary run status: {run.status}")

        self.log_summary(user_study_summary, output_file_name)

        return user_study_summary

    def gatherAnalysisFrom(self, agent, pm_agent, design_task, initial_question, chat_turn_limit, file_name_history_to_be_saved):
        thread_pm = self.client.beta.threads.create()

        print(f"Agent: {agent.name}")
        pm_agent = self.design_team_agents.updateProductManagerFor(agent.name, pm_agent, design_task)
        self.product_manager_agent = pm_agent

        n = 0

        # Product manager asks the agent to provide an analysis of the design task
        product_manager_msg = initial_question
        self.log_conversation("Product Manager", product_manager_msg, file_name_history_to_be_saved)
        print(f"\n\nProduct Manager: \n{product_manager_msg}\n")

        product_manager_message = self.client.beta.threads.messages.create(
            thread_id=thread_pm.id,
            role="user",
            content=product_manager_msg
        )

        # Agent answers the detail of the analysis
        run_agent_answer = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread_pm.id,
            assistant_id=agent.id,
            additional_instructions="Please keep giving me detailed and insightful answers."
        )
        if run_agent_answer.status == "completed":
                agent_message = self.client.beta.threads.messages.list(thread_id=thread_pm.id)
                agent_msg = agent_message.data[0].content[0].text.value
                self.log_conversation(agent.name, agent_msg, file_name_history_to_be_saved)
                print(f"\n{agent.name}: \n{agent_msg}\n")
        else:
            print(f"In gatherAnalysisFrom, run_agent_answer status: {run_agent_answer.status}")
        
        while n < chat_turn_limit:
            n += 1

            # Product Manager ask questions to the agent
            run_product_manager_ask = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread_pm.id,
                assistant_id=pm_agent.id,
                additional_instructions=agent_msg
            )
            if run_product_manager_ask.status == "completed":
                product_manager_message = self.client.beta.threads.messages.list(thread_id=thread_pm.id)
                product_manager_msg = product_manager_message.data[0].content[0].text.value
                self.log_conversation("Product Manager", product_manager_msg, file_name_history_to_be_saved)
                print(f"\nProduct Manager: \n{product_manager_msg}\n")
            else:
                print(f"In gatherAnalysisFrom, run_product_manager_ask status: {run_product_manager_ask.status}")

            # Agent answers the questions from the Product Manager
            run_agent_answer = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread_pm.id,
                assistant_id=agent.id,
                additional_instructions=product_manager_msg
            )
            if run_agent_answer.status == "completed":
                agent_message = self.client.beta.threads.messages.list(thread_id=thread_pm.id)
                agent_msg = agent_message.data[0].content[0].text.value
                self.log_conversation(agent.name, agent_msg, file_name_history_to_be_saved)
                print(f"\n{agent.name}: \n{agent_msg}\n")
            else:
                print(f"In gatherAnalysisFrom, run_{agent.name}_answer status: {run_agent_answer.status}")

            print(f"\nGather {agent.name} Analysis Turn: {n}\n")

                
    def run(self):
        self.design_team_agents = DesignTeamAgents(client=self.client, model=self.model)
        
        
        # Step 1: Human input a rough design task
        design_task = self.createDesignTask()
        print(f"Design Task: {design_task}")
        
        # # Step 2: User researchers receives the task and indicates the target users. 
        # Create user researcher agent
        self.user_researcher_agent = self.design_team_agents.createUserResearcherAgent(design_task)
        # Clarify the stakeholder identity
        end_user_persona = self.clarifyStakeholderIdentity(design_task)
        # Create stakeholder agent
        self.stakeholder_agent = self.design_team_agents.createStakeholderAgent(design_task, end_user_persona)

        # Step 3: User researcher probe the stakeholders and gather user needs. Make a summary of the user needs and context information.
        self.gatherUserNeeds(design_task, end_user_persona, GATHER_USER_NEEDS_TURN_LIMIT)

        



if __name__ == "__main__":
    group_intelligence = GroupIntelligence()
    group_intelligence.run()