import json
from langsmith import traceable

# General instructions for agent responses
general_instructions = """
You must answer questions based on your expertise to complete the task honestly and thoroughly.
You must provide specific, detailed answers that are insightful for creating a personalized longevity plan.
Your responses should be professional, empathetic, and data-driven.
Always end your responses with: "Please let me know if you have further questions or need clarification."
"""


class LongevityAgents:
    """
    Agent system for longevity health planning.
    Two primary agents:
    1. Customer Needs Agent - understands user health data, goals, and preferences
    2. Company Rules Agent - knows company services, policies, and scheduling
    """

    def __init__(self, client, model):
        self.client = client
        self.model = model
        self.conversation_history_file_name = None

    def declare_customer_needs_agent(self, user_data):
        """
        Agent that represents the customer's needs, wants, and health profile.
        Has deep knowledge of user's health metrics, goals, and constraints from long-term data collection.
        """
        customer_needs_agent = {
            "name": "Customer Health Advocate",
            "description": "Represents customer's health needs, goals, and preferences based on long-term health data",
            "instructions": f"""
            Never forget you are a <CUSTOMER_HEALTH_ADVOCATE> and I am a <COMPANY_SERVICE_ADVISOR>. Never flip roles!

            Your role is to represent the customer's health needs, preferences, and constraints to negotiate
            the best possible longevity plan and schedule body check appointments.

            Here is the comprehensive <USER_DATA> you have collected over time:
            {json.dumps(user_data, indent=2)}

            Your responsibilities:
            1. Advocate for services that align with the user's specific health goals and medical history
            2. Ensure recommendations are within the user's budget range (${user_data['preferences']['budget_range_monthly_usd']['min']}-${user_data['preferences']['budget_range_monthly_usd']['max']}/month)
            3. Prioritize evidence-based interventions that match user's preferences
            4. Consider user's time availability and scheduling constraints
            5. Flag any contraindications based on medical history
            6. Ensure dietary restrictions and preferences are accommodated
            7. Seek services that address the user's primary longevity goals: {', '.join(user_data['longevity_goals']['primary_goals'])}
            8. Consider the user's APOE genotype ({user_data['biomarkers_history']['notable_values']['apoe_genotype']}) in recommendations

            When discussing services, you should:
            - Ask clarifying questions about effectiveness and scientific evidence
            - Request scheduling options that match preferred times: {', '.join(user_data['availability']['preferred_appointment_times'])}
            - Ensure blocked dates are avoided: {', '.join(user_data['availability']['blocked_dates'])}
            - Negotiate for comprehensive packages that provide good value
            - Ask about success rates and expected outcomes
            - Verify that all recommendations are safe given medical history

            Communication style: {user_data['preferences']['communication_style']} - emphasize data and evidence

            {general_instructions}

            You are working together to create an optimal 6-month longevity plan with specific appointments scheduled.
            """
        }
        return customer_needs_agent

    def declare_company_rules_agent(self, company_resources):
        """
        Agent that knows all company services, policies, scheduling rules, and constraints.
        Expert in available treatments, pricing, evidence basis, and booking procedures.
        """
        company_rules_agent = {
            "name": "Company Service Advisor",
            "description": "Expert in company services, policies, and scheduling with deep knowledge of longevity interventions",
            "instructions": f"""
            Never forget you are a <COMPANY_SERVICE_ADVISOR> and I am a <CUSTOMER_HEALTH_ADVOCATE>. Never flip roles!

            Your role is to recommend appropriate longevity services, explain company policies,
            and help schedule body checks and treatments based on company resources and medical guidelines.

            Here are the complete <COMPANY_RESOURCES> you must follow:
            {company_resources}

            Your responsibilities:
            1. Recommend evidence-based services that match the customer's health profile
            2. Explain the scientific rationale and expected outcomes for each intervention
            3. Provide accurate pricing and package options
            4. Check eligibility and contraindications for all services
            5. Offer scheduling options that comply with company availability
            6. Explain policies clearly (booking, cancellation, payment)
            7. Suggest comprehensive programs when appropriate for better outcomes and value
            8. Ensure all recommendations meet scientific standards outlined in company policy
            9. Flag any safety concerns or required baseline testing
            10. Provide realistic timelines and frequency recommendations

            When making recommendations, you should:
            - Start with services most aligned with customer's primary health concerns
            - Explain the evidence basis for each recommendation (RCT data, observational studies, etc.)
            - Provide specific appointment time options from available slots
            - Offer package deals and memberships when they provide value
            - Be transparent about what insurance may/may not cover
            - Explain monitoring requirements for ongoing treatments
            - Suggest appropriate testing frequency based on health status

            Important constraints you must follow:
            - Only recommend services that meet company's evidence standards
            - Do not book blackout dates
            - Ensure advance booking requirements are met (7 days for assessments, 3 days for follow-ups)
            - Verify baseline testing requirements are satisfied
            - Check for contraindications before recommending any therapy
            - Stay within scope of company offerings (no unapproved treatments)

            {general_instructions}

            You are working together to create an optimal 6-month longevity plan with specific appointments scheduled.
            Be helpful, knowledgeable, and ensure all recommendations are safe and evidence-based.
            """
        }
        return company_rules_agent

    @traceable
    def create_customer_needs_agent(self, user_data):
        """Create OpenAI assistant for customer needs agent"""
        agent_config = self.declare_customer_needs_agent(user_data)
        agent = self.client.beta.assistants.create(
            name=agent_config["name"],
            instructions=agent_config["instructions"],
            model=self.model,
            tools=[{"type": "code_interpreter"}]
        )
        return agent

    def create_company_rules_agent(self, company_resources):
        """Create OpenAI assistant for company rules agent"""
        agent_config = self.declare_company_rules_agent(company_resources)
        agent = self.client.beta.assistants.create(
            name=agent_config["name"],
            instructions=agent_config["instructions"],
            model=self.model,
            tools=[{"type": "code_interpreter"}]
        )
        return agent

    def get_summary_prompt(self):
        """Generate prompt for summarizing the conversation into a longevity plan"""
        summary_prompt = """
        You are a medical coordinator summarizing a conversation between a customer health advocate
        and a company service advisor.

        Please provide a comprehensive LONGEVITY PLAN SUMMARY that includes:

        1. RECOMMENDED SERVICES & INTERVENTIONS
           - List all agreed-upon services, tests, and therapies
           - Include scientific rationale for each
           - Note expected outcomes and success metrics

        2. SCHEDULED APPOINTMENTS
           - Specific dates and times for all body checks and assessments
           - List of follow-up appointments
           - Testing schedule (quarterly, semi-annual, etc.)

        3. MONTHLY BREAKDOWN
           - Services scheduled for each month (Month 1-6)
           - Estimated costs per month
           - Monitoring and check-in schedule

        4. TOTAL INVESTMENT
           - 6-month total cost
           - Average monthly cost
           - Payment structure (upfront, monthly, etc.)

        5. HEALTH GOALS ADDRESSED
           - How each service addresses specific customer goals
           - Expected timeline for improvements

        6. SAFETY CONSIDERATIONS
           - Any contraindications noted
           - Required baseline testing
           - Monitoring requirements

        7. NEXT STEPS
           - Immediate action items
           - Required preparations before first appointment
           - Portal registration and documentation needed

        Format the summary in a clear, organized manner. Only provide the summary, nothing else.
        """
        return summary_prompt
