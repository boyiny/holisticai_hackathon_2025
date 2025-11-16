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
    If you don't know the answer, please say you don't know and give practical suggestions about what I can do to solve it. \
    You never repeat or rephrase what I say! \
    You never ask me questions or repeat my questions! \

    I must give you one or a few interview questions at a time. You must answer all questions. \
    You don't need to agree with me. You should provide your own perspective and insights. \
    You must write specific answers that are critical and insightful for the <DESIGN_TASK>. \
    
    <YOUR_REPLY> should be specific, and provide critical and insightful information that reflects your characteristic and identity. \
    Always end <YOUR_REPLY> with: 
    
    Please let me know if you have further questions.
    
    Do not add anything else other than your reply to my questions! \
    Keep giving me detailed and insightful answers. \
"""


hcd_techniques_for_user_researcher = """
    1. You must ask me open-ended questions to understand my goals, needs, and preferences. \
    2. You must ask me how do I handle the current situation and tools and rescources I used if there are any.
    3. You must ask me about my current pain points, experiences, and challenges to understand my true needs. \
    3. You must ask me about the use scenarios to understand my context of use and who else may be involved. \
    4. You must ask me to understand my emotions, concerns, thoughts, and behaviors. \
    5. You can ask follow-up questions to gather more information. \
    6. You can ask me questions about ideas around a central concept. \
    7. You can ask me narrative questions to understand my stories, and motivations.\
    8. If I mentioned a previous experience, you must ask me to elaborate on it. \
    9. If I mentioned some products, you must ask me to explain why it works or doesn't work for me. \
    10. If I mentioned some features, you must ask me to explain why I like or dislike them. \
    11. You must avoid leading questions that may influence my answers. \
    12. You must avoid asking specific system features or solutions I want. 
"""

hcd_perspectives_for_product_manager = """
    1. Objective facts and numbers \
    2. Emotions \
    3. Negative aspects \
    4. Optimal and positive thoughts \
    5. Creativity and ideas \
    6. The control and organization of the thought process. 
"""

hcd_techniques_for_product_manager = """
    1. You can ask me follow-up questions to gather more information. \
    2. You can ask me questions about ideas around a central concept. \
    3. If I mentioned a solution, you must ask me to elaborate on it. \
    4. You must avoid leading questions that may influence my answers. \
    5. You must finish the conversation by encouraging me to answer your questions. 
"""

# prd_instructions = """
#     1. The PRD should indicate the market size, market value, user value, business value, unique selling points, ethical consideration, and technical implimentation of the product features in detail based on all <INFORMATION> provided. \
#     2. The PRD should clearly indicate the system boundries and list all product features in detail and link them with user/business/ethical requirements. \
#     3. The PRD should specifiy executable technical implimentation guidelines to the product features in detail so that even for junior developers can carry out the task. \
#     4. The PRD should be detailed and executable so that the team can understand the product features and their implications so that even for a junior team can carry out the whole task. \
#     5. The PRD should also include the timeline, budget, success metrics, and other relevant information for each each role in the team: product manager, user researcher, interaction designer, business analyst, ethics advisor, and developer, as well as the whole team. \
#     6. The PRD should be written in a professional and clear language.
# """

prd_instructions = """
The Product Requirements Document (PRD) should based on all <INFORMATION> provided above and include the following sections in detail:

1. Overview: A brief description of the product, feature, or update. Include the key problem it solves or the primary goals.
Requirements: Clear and concise. Describe what problem the product solves and how it aligns with the business strategy in a few paragraphs. It should be inspirational but not overly technical.

2. Objectives and Goals
Product Vision: A high-level vision of what the product will achieve and how it aligns with the company's strategic goals.
Objectives: What specific business or user problems does this product aim to solve?
Success Metrics: How will success be measured? (KPIs, user engagement, revenue targets, etc.)
Reuirements: Semi-detailed. Provide measurable goals, so the team knows what to aim for.

3. Scope and Features
Feature List: Detailed list of all features or functionalities that the product will include. Prioritize features as "must-have," "nice-to-have," and "optional."
Feature Descriptions: For each feature, explain its purpose, how it works, and how it benefits the user.
Non-Features: Clarify what will not be included to manage expectations.
Requirements: Detailed. For each key feature, include a detailed description of how it works, its dependencies, and its impact on users. Lower-priority features can have lighter descriptions, to be filled in during later phases. You should organize features by priority. These features should be linked to objectives and goals.

4. User Stories or Use Cases
User Personas: Define the target users (e.g., type of user, industry).
User Stories: Describe how the user will interact with the product (e.g., "As a [persona], I want to [goal], so that [benefit].")
Use Cases: Detailed scenarios in which users would use the product.
Requirements: Detailed. Write specific user stories for all key user actions. These should reflect the objectives and goals of the product and be written from the user's perspective.

5. Assumptions and Constraints
Assumptions: What assumptions are being made about users, technology, market conditions, etc.?
Constraints: Any technical, business, or legal limitations that could affect the product.
Requirements: Detailed. List all assumptions and constraints that could impact development.


6. Conceptual Design
Visual Description: A description of system architecture, user interface, and any other visual elements.
UI/UX Guidelines: Outline key design principles, branding guidelines, and any user experience considerations.
Requirements: Semi-detailed. Provide a high-level overview of the product's design and user experience.

8. Technical Specifications
Architecture: High-level technical architecture of the product, explaining how systems will integrate.
APIs: If applicable, describe required APIs and how they will function.
Tech Stack: Identify any technology platforms, frameworks, or tools needed for development.
Requirements: As detailed as necessary. Highly detailed if technical complexity is high, but focus on critical parts if the technology is straightforward. If the product involves API integrations, define how APIs should work, what data will be exchanged, and security considerations.

9. Risks and Mitigation
Risks: Identify potential risks (e.g., technical, market, or time-based risks).
Mitigation Plans: Strategies to address these risks.
Requirements: Semi-detailed, highlighting key risks and dependencies. Identify major risks (e.g., technical or market risks) without getting bogged down in minutiae.

10. Timeline and Milestones
Development Timeline: Estimated time for each phase (design, development, testing, deployment).
Milestones: Key milestones such as MVP, beta launch, final release, etc.
Requirements: Present a detailed timelines with detail major milestones. Give a realistic sense of the development timeline but leave room for flexibility, especially in Agile environments.

11. Testing and Validation
Testing Plan: How will the product be tested? Include unit tests, user acceptance testing (UAT), and beta testing plans.
Feedback Loops: How will user feedback be collected and incorporated?
Requirements: Detailed. Outline the testing process, including the success metrics of each system feature, what tools will be used, and how feedback will be collected and addressed. Include a testing matrix with unit tests, UAT, and edge cases to be covered, especially for high-risk areas of the product.

12. Maintenance and Support
Post-Launch Support: Describe how the product will be maintained and supported after launch (e.g., bug fixes, performance improvements).
Version Control: How updates and new versions will be rolled out.
Requirements: High-level, but provide sufficient clarity for support planning. Make sure the team understands what post-launch maintenance looks like without going into exhaustive detail.

13. Stakeholders
List of Stakeholders: Identify key people who need to approve or provide input (e.g., product manager, engineering lead, marketing, etc.).
Roles and Responsibilities: Clarify roles within the project team.
Requirements: Semi-detailed. Provide stakeholders and their roles mentioned in the <INFORMATION> material, but don't get bogged down in organizational details.
"""







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
            You must ask me questions to my experience, requirements, expectations, and preferences to get context information and insights for the <DESIGN_TASK>. \
            Here is the <DESIGN_TASK>: {design_task}. Never forget the design task! \
            
            We share a common interest in collaborating to successfully understand my goals, needs, expections, preferences, and all context information. \
            You should ask me multiple questions at a time. You can ask me follow-up questions to gather more information. \
            You must keep asking me necessary questions to understand my motivation, goals, challenges, needs and relavent context information in detail.  \
            You should ask me how much I would pay for the product, what are my expectations, and what are my preferences. \
            Here are some human-centered design (HCD) techniques you should use to gather insights from me: {hcd_techniques_for_user_researcher}  \
            
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
            
            Never forget you are telling me your experience and needs based on your persona, which are relevant to the <DESIGN_TASK>. \
            Here is the <DESIGN_TASK> {design_task} </DESIGN_TASK>. 

            We share a common interest in collaborating to successfully understand your needs, expections, preferences, and all context information. \
            Your answers should be vivid, detailed, and specific to your persona. \
            Your answer must reflect your persona's characteristic and identity. \
            You must use a natural language style that is relevant to your persona. \
            
            {general_instructions_for_answering_questions}
            """
        }
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
            You may ask multiple questions to one team member at a time. 
            You must keep asking necessary questions.
            If you think one aspect is well discussed, you can switch to a new relevant topic and ask new questions. \
            You must look at a problem from multiple perspectives: {hcd_perspectives_for_product_manager}
            Here are some interview techniques you should use to gather insights from me: {hcd_techniques_for_product_manager}
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
            <INFORMATION>
            {text_user_study_summary} 
            {text_business_analysis}
            {text_ethical_analysis}
            {text_technical_analysis}
            {text_design_analysis}
            </INFORMATION>

            We share a common interest in collaborating to successfully understand the current market size, the market gaps, how can this product make profit, what are the competitors and other relevant questions about business. \
            Your questions should be focused on making unique business insights, understanding the market size, the market gaps, the competitors, and the business goals based on the <INFORMATION> provided. \
            You shouldn't ask me about technical feasbility, ethical risks, interaction design, or user experience design. \
            Your should ask me multiple questions at a time. You should ask me follow-up questions to gather in-depth information. \
            You must keep asking necessary questions. If you think one business aspect is well discussed, you can switch to a new business topic and ask new questions. \
            You must look at a problem from multiple perspectives: {hcd_perspectives_for_product_manager} \
            Here are some interview techniques you should use to gather insights from me: {hcd_techniques_for_product_manager}
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
            <INFORMATION>
            {text_user_study_summary} 
            {text_business_analysis}
            {text_ethical_analysis}
            {text_technical_analysis}
            {text_design_analysis}
            </INFORMATION>

            We share a common interest in collaborating to successfully understand what are the potential ethical risks of our product, how can we handle the ethical risks of our product, and other relevant questions about ethics. \
            Your questions should be focused on the ethical risks, specific regulation rules, implications, and considerations of the product features based on the <INFORMATION> provided. \
            You shouldn't ask me about technical feasbility, business insights, interaction design, or user experience design. \
            Your should ask me multiple questions at a time. You can ask me follow-up questions to gather more information. \
            You must keep asking necessary questions. If you think one ethical aspect is well discussed, you can switch to a new ethical topic and ask new questions. \
            You must look at a problem from multiple perspectives: {hcd_perspectives_for_product_manager} \
            Here are some interview techniques you should use to gather insights from me: {hcd_techniques_for_product_manager}
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
            <INFORMATION>
            {text_user_study_summary} 
            {text_business_analysis}
            {text_ethical_analysis}
            {text_technical_analysis}
            {text_design_analysis}
            </INFORMATION>

            We share a common interest in collaborating to successfully understand the technical requirements, implimentations, and constraints of the product features. \
            Your questions should be focused on the technical feasbility and implimentation of the product features based on the <INFORMATION> provided. \
            You shouldn't ask me about business insights, ethical risks, interaction design, or user experience design. \
            Your may ask me multiple questions at a time. You can ask me follow-up questions to gather more information. \
            You must keep asking necessary questions. If you think one technical aspect is well discussed, you can switch to a new technical topic and ask new questions. \
            You must look at a problem from multiple perspectives: {hcd_perspectives_for_product_manager} \
            Here are some interview techniques you should use to gather insights from me: {hcd_techniques_for_product_manager}
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
            Never forget you are a <PRODUCT_MANAGER> and I am an <INTERACTION_DESIGNER>. Never flip roles! Never repeat what I say! You must keep asking me questions to understand the system design of the <DESIGN_TASK> based on the information provided below: 
            Here is the <DESIGN_TASK>: {design_task}. Never forget the design task! 
            <INFORMATION>
            {text_user_study_summary} 
            {text_business_analysis}
            {text_ethical_analysis}
            {text_technical_analysis}
            {text_design_analysis}
            </INFORMATION>

            We share a common interest in collaborating to successfully design a creative, enjoyable, effecient, effective, and user-friendly product that meets all essential needs mentioned in the provided information. \
            Your questions should be focused on aspects that associate to creative system features, core system features, interaction design, and user experience design based on all <INFORMATION> provided. \
            You shouldn't ask me about business insights, ethical risks, technical feasbility, or user needs. \
            Your should ask me multiple questions at a time. You can ask me follow-up questions to gather more information. \
            You must keep asking necessary questions. If you think one design aspect is well discussed, you can switch to a new design topic and ask new questions. \
            You must look at a problem from multiple perspectives: {hcd_perspectives_for_product_manager} \
            Here are some interview techniques you should use to gather insights from me: {hcd_techniques_for_product_manager}
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
            Never forget you are a <PRODUCT_MANAGER>. You need to write a detailed Product Requirements Document (PRD) based on the information provided below:
            Here is the <DESIGN_TASK>: {design_task}. Never forget the design task! 
            <INFORMATION>
            {text_user_study_summary} 
            {text_business_analysis}
            {text_ethical_analysis}
            {text_technical_analysis}
            {text_design_analysis}
            </INFORMATION>

            You must compose the report based on the instructions provided below: 
            {prd_instructions}
            """
        }
        # The PRD should point out the market value, user value, business value, ethical consideration, and technical implimentation of the product features. \
        # The roles in the team are user researcher, interaction designer, business analyst, ethics advisor, and developer.
        # The PRD should list all product features in detail and link them with user/business/ethical requirements. \

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
            Never forget you are helping me to conduct a system design for the <DESIGN_TASK>. \
            Here is the <DESIGN_TASK>: {design_task}. Never forget the design task! \
            You only focus on aspects that associate to creative system features, core system features, interaction design, and user experience design. \
            Your answer must be creative, detailed, and specific. \
            You should suggest several interaction solutions for each system feature, depending on the feature types, it can be from high engagement to low engagement, or from high entertainment to low entertainment, or from high professional to low professional, or from high tech to low tech, etc. \
            For each interaction solution, you should indicate how users can benefit from it, what are the constraints, and what are the requirements. \
            If you don't know the answer, please say you don't know and give practical suggestions about what I can do to solve it. \
            Never forget we share a common interest in collaborating to successfully design a product that meets all essential requirements from the information provided below: 
            {text_user_study_summary}
            {text_business_analysis} 
            {text_ethical_analysis} 
            {text_technical_analysis} 
            {text_design_analysis}

            We share a common interest in collaborating to successfully design a creative, effecient, effective, and user-friendly product that meets all essential needs mentioned in the provided information. \
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
            You only focus on aspects that associate to business. Your answer must be critical, detailed, and specific. If you don't know the answer, please say you don't know and give practical suggestions about what I can do to solve it.\
            Your solution should highlight the unique selling points, how can this product provide value to users that competitors can't, and how can this product make profit. \
            You should regard each user as a representitive of a user group, and you should analyze the business insights based on the user group. \
            You should compare different user needs and propose unique selling points for each user group. \
            You should provide your analysis about whether to include all user groups or only some user groups, as well as the user needs. \
            You should provide solutions on how to promote the product to different user groups. \
            If you provide specific market data, you should annotate the data source and explain how this data is calculated (e.g., from customer side or from supplier side or some other approaches). \
            You always answer my questions about your business insights that are relevant to the information provided below:
            Here is the <DESIGN_TASK> {design_task} </DESIGN_TASK>. 
            {text_user_study_summary}
            {text_business_analysis}
            {text_technical_analysis} 
            {text_ethical_analysis} 
            {text_design_analysis}

            We share a common interest in collaborating to successfully understand the current market size, the market gaps, what are the competitors, our selling points, how can this product make profit, and other relevant questions about business. \
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
            You only focus on aspects that associate to ethics. Your answer must be critival, detailed, and specific. If you don't know the answer, please say you don't know and give practical suggestions about what I can do to solve it.\
            When you suggest a solution, you must provide specific regulations that support your solution. \
            You shouldn't over exaggerate the ethical risks. \
            You need to justifty the level of ethical risks and how to handle them and the cost of handling or not handling them. \
            You always answer my questions about your ethical advices that are relevant to the information provided below:
            Here is the <DESIGN_TASK> {design_task} </DESIGN_TASK>. 
            {text_user_study_summary}
            {text_business_analysis} 
            {text_technical_analysis} 
            {text_ethical_analysis}
            {text_design_analysis}

            We share a common interest in collaborating to successfully understand what are the potential ethical risks of our product, how can we handle the ethical risks of our product, the specific regulations we need to comply with, and other relevant questions about ethics. \
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
            You only focus on aspects that associate to technology implimentation and feasibility. Your answer must be detailed and specific. If you don't know the answer, please say you don't know and give practical suggestions about what I can do to solve it.\
            You should suggest several technical solutions for each system feature, depending on the feature types, it can be from high automation to low automation, or from high entertainment to low entertainment, or from high tech to low tech, etc. \
            If your technical solution requires AI models, you must provide several AI models, as well as its paper or document that supports your solution. \
            If your technical solution requires a specific technology, you must provide severl specific technology options (e.g., algorithms, models, libraries, frameworks, system architecture, proggramming languages, etc.) that supports your solution. \
            For each technical solution, you should indicate how to impliment it, what are the costs, benefits, constraints, and requirements. \
            You always answer my questions about technical implimentation and feasbility that are relevant to the information provided below: 
            Here is the <DESIGN_TASK> {design_task} </DESIGN_TASK>. 
            {text_user_study_summary} 
            {text_business_analysis} 
            {text_ethical_analysis} 
            {text_technical_analysis}
            {text_design_analysis}

            We share a common interest in collaborating to successfully understand the technical implimentation, requirements, and constraints of the product features. \
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
    
    def updateProductManagerFor(self, whom, pm_agent, design_task, file_name_user_study_summary_list=None, file_name_business_analysis_summary=None, file_name_technical_analysis_summary=None, file_name_ethical_analysis_summary=None, file_name_design_analysis_summary=None):
        product_manager_agent = None

        user_study_summary = ""
        business_analysis_summary = ""
        technical_analysis_summary = ""
        ethical_analysis_summary = ""
        design_analysis_summary = ""
        
        if file_name_user_study_summary_list:
            for file_name_user_study_summary in file_name_user_study_summary_list:
                with open(file_name_user_study_summary, "r") as file:
                    user_study_summary += file.read()
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
    
    
    
    def createDeveloperAgent(self, design_task, file_name_user_study_summary_list=None, file_name_business_analysis_summary=None, file_name_technical_analysis_summary=None, file_name_ethical_analysis_summary=None, file_name_design_analysis_summary=None):
        user_study_summary = ""
        business_analysis_summary = ""
        technical_analysis_summary = ""
        ethical_analysis_summary = ""
        design_analysis_summary = ""
        
        if file_name_user_study_summary_list:
            for file_name_user_study_summary in file_name_user_study_summary_list:
                with open(file_name_user_study_summary, "r") as file:
                    user_study_summary += file.read()
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
    
    def createBusinessAnalystAgent(self, design_task, file_name_user_study_summary_list=None, file_name_business_analysis_summary=None, file_name_technical_analysis_summary=None, file_name_ethical_analysis_summary=None, file_name_design_analysis_summary=None):
        user_study_summary = ""
        business_analysis_summary = ""
        technical_analysis_summary = ""
        ethical_analysis_summary = ""
        design_analysis_summary = ""

        if file_name_user_study_summary_list:
            for file_name_user_study_summary in file_name_user_study_summary_list:
                with open(file_name_user_study_summary, "r") as file:
                    user_study_summary += file.read()
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
    
    def createEthicsAdvisorAgent(self, design_task, file_name_user_study_summary_list=None, file_name_business_analysis_summary=None, file_name_technical_analysis_summary=None, file_name_ethical_analysis_summary=None, file_name_design_analysis_summary=None):
        user_study_summary = ""
        business_analysis_summary = ""
        technical_analysis_summary = ""
        ethical_analysis_summary = ""
        design_analysis_summary = ""

        if file_name_user_study_summary_list:
            for file_name_user_study_summary in file_name_user_study_summary_list:
                with open(file_name_user_study_summary, "r") as file:
                    user_study_summary += file.read()
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
    
    def createInteractionDesignerAgent(self, design_task, file_name_user_study_summary_list=None, file_name_business_analysis_summary=None, file_name_technical_analysis_summary=None, file_name_ethical_analysis_summary=None, file_name_design_analysis_summary=None):
        user_study_summary = ""
        business_analysis_summary = ""
        technical_analysis_summary = ""
        ethical_analysis_summary = ""
        design_analysis_summary = ""

        if file_name_user_study_summary_list:
            for file_name_user_study_summary in file_name_user_study_summary_list:
                with open(file_name_user_study_summary, "r") as file:
                    user_study_summary += file.read()
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

    def getSummaryPrompt(self, design_task, design_event):
        summary_prompt = f"You are a <PRODUCT_MANAGER>. Please provide a detailed summary of the user study conversation from the txt file. This summary should be insightful for the <DESIGN_TASK>: {design_task}. Only reply the summay. Do not add anything else!"
        if design_event == "GATHER_USER_NEEDS":
            summary_prompt = f"""
            You are a <PRODUCT_MANAGER>. Please provide a detailed report of the user study conversation from the txt file. \
            You should capture the user needs, user goals, user pain points, user preferences, user expectations, and all relevant user information mentioned in the document. \
            You should highlight the user attempts and challenges. \
            If the user mentioned any failure or success, you should capture the failure or success details and avoid generalization. \
            You should capture the details and avoid generalization. \
            Only reply the report. Do not add anything else!
            """
        elif design_event == "GATHER_BUSINESS_ANALYSIS":
            summary_prompt = f"""
            You are a <PRODUCT_MANAGER>. Please provide a detailed report of the business analysis conversation from the txt file. \
            This report should be insightful for the <DESIGN_TASK>: {design_task}. \
            You should address the market size, market gaps, competitors, selling points, business values, business risks, business opportunities, and all other relevant business information mentioned in the document. \
            You should capture all the details and avoid generalization. The report should be well organized. Don't be afraid of being long. \
            Only reply the report. Do not add anything else!
            """
        elif design_event == "GATHER_ETHICAL_ANALYSIS":
            summary_prompt = f"""
            You are a <PRODUCT_MANAGER>. Please provide a detailed report of the ethical analysis conversation from the txt file. \
            This report should be insightful for the <DESIGN_TASK>: {design_task}. \
            You should address the potential ethical risks, ethical considerations, ethical implications, ethical requirements, ethical regulations, and other relevant ethical information mentioned in the document. \
            You should capture all the details and avoid generalization. The report should be well organized. Don't be afraid of being long. \
            Only reply the report. Do not add anything else!
            """
        elif design_event == "GATHER_DESIGN_ANALYSIS":
            summary_prompt = f"""
            You are a <PRODUCT_MANAGER>. Please provide a detailed report of the design analysis conversation from the txt file. \
            This report should be insightful for the <DESIGN_TASK>: {design_task}. \
            You should address the creative system features, core system features, interaction design, user experience design, and other relevant design information mentioned in the document. \
            You should capture all the details and avoid generalization. The report should be well organized. Don't be afraid of being long. \
            Only reply the report. Do not add anything else!
            """
        elif design_event == "GATHER_TECHNICAL_ANALYSIS":
            summary_prompt = f"""
            You are a <PRODUCT_MANAGER>. Please provide a detailed report of the technical analysis conversation from the txt file. \
            This report should be insightful for the <DESIGN_TASK>: {design_task}. \
            You should address the technical feasbility, technical requirements, technical constraints, technical implimentations, and other relevant technical information mentioned in the document. \
            You should capture all the details and avoid generalization. The report should be well organized. Don't be afraid of being long. \
            Only reply the report. Do not add anything else!
            """

        return summary_prompt