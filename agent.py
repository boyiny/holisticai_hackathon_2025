from openai import OpenAI
import os
from os.path import join, dirname
from dotenv import load_dotenv

# from typing import List
# from langchain.chat_models import ChatOpenAI
# from langchain.prompts.chat import (
#     SystemMessagePromptTemplate,
#     HumanMessagePromptTemplate,
# )
# from langchain.schema import (
#     AIMessage,
#     HumanMessage,
#     SystemMessage,
#     BaseMessage,
# )


# model = "gpt-4o"
# dotenv_path = join(dirname(__file__), '.env')
# load_dotenv(dotenv_path)
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") 
# client = OpenAI(api_key=OPENAI_API_KEY)

general_instructions_for_answering_questions = """
    You must ONLY answer my questions based on your expertise to complete the task honestly and detailedly. \

    I must give you one or a few interview questions at a time. You must answer all questions. \
    You must write specific answers that are insightful for the <DESIGN_TASK>. \
    Unless I say the task is completed, you should always start with: 
    
    Reply: <YOUR_REPLY> 
    
    <YOUR_REPLY> should be specific, and provide insightful information that reflects your characteristic and identity. \
    Always end <YOUR_REPLY> with: 
    
    Please let me know if you have further questions.
    
    Do not add anything else other than your reply to my questions! \
    Keep giving me detailed and insightful answers until you think it is sufficient for inspring the design task. \
"""







# interaction_designer = {
#     "name": "Interaction Designer",
#     "description": """
#     """,
#     "instructions": """
#     You are an interaction designer working with a product manager. 
#     Your goal is to design the user experience that addresses the user needs and business goals.
#     The interaction designer agent is responsible for designing the user experience and interface of the product. The agent is responsible for creating wireframes, prototypes, and user flows to define the user journey. The interaction designer agent is also responsible for conducting user testing to validate design decisions.
#     """
# }



# ethics_advisor = {
#     "name": "Ethics Advisor",
#     "description": """
#     """,
#     "instructions": """
#     You are a ethics advisor working with a product manager.
#     The ethics advisor ensures that the design process and the final product adhere to ethical standards, considering user privacy, data security, and ethical implications.
#     """
# }



# developer = {
#     "name": "Developer",
#     "description": """
#     """,
#     "instructions": """
#     The developer is responsible for evaluating the feasbility of product features, including the technical requirements and constraints. 
#     """
# }



class DesignTeamAgents:
    def __init__(self, client, model):
        self.client = client
        self.model = model
        self.conversation_history_file_name = None

    
    def declare_user_researcher(self, design_task):
        user_researcher = {
            "name": "User Researcher",
            "description": """
            """,
            "instructions": f"""
            Never forget you are a <USER_RESEARCHER> and I am a <USER>. Never flip roles! Never repeat what I say! \
            You must ask me questions to my experiene, requirements, expections, and preferences to get context information and insights for the <DESIGN_TASK>. \
            Here is the <DESIGN_TASK>: {design_task}. Never forget the design task! \
            
            We share a common interest in collaborating to successfully understand my goals, needs, expections, preferences, and all context information. \
            Your may ask me one or a few questions at a time. You can ask me follow-up questions to gather more information. \
            You must keep asking me necessary questions to understand my motivation, goals, needs and relavent context information in detail. \    
            """
        }
        return user_researcher
    
    def declare_stakeholder(self, design_task, persona):
        stakeholder = {
            "name": "User",
            "description": """
            """,
            "instructions": f"""Never forget you are a <USER> and I am a <USER_RESEARCHER>. Never flip the roles! \
            Never forget your persona: \
            <persona> {persona} </persona>. \
            
            Never forget you are telling me your experience and needs that are relevant to the <DESIGN_TASK>. \
            Here is the <DESIGN_TASK>: {design_task}. 

            We share a common interest in collaborating to successfully understand your needs, expections, preferences, and all context information. \
            
            You must use a natural language style that is relevant to your persona. \
            {general_instructions_for_answering_questions}
            """
        }
        # Keep giving me detailed and insightful answers until you think it is sufficient for inspring the design task. \
        return stakeholder
    
    def declare_product_manager(self, design_task):
        product_manager = {
            "name": "Product Manager",
            "description": """
            """,
            "instructions": f""" 
            You are a product manager working with a team of user researcher, interaction designer, business analyst, ethics advisor, and stakeholder to develop a new product. 
            Your goal is to discuss with other team members to help them to compelet their goals in a shared design task. 
            Your goal is to understand the essential features of the product, the target audience, and the business goals.
            Here is the design task: {design_task}. Never forget the design task. Never forget your role in the team.
            You may ask one or a few questions to one team member at a time. 
            You must keep asking necessary questions until you think the team member's goal is completed.
            When the task is completed, you must provide a summary of the task. 
            """
        }
        return product_manager
    
    def update_product_manager_for_business_analysis(self, design_task, user_study_summary=None, business_analysis_summary=None, technical_analysis_summary=None, ethical_analysis_summary=None, design_analysis_summary=None):
        text_user_study_summary = ""
        text_business_analysis = ""
        text_ethical_analysis = ""
        text_technical_analysis = ""
        text_design_analysis = ""
        if user_study_summary:
            text_user_study_summary = f"Here is the <USER_STUDY_SUMMARY> {user_study_summary} </USER_STUDY_SUMMARY>."
        if business_analysis_summary:
            text_business_analysis = f"Here is the <BUSINESS_ANALYSIS_SUMMARY> {business_analysis_summary} </BUSINESS_ANALYSIS_SUMMARY>."
        if technical_analysis_summary:
            text_technical_analysis = f"Here is the <TECHNICAL_ANALYSIS_SUMMARY> {technical_analysis_summary} </TECHNICAL_ANALYSIS_SUMMARY>."
        if ethical_analysis_summary:
            text_ethical_analysis = f"Here is the <ETHICAL_ANALYSIS_SUMMARY> {ethical_analysis_summary} </ETHICAL_ANALYSIS_SUMMARY>."
        if design_analysis_summary:
            text_design_analysis = f"Here is the <DESIGN_ANALYSIS_SUMMARY> {design_analysis_summary} </DESIGN_ANALYSIS_SUMMARY>."
        
        
        product_manager = {
            "name": "Product Manager",
            "description": """
            """,
            "instructions": f"""
            Never forget you are a <PRODUCT_MANAGER> and I am a <BUSINESS_ANALYST>. Never flip roles! Never repeat what I say! You must keep asking me questions to understand business insights for the <DESIGN_TASK> based on the information provided below: 
            Here is the <DESIGN_TASK>: {design_task}. Never forget the design task! 
            {text_user_study_summary} 
            {text_business_analysis}
            {text_ethical_analysis}
            {text_technical_analysis}
            {text_design_analysis}

            We share a common interest in collaborating to successfully understand the current market size, the market gaps, how can this product make profit, what are the competitors and other relevant questions about business. \
            Your may ask me one or a few questions at a time. You can ask me follow-up questions to gather more information. \
            You must keep asking me necessary questions until you think the my needs are understood. \
            When you think you have get enought information, you can end this interview by providing a summary our discussion. \
            """
        }
        return product_manager
    
    def update_product_manager_for_ethics_advisor(self, design_task, user_study_summary=None, business_analysis_summary=None, technical_analysis_summary=None, ethical_analysis_summary=None, design_analysis_summary=None):
        text_user_study_summary = ""
        text_business_analysis = ""
        text_ethical_analysis = ""
        text_technical_analysis = ""
        text_design_analysis = ""
        if user_study_summary:
            text_user_study_summary = f"Here is the <USER_STUDY_SUMMARY> {user_study_summary} </USER_STUDY_SUMMARY>."
        if business_analysis_summary:
            text_business_analysis = f"Here is the <BUSINESS_ANALYSIS_SUMMARY> {business_analysis_summary} </BUSINESS_ANALYSIS_SUMMARY>."
        if technical_analysis_summary:
            text_technical_analysis = f"Here is the <TECHNICAL_ANALYSIS_SUMMARY> {technical_analysis_summary} </TECHNICAL_ANALYSIS_SUMMARY>."
        if ethical_analysis_summary:
            text_ethical_analysis = f"Here is the <ETHICAL_ANALYSIS_SUMMARY> {ethical_analysis_summary} </ETHICAL_ANALYSIS_SUMMARY>."
        if design_analysis_summary:
            text_design_analysis = f"Here is the <DESIGN_ANALYSIS_SUMMARY> {design_analysis_summary} </DESIGN_ANALYSIS_SUMMARY>."

        product_manager = {
            "name": "Product Manager",
            "description": """
            """,
            "instructions": f"""
            Never forget you are a <PRODUCT_MANAGER> and I am a <ETHICS_ADVISOR>. Never flip roles! Never repeat what I say! You must keep asking me questions to understand the potential ethical risks for the <DESIGN_TASK> based on the information provided below: 
            Here is the <DESIGN_TASK>: {design_task}. Never forget the design task! 
            {text_user_study_summary} 
            {text_business_analysis}
            {text_ethical_analysis}
            {text_technical_analysis}
            {text_design_analysis}

            We share a common interest in collaborating to successfully understand what are the potential ethical risks of our product, how the competitors handle their ethical risks, how can we handle the ethical risks of our product, and other relevant questions about ethics. \
            Your may ask me one or a few questions at a time. You can ask me follow-up questions to gather more information. \
            You must keep asking me necessary questions until you think the the ethical risks are understood. \
            When you think you have get enought information, you can end this interview by providing a summary our discussion. \
            """
        }
        return product_manager
    
    def update_product_manager_for_developer(self, design_task, user_study_summary=None, business_analysis_summary=None, technical_analysis_summary=None, ethical_analysis_summary=None, design_analysis_summary=None):
        text_user_study_summary = ""
        text_business_analysis = ""
        text_ethical_analysis = ""
        text_technical_analysis = ""
        text_design_analysis = ""

        if user_study_summary:
            text_user_study_summary = f"Here is the <USER_STUDY_SUMMARY> {user_study_summary} </USER_STUDY_SUMMARY>."
        if business_analysis_summary:
            text_business_analysis = f"Here is the <BUSINESS_ANALYSIS_SUMMARY> {business_analysis_summary} </BUSINESS_ANALYSIS_SUMMARY>."
        if technical_analysis_summary:
            text_technical_analysis = f"Here is the <TECHNICAL_ANALYSIS_SUMMARY> {technical_analysis_summary} </TECHNICAL_ANALYSIS_SUMMARY>."
        if ethical_analysis_summary:
            text_ethical_analysis = f"Here is the <ETHICAL_ANALYSIS_SUMMARY> {ethical_analysis_summary} </ETHICAL_ANALYSIS_SUMMARY>."
        if design_analysis_summary:
            text_design_analysis = f"Here is the <DESIGN_ANALYSIS_SUMMARY> {design_analysis_summary} </DESIGN_ANALYSIS_SUMMARY>."
        
        product_manager = {
            "name": "Product Manager",
            "description": """
            """,
            "instructions": f"""
            Never forget you are a <PRODUCT_MANAGER> and I am a <DEVELOPER>. Never flip roles! Never repeat what I say! You must keep asking me questions to understand the technical feasbility for the <DESIGN_TASK> based on the information provided below: 
            Here is the <DESIGN_TASK>: {design_task}. Never forget the design task! 
            {text_user_study_summary} 
            {text_business_analysis}
            {text_ethical_analysis}
            {text_technical_analysis}
            {text_design_analysis}

            We share a common interest in collaborating to successfully understand the technical requirements and constraints of the product features. \
            Your may ask me one or a few questions at a time. You can ask me follow-up questions to gather more information. \
            You must keep asking me necessary questions until you think the technical feasbility is understood. \
            When you think you have get enought information, you can end this interview by providing a summary our discussion. \
            """
        }
        return product_manager
    
    def update_product_manager_for_interaction_designer(self, design_task, user_study_summary=None, business_analysis_summary=None, technical_analysis_summary=None, ethical_analysis_summary=None, design_analysis_summary=None):
        text_user_study_summary = ""
        text_business_analysis = ""
        text_ethical_analysis = ""
        text_technical_analysis = ""
        text_design_analysis = ""

        if user_study_summary:
            text_user_study_summary = f"Here is the <USER_STUDY_SUMMARY> {user_study_summary} </USER_STUDY_SUMMARY>."
        if business_analysis_summary:
            text_business_analysis = f"Here is the <BUSINESS_ANALYSIS_SUMMARY> {business_analysis_summary} </BUSINESS_ANALYSIS_SUMMARY>."
        if technical_analysis_summary:
            text_technical_analysis = f"Here is the <TECHNICAL_ANALYSIS_SUMMARY> {technical_analysis_summary} </TECHNICAL_ANALYSIS_SUMMARY>."
        if ethical_analysis_summary:
            text_ethical_analysis = f"Here is the <ETHICAL_ANALYSIS_SUMMARY> {ethical_analysis_summary} </ETHICAL_ANALYSIS_SUMMARY>."
        if design_analysis_summary:
            text_design_analysis = f"Here is the <DESIGN_ANALYSIS_SUMMARY> {design_analysis_summary} </DESIGN_ANALYSIS_SUMMARY>."
        
        product_manager = {
            "name": "Product Manager",
            "description": """
            """,
            "instructions": f"""
            Never forget you are a <PRODUCT_MANAGER> and I am an <INTERACTION_DESIGNER>. Never flip roles! Never repeat what I say! You must keep asking me questions to understand the interaction design of the <DESIGN_TASK> based on the information provided below: 
            Here is the <DESIGN_TASK>: {design_task}. Never forget the design task! 
            {text_user_study_summary} 
            {text_business_analysis}
            {text_ethical_analysis}
            {text_technical_analysis}
            {text_design_analysis}

            We share a common interest in collaborating to successfully design an effecient, effective, and user-friendly product that meets all essential needs mentioned in the provided information. \
            Your may ask me one or a few questions at a time. You can ask me follow-up questions to gather more information. \
            You must keep asking me necessary questions until you think the technical feasbility is understood. \
            When you think you have get enought information, you can end this interview by providing a summary our discussion. \
            """
        }
        return product_manager
    
    def update_product_manager_for_client(self, design_task, user_study_summary=None, business_analysis_summary=None, technical_analysis_summary=None, ethical_analysis_summary=None, design_analysis_summary=None):
        text_user_study_summary = ""
        text_business_analysis = ""
        text_ethical_analysis = ""
        text_technical_analysis = ""
        text_design_analysis = ""

        if user_study_summary:
            text_user_study_summary = f"Here is the <USER_STUDY_SUMMARY> {user_study_summary} </USER_STUDY_SUMMARY>."
        if business_analysis_summary:
            text_business_analysis = f"Here is the <BUSINESS_ANALYSIS_SUMMARY> {business_analysis_summary} </BUSINESS_ANALYSIS_SUMMARY>."
        if technical_analysis_summary:
            text_technical_analysis = f"Here is the <TECHNICAL_ANALYSIS_SUMMARY> {technical_analysis_summary} </TECHNICAL_ANALYSIS_SUMMARY>."
        if ethical_analysis_summary:
            text_ethical_analysis = f"Here is the <ETHICAL_ANALYSIS_SUMMARY> {ethical_analysis_summary} </ETHICAL_ANALYSIS_SUMMARY>."
        if design_analysis_summary:
            text_design_analysis = f"Here is the <DESIGN_ANALYSIS_SUMMARY> {design_analysis_summary} </DESIGN_ANALYSIS_SUMMARY>."
        
        product_manager = {
            "name": "Product Manager",
            "description": """
            """,
            "instructions": f"""
            Never forget you are a <PRODUCT_MANAGER>. You need to write a detailed and executable product requirement document (PRD) based on the information provided below:
            Here is the <DESIGN_TASK>: {design_task}. Never forget the design task! 
            {text_user_study_summary} 
            {text_business_analysis}
            {text_ethical_analysis}
            {text_technical_analysis}
            {text_design_analysis}

            The PRD should link the user needs, business goals, and technical feasbility to the product features. \
            The PRD should include all the essential requirements for the product features. \
            """
        }
        return product_manager
    
    #  This PRD should include the following sections:
    #         1. Product Overview
    #         2. Product Objectives
    #         3. Market Analysis
    #         3. Target Audience
    #         4. User Stories
    #         5. Functional Requirements
    #         6. Non-Functional Requirements
    #         7. Wireframes
    #         8. User Flows
    #         9. Acceptance Criteria
    #         10. Risks and Assumptions
    #         11. Dependencies
    #         12. Timeline
    #         13. Budget
    #         14. Success Metrics
    #         15. Conclusion
    
    def declare_interaction_designer(self, design_task, user_study_summary=None, business_analysis_summary=None, technical_analysis_summary=None, ethical_analysis_summary=None, design_analysis_summary=None):
        text_user_study_summary = ""
        text_business_analysis = ""
        text_ethical_analysis = ""
        text_technical_analysis = ""
        text_design_analysis = ""
        
        if user_study_summary:
            text_user_study_summary = f"Here is the <USER_STUDY_SUMMARY> {user_study_summary} </USER_STUDY_SUMMARY>."
        if business_analysis_summary:
            text_business_analysis = f"Here is the <BUSINESS_ANALYSIS_SUMMARY> {business_analysis_summary} </BUSINESS_ANALYSIS_SUMMARY>."
        if technical_analysis_summary:
            text_technical_analysis = f"Here is the <TECHNICAL_ANALYSIS_SUMMARY> {technical_analysis_summary} </TECHNICAL_ANALYSIS_SUMMARY>."
        if ethical_analysis_summary:
            text_ethical_analysis = f"Here is the <ETHICAL_ANALYSIS_SUMMARY> {ethical_analysis_summary} </ETHICAL_ANALYSIS_SUMMARY>."
        if design_analysis_summary:
            text_design_analysis = f"Here is the <DESIGN_ANALYSIS_SUMMARY> {design_analysis_summary} </DESIGN_ANALYSIS_SUMMARY>."

        interaction_designer = {
            "name": "Interaction Designer",
            "description": """
            """,
            "instructions": f"""
            Never forget you are a <INTERACTION_DESIGNER> and I am a <PRODUCT_MANAGER>. Never flip roles! Never repeat what I say! \
            Never forget you are helping me to conduct the conceptual design for the <DESIGN_TASK>. \
            Never forget we share a common interest in collaborating to successfully design a product that meets all essential requirements from the information provided below: 
            Here is the <DESIGN_TASK>: {design_task}. Never forget the design task! \
            {text_user_study_summary}
            {text_business_analysis} 
            {text_ethical_analysis} 
            {text_technical_analysis} 
            {text_design_analysis}

            We share a common interest in collaborating to successfully design an effecient, effective, and user-friendly product that meets all essential needs mentioned in the provided information. \
            {general_instructions_for_answering_questions}
            """
        }
        return interaction_designer
    
    
    def declare_business_analyst(self, design_task, user_study_summary=None, business_analysis_summary=None, technical_analysis_summary=None, ethical_analysis_summary=None, design_analysis_summary=None):
        text_user_study_summary = ""
        text_business_analysis = ""
        text_technical_analysis = ""
        text_ethical_analysis = ""
        text_design_analysis = ""

        if user_study_summary:
            text_user_study_summary = f"Here is the <USER_STUDY_SUMMARY> {user_study_summary} </USER_STUDY_SUMMARY>."
        if business_analysis_summary:
            text_business_analysis = f"Here is the <BUSINESS_ANALYSIS_SUMMARY> {business_analysis_summary} </BUSINESS_ANALYSIS_SUMMARY>."
        if technical_analysis_summary:
            text_technical_analysis = f"Here is the <TECHNICAL_ANALYSIS_SUMMARY> {technical_analysis_summary} </TECHNICAL_ANALYSIS_SUMMARY>."
        if ethical_analysis_summary:
            text_ethical_analysis = f"Here is the <ETHICAL_ANALYSIS_SUMMARY> {ethical_analysis_summary} </ETHICAL_ANALYSIS_SUMMARY>."
        if design_analysis_summary:
            text_design_analysis = f"Here is the <DESIGN_ANALYSIS_SUMMARY> {design_analysis_summary} </DESIGN_ANALYSIS_SUMMARY>."

        business_analyst = {
            "name": "Business Analyst",
            "description": """
            """,
            "instructions": f"""
            Never forget you are a <BUSINESS_ANALYST> and I am a <PRODUCT_MANAGER>. Never flip the roles! \
            Never forget you are helping me to analyze the business insights for the <DESIGN_TASK>. \
            You always answer my questions about your business insights that are relevant to the information provided below:
            Here is the <DESIGN_TASK> {design_task} </DESIGN_TASK>. 
            {text_user_study_summary}
            {text_business_analysis}
            {text_technical_analysis} 
            {text_ethical_analysis} 
            {text_design_analysis}

            We share a common interest in collaborating to successfully understand the current market size, the market gaps, how can this product make profit, what are the competitors and other relevant questions about business. \
            {general_instructions_for_answering_questions}
            """
        }
        return business_analyst

    def declare_ethics_advisor(self, design_task, user_study_summary=None, business_analysis_summary=None, technical_analysis_summary=None, ethical_analysis_summary=None, design_analysis_summary=None):
        text_user_study_summary = ""
        text_business_analysis = ""
        text_technical_analysis = ""
        text_ethical_analysis = ""
        text_design_analysis = ""
        
        if user_study_summary:
            text_user_study_summary = f"Here is the <USER_STUDY_SUMMARY> {user_study_summary} </USER_STUDY_SUMMARY>."
        if business_analysis_summary:
            text_business_analysis = f"Here is the <BUSINESS_ANALYSIS_SUMMARY> {business_analysis_summary} </BUSINESS_ANALYSIS_SUMMARY>."
        if technical_analysis_summary:
            text_technical_analysis = f"Here is the <TECHNICAL_ANALYSIS_SUMMARY> {technical_analysis_summary} </TECHNICAL_ANALYSIS_SUMMARY>."
        if ethical_analysis_summary:
            text_ethical_analysis = f"Here is the <ETHICAL_ANALYSIS_SUMMARY> {ethical_analysis_summary} </ETHICAL_ANALYSIS_SUMMARY>."
        if design_analysis_summary:
            text_design_analysis = f"Here is the <DESIGN_ANALYSIS_SUMMARY> {design_analysis_summary} </DESIGN_ANALYSIS_SUMMARY>."

        ethics_advisor = {
            "name": "Ethics Advisor",
            "description": """
            """,
            "instructions": f"""
            Never forget you are a <ETHICS_ADVISOR> and I am a <PRODUCT_MANAGER>. Never flip the roles! \
            Never forget you are helping me to analyze the potential ethical risks for the <DESIGN_TASK>. \
            You always answer my questions about your ethical advices that are relevant to the information provided below:
            Here is the <DESIGN_TASK> {design_task} </DESIGN_TASK>. 
            {text_user_study_summary}
            {text_business_analysis} 
            {text_technical_analysis} 
            {text_ethical_analysis}
            {text_design_analysis}

            We share a common interest in collaborating to successfully understand what are the potential ethical risks of our product, how the competitors handle their ethical risks, how can we handle the ethical risks of our product, and other relevant questions about ethics. \
            {general_instructions_for_answering_questions}
            """
        }
        return ethics_advisor
    
    def declare_developer(self, design_task, user_study_summary=None, business_analysis_summary=None, technical_analysis_summary=None, ethical_analysis_summary=None, design_analysis_summary=None):
        text_user_study_summary = ""
        text_business_analysis = ""
        text_technical_analysis = ""
        text_ethical_analysis = ""
        text_design_analysis = ""

        if user_study_summary:
            text_user_study_summary = f"Here is the <USER_STUDY_SUMMARY> {user_study_summary} </USER_STUDY_SUMMARY>."
        if business_analysis_summary:
            text_business_analysis = f"Here is the <BUSINESS_ANALYSIS_SUMMARY> {business_analysis_summary} </BUSINESS_ANALYSIS_SUMMARY>."
        if technical_analysis_summary:
            text_technical_analysis = f"Here is the <TECHNICAL_ANALYSIS_SUMMARY> {technical_analysis_summary} </TECHNICAL_ANALYSIS_SUMMARY>."
        if  ethical_analysis_summary:
            text_ethical_analysis = f"Here is the <ETHICAL_ANALYSIS_SUMMARY> {ethical_analysis_summary} </ETHICAL_ANALYSIS_SUMMARY>."
        if design_analysis_summary:
            text_design_analysis = f"Here is the <DESIGN_ANALYSIS_SUMMARY> {design_analysis_summary} </DESIGN_ANALYSIS_SUMMARY>."

        developer = {
            "name": "Developer",
            "description": """
            """,
            "instructions": f"""
            Never forget you are a <DEVELOPER> and I am a <PRODUCT_MANAGER>. Never flip the roles! \
            Never forget you are helping me to analyze the technical feasbility for the <DESIGN_TASK>. \
            You always answer my questions about your technical feasbility that are relevant to the information provided below: 
            Here is the <DESIGN_TASK> {design_task} </DESIGN_TASK>. 
            {text_user_study_summary} 
            {text_business_analysis} 
            {text_ethical_analysis} 
            {text_technical_analysis}
            {text_design_analysis}

            We share a common interest in collaborating to successfully understand the technical requirements and constraints of the product features. \
            {general_instructions_for_answering_questions}
            """
        }
        return developer
    

    def createUserResearcherAgent(self, design_task):
        user_researcher_agent = self.client.beta.assistants.create(
            name = self.declare_user_researcher(design_task)["name"],
            # description = user_researcher["description"],
            instructions = self.declare_user_researcher(design_task)["instructions"],
            model = self.model,
            tools = [{"type":"code_interpreter"}]
        )
        return user_researcher_agent
    
    def createStakeholderAgent(self, design_task, persona):
        stakeholder_agent = self.client.beta.assistants.create(
            name = self.declare_stakeholder(design_task, persona)["name"],
            # description = stakeholder["description"],
            instructions = self.declare_stakeholder(design_task, persona)["instructions"],
            model = self.model,
            tools = [{"type":"code_interpreter"}]
        )
        return stakeholder_agent

    def createProductManagerAgent(self, design_task):
        product_manager_agent = self.client.beta.assistants.create(
            name = self.declare_product_manager(design_task)["name"],
            # description = product_manager["description"],
            instructions = self.declare_product_manager(design_task)["instructions"],
            model = self.model,
            tools = [{"type":"code_interpreter"}]
        )
        return product_manager_agent
    
    def updateProductManagerFor(self, whom, pm_agent, design_task, file_name_user_study_summary=None, file_name_business_analysis_summary=None, file_name_technical_analysis_summary=None, file_name_ethical_analysis_summary=None, file_name_design_analysis_summary=None):
        product_manager_agent = None

        user_study_summary = ""
        business_analysis_summary = ""
        technical_analysis_summary = ""
        ethical_analysis_summary = ""
        design_analysis_summary = ""
        
        if file_name_user_study_summary:
            with open(file_name_user_study_summary, "r") as file:
                user_study_summary = file.read()
        if file_name_business_analysis_summary:
            with open(file_name_business_analysis_summary, "r") as file:
                business_analysis_summary = file.read()
        if file_name_technical_analysis_summary:
            with open(file_name_technical_analysis_summary, "r") as file:
                technical_analysis_summary = file.read()
        if file_name_ethical_analysis_summary:
            with open(file_name_ethical_analysis_summary, "r") as file:
                ethical_analysis_summary = file.read()
        if file_name_design_analysis_summary:
            with open(file_name_design_analysis_summary, "r") as file:
                design_analysis_summary = file.read()
        
        if whom == "Business Analyst":
            product_manager_agent = self.client.beta.assistants.update(
                assistant_id = pm_agent.id,
                instructions = self.update_product_manager_for_business_analysis(design_task, user_study_summary, business_analysis_summary, technical_analysis_summary, ethical_analysis_summary, design_analysis_summary)["instructions"],
            )
        elif whom == "Ethics Advisor":
            product_manager_agent = self.client.beta.assistants.update(
                assistant_id = pm_agent.id,
                instructions = self.update_product_manager_for_ethics_advisor(design_task, user_study_summary, business_analysis_summary, technical_analysis_summary, ethical_analysis_summary, design_analysis_summary)["instructions"],
            )
        elif whom == "Developer":
            product_manager_agent = self.client.beta.assistants.update(
                assistant_id = pm_agent.id,
                instructions = self.update_product_manager_for_developer(design_task, user_study_summary, business_analysis_summary, technical_analysis_summary, ethical_analysis_summary, design_analysis_summary)["instructions"],
            )
        elif whom == "Interaction Designer":
            product_manager_agent = self.client.beta.assistants.update(
                assistant_id = pm_agent.id,
                instructions = self.update_product_manager_for_interaction_designer(design_task, user_study_summary, business_analysis_summary, technical_analysis_summary, ethical_analysis_summary, design_analysis_summary)["instructions"],
            )
        elif whom == "Client":
            product_manager_agent = self.client.beta.assistants.update(
                assistant_id = pm_agent.id,
                instructions = self.update_product_manager_for_client(design_task, user_study_summary, business_analysis_summary, technical_analysis_summary, ethical_analysis_summary, design_analysis_summary)["instructions"],
            )
        return product_manager_agent
    
    
    
    def createDeveloperAgent(self, design_task, file_name_user_study_summary=None, file_name_business_analysis_summary=None, file_name_technical_analysis_summary=None, file_name_ethical_analysis_summary=None, file_name_design_analysis_summary=None):
        user_study_summary = ""
        business_analysis_summary = ""
        technical_analysis_summary = ""
        ethical_analysis_summary = ""
        design_analysis_summary = ""
        
        if file_name_user_study_summary:
            with open(file_name_user_study_summary, "r") as file:
                user_study_summary = file.read()
        if file_name_business_analysis_summary:
            with open(file_name_business_analysis_summary, "r") as file:
                business_analysis_summary = file.read()
        if file_name_technical_analysis_summary:
            with open(file_name_technical_analysis_summary, "r") as file:
                technical_analysis_summary = file.read()
        if file_name_ethical_analysis_summary:
            with open(file_name_ethical_analysis_summary, "r") as file:
                ethical_analysis_summary = file.read()
        if file_name_design_analysis_summary:
            with open(file_name_design_analysis_summary, "r") as file:
                design_analysis_summary = file.read()
        
        developer_info = self.declare_developer(design_task, user_study_summary, business_analysis_summary, technical_analysis_summary, ethical_analysis_summary, design_analysis_summary)

        developer_agent = self.client.beta.assistants.create(
            name = developer_info["name"],
            # description = developer["description"],
            instructions = developer_info["instructions"],
            model = self.model,
            tools = [{"type":"code_interpreter"}]
        )
        return developer_agent
    
    def createBusinessAnalystAgent(self, design_task, file_name_user_study_summary=None, file_name_business_analysis_summary=None, file_name_technical_analysis_summary=None, file_name_ethical_analysis_summary=None, file_name_design_analysis_summary=None):
        user_study_summary = ""
        business_analysis_summary = ""
        technical_analysis_summary = ""
        ethical_analysis_summary = ""
        design_analysis_summary = ""

        if file_name_user_study_summary:
            with open(file_name_user_study_summary, "r") as file:
                user_study_summary = file.read()
        if file_name_business_analysis_summary:
            with open(file_name_business_analysis_summary, "r") as file:
                business_analysis_summary = file.read()
        if file_name_technical_analysis_summary:
            with open(file_name_technical_analysis_summary, "r") as file:
                technical_analysis_summary = file.read()
        if file_name_ethical_analysis_summary:
            with open(file_name_ethical_analysis_summary, "r") as file:
                ethical_analysis_summary = file.read()
        if file_name_design_analysis_summary:
            with open(file_name_design_analysis_summary, "r") as file:
                design_analysis_summary = file.read()

        business_analyst_info = self.declare_business_analyst(design_task, user_study_summary, business_analysis_summary, technical_analysis_summary, ethical_analysis_summary, design_analysis_summary)
        
        business_analyst_agent = self.client.beta.assistants.create(
            name = business_analyst_info["name"],
            # description = business_analyst["description"],
            instructions = business_analyst_info["instructions"],
            model = self.model,
            tools = [{"type":"code_interpreter"}]
        )
        return business_analyst_agent
    
    def createEthicsAdvisorAgent(self, design_task, file_name_user_study_summary=None, file_name_business_analysis_summary=None, file_name_technical_analysis_summary=None, file_name_ethical_analysis_summary=None, file_name_design_analysis_summary=None):
        user_study_summary = ""
        business_analysis_summary = ""
        technical_analysis_summary = ""
        ethical_analysis_summary = ""
        design_analysis_summary = ""

        if file_name_user_study_summary:
            with open(file_name_user_study_summary, "r") as file:
                user_study_summary = file.read()
        if file_name_business_analysis_summary:
            with open(file_name_business_analysis_summary, "r") as file:
                business_analysis_summary = file.read()
        if file_name_technical_analysis_summary:
            with open(file_name_technical_analysis_summary, "r") as file:
                technical_analysis_summary = file.read()
        if file_name_ethical_analysis_summary:
            with open(file_name_ethical_analysis_summary, "r") as file:
                ethical_analysis_summary = file.read()
        if file_name_design_analysis_summary:
            with open(file_name_design_analysis_summary, "r") as file:
                design_analysis_summary = file.read()

        ethics_advisor_info = self.declare_ethics_advisor(design_task, user_study_summary, business_analysis_summary, technical_analysis_summary, ethical_analysis_summary, design_analysis_summary)
        
        ethics_advisor_agent = self.client.beta.assistants.create(
            name = ethics_advisor_info["name"],
            # description = ethics_advisor["description"],
            instructions = ethics_advisor_info["instructions"],
            model = self.model,
            tools = [{"type":"code_interpreter"}]
        )

        return ethics_advisor_agent
    
    def createInteractionDesignerAgent(self, design_task, file_name_user_study_summary=None, file_name_business_analysis_summary=None, file_name_technical_analysis_summary=None, file_name_ethical_analysis_summary=None, file_name_design_analysis_summary=None):
        user_study_summary = ""
        business_analysis_summary = ""
        technical_analysis_summary = ""
        ethical_analysis_summary = ""
        design_analysis_summary = ""

        if file_name_user_study_summary:
            with open(file_name_user_study_summary, "r") as file:
                user_study_summary = file.read()
        if file_name_business_analysis_summary:
            with open(file_name_business_analysis_summary, "r") as file:
                business_analysis_summary = file.read()
        if file_name_technical_analysis_summary:
            with open(file_name_technical_analysis_summary, "r") as file:
                technical_analysis_summary = file.read()
        if file_name_ethical_analysis_summary:
            with open(file_name_ethical_analysis_summary, "r") as file:
                ethical_analysis_summary = file.read()
        if file_name_design_analysis_summary:
            with open(file_name_design_analysis_summary, "r") as file:
                design_analysis_summary = file.read()

        interaction_designer_info = self.declare_interaction_designer(design_task, user_study_summary, business_analysis_summary, technical_analysis_summary, ethical_analysis_summary, design_analysis_summary)
        
        interaction_designer_agent = self.client.beta.assistants.create(
            name = interaction_designer_info["name"],
            # description = ethics_advisor["description"],
            instructions = interaction_designer_info["instructions"],
            model = self.model,
            tools = [{"type":"code_interpreter"}]
        )

        return interaction_designer_agent

    