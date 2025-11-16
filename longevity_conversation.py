from openai import OpenAI
import os
from os.path import join, dirname
from dotenv import load_dotenv
from datetime import datetime
import json
import requests

from longevity_agents import LongevityAgents

# Configuration
CONVERSATION_TURN_LIMIT = 10  # 10 turns of back-and-forth conversation


class LongevityConversationSystem:
    """
    Multi-turn conversation system for longevity planning.
    Facilitates dialogue between Customer Needs Agent and Company Rules Agent
    to create personalized longevity plans and schedule body checks.
    Integrates with Valyu server for scientific validity checking.
    """

    def __init__(self):
        # Load environment variables
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY_1")
        self.model = "gpt-4o-mini"
        self.client = OpenAI(api_key=OPENAI_API_KEY)

        # Valyu MCP server configuration
        self.valyu_enabled = True  # Set to False if Valyu is not available
        self.valyu_base_url = "http://localhost:3000"  # Adjust based on Valyu MCP server setup

        # Initialize agents system
        self.longevity_agents = LongevityAgents(client=self.client, model=self.model)

        # Agent instances
        self.customer_agent = None
        self.company_agent = None

        # Conversation thread
        self.conversation_thread = None

        # Create output directory
        current_time = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_folder = f"data/longevity_plan_{current_time}"
        os.makedirs(self.output_folder, exist_ok=True)

        # Output files
        self.conversation_history_file = f"{self.output_folder}/conversation_history.txt"
        self.plan_summary_file = f"{self.output_folder}/longevity_plan_summary.txt"
        self.validity_check_file = f"{self.output_folder}/scientific_validity_checks.json"

        # Initialize files
        with open(self.conversation_history_file, 'w') as f:
            f.write(f"Longevity Planning Conversation\n")
            f.write(f"Started: {datetime.now()}\n")
            f.write("=" * 80 + "\n\n")

        # Validity checks storage
        self.validity_checks = []

    def load_user_data(self):
        """Load user information from JSON file"""
        with open('user_info.json', 'r') as f:
            user_data = json.load(f)
        return user_data

    def load_company_resources(self):
        """Load company resources from text file"""
        with open('company_resource.txt', 'r') as f:
            company_resources = f.read()
        return company_resources

    def check_scientific_validity_with_valyu(self, claim, context):
        """
        Check scientific validity of a claim using Valyu MCP server.

        Args:
            claim: The scientific claim to validate
            context: Additional context about the claim

        Returns:
            dict: Validation result with evidence and confidence
        """
        if not self.valyu_enabled:
            return {
                "valid": True,
                "confidence": "not_checked",
                "evidence": "Valyu validation not enabled",
                "sources": []
            }

        try:
            # Call Valyu MCP server to validate the claim
            # Note: Adjust endpoint based on actual Valyu API
            response = requests.post(
                f"{self.valyu_base_url}/validate",
                json={
                    "claim": claim,
                    "context": context,
                    "domain": "longevity_medicine"
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result
            else:
                return {
                    "valid": "unknown",
                    "confidence": "error",
                    "evidence": f"Valyu server error: {response.status_code}",
                    "sources": []
                }

        except requests.exceptions.RequestException as e:
            # Valyu server not available - log but continue
            print(f"Warning: Valyu validation unavailable: {e}")
            return {
                "valid": "unknown",
                "confidence": "server_unavailable",
                "evidence": str(e),
                "sources": []
            }

    def log_conversation(self, role, message):
        """Log conversation to file"""
        with open(self.conversation_history_file, 'a') as f:
            f.write(f"\n{datetime.now().strftime('%H:%M:%S')} - {role}:\n")
            f.write("-" * 80 + "\n")
            f.write(f"{message}\n")
            f.write("=" * 80 + "\n")

    def extract_claims_for_validation(self, message):
        """
        Extract scientific claims from agent messages that should be validated.
        Uses simple heuristics to identify claims about effectiveness, outcomes, etc.
        """
        claims = []

        # Keywords that indicate scientific claims
        claim_indicators = [
            "evidence shows", "studies show", "proven", "effective",
            "success rate", "improves", "reduces", "increases",
            "clinical trial", "research", "shown to"
        ]

        # Split message into sentences
        sentences = message.split('.')

        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in claim_indicators):
                claims.append(sentence.strip())

        return claims

    def validate_conversation_claims(self, role, message):
        """
        Validate scientific claims made in the conversation using Valyu.
        """
        claims = self.extract_claims_for_validation(message)

        for claim in claims:
            if len(claim) > 20:  # Only validate substantial claims
                validation_result = self.check_scientific_validity_with_valyu(
                    claim=claim,
                    context=f"Longevity medicine conversation - {role}"
                )

                validation_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "role": role,
                    "claim": claim,
                    "validation": validation_result
                }

                self.validity_checks.append(validation_entry)

                # Log if claim has low confidence or is invalid
                if validation_result.get("confidence") in ["low", "very_low"] or \
                   validation_result.get("valid") == False:
                    print(f"\n⚠️  Scientific validity concern detected:")
                    print(f"   Claim: {claim[:100]}...")
                    print(f"   Confidence: {validation_result.get('confidence')}")
                    print(f"   Valid: {validation_result.get('valid')}\n")

    def initialize_agents(self):
        """Initialize both customer and company agents"""
        print("Loading user data and company resources...")
        user_data = self.load_user_data()
        company_resources = self.load_company_resources()

        print("Creating Customer Health Advocate agent...")
        self.customer_agent = self.longevity_agents.create_customer_needs_agent(user_data)

        print("Creating Company Service Advisor agent...")
        self.company_agent = self.longevity_agents.create_company_rules_agent(company_resources)

        print("Agents initialized successfully!\n")

    def run_conversation(self):
        """
        Run multi-turn conversation between Customer Needs Agent and Company Rules Agent.
        Total of 10 turns (5 exchanges each).
        """
        print(f"Starting {CONVERSATION_TURN_LIMIT}-turn conversation for longevity planning...\n")

        # Create conversation thread
        self.conversation_thread = self.client.beta.threads.create()

        # Initial message from Customer Agent to Company Agent
        initial_message = """Hello! I'm here to help create a personalized longevity plan for my client.

Based on their comprehensive health data, they are particularly interested in:
1. Preventing diabetes progression (currently pre-diabetic with HbA1c of 5.9)
2. Improving cardiovascular health (mild hypertension, elevated cholesterol)
3. Enhancing cognitive function (family history of Alzheimer's, APOE e3/e4 genotype)
4. Optimizing metabolic health and maintaining healthy weight

They have a monthly budget of $500-$1,500 and prefer evidence-based, minimally invasive interventions.
Preferred appointment times are weekday mornings before 9 AM or Saturday afternoons.

Could you recommend a comprehensive 6-month longevity program with specific services and appointment schedule?"""

        # Log and send initial message
        self.log_conversation("Customer Health Advocate", initial_message)
        print(f"Turn 1 - Customer Health Advocate:\n{initial_message}\n")
        print("=" * 80 + "\n")

        # Add message to thread
        self.client.beta.threads.messages.create(
            thread_id=self.conversation_thread.id,
            role="user",
            content=initial_message
        )

        # Validate initial claims
        self.validate_conversation_claims("Customer Health Advocate", initial_message)

        current_turn = 1
        current_speaker = "company"  # Company responds first

        while current_turn <= CONVERSATION_TURN_LIMIT:
            if current_speaker == "company":
                # Company agent responds
                print(f"Turn {current_turn} - Company Service Advisor responding...")

                run = self.client.beta.threads.runs.create_and_poll(
                    thread_id=self.conversation_thread.id,
                    assistant_id=self.company_agent.id,
                    instructions="Provide detailed, evidence-based recommendations with specific scheduling options."
                )

                if run.status == "completed":
                    messages = self.client.beta.threads.messages.list(
                        thread_id=self.conversation_thread.id
                    )
                    company_message = messages.data[0].content[0].text.value

                    # Log and display
                    self.log_conversation("Company Service Advisor", company_message)
                    print(f"\nCompany Service Advisor:\n{company_message}\n")
                    print("=" * 80 + "\n")

                    # Validate scientific claims
                    self.validate_conversation_claims("Company Service Advisor", company_message)

                    current_speaker = "customer"
                    current_turn += 1
                else:
                    print(f"Error: Company agent run status: {run.status}")
                    break

            else:  # customer
                # Check if we've reached the limit
                if current_turn > CONVERSATION_TURN_LIMIT:
                    break

                # Customer agent responds
                print(f"Turn {current_turn} - Customer Health Advocate responding...")

                run = self.client.beta.threads.runs.create_and_poll(
                    thread_id=self.conversation_thread.id,
                    assistant_id=self.customer_agent.id,
                    instructions="Ask clarifying questions, negotiate for best value, ensure safety and alignment with client goals."
                )

                if run.status == "completed":
                    messages = self.client.beta.threads.messages.list(
                        thread_id=self.conversation_thread.id
                    )
                    customer_message = messages.data[0].content[0].text.value

                    # Log and display
                    self.log_conversation("Customer Health Advocate", customer_message)
                    print(f"\nCustomer Health Advocate:\n{customer_message}\n")
                    print("=" * 80 + "\n")

                    # Validate scientific claims
                    self.validate_conversation_claims("Customer Health Advocate", customer_message)

                    current_speaker = "company"
                    current_turn += 1
                else:
                    print(f"Error: Customer agent run status: {run.status}")
                    break

        print(f"\nConversation completed after {current_turn-1} turns.\n")

    def generate_plan_summary(self):
        """Generate final longevity plan summary from the conversation"""
        print("Generating comprehensive longevity plan summary...\n")

        # Create a new thread for summarization
        summary_thread = self.client.beta.threads.create(
            messages=[{
                "role": "user",
                "content": self.longevity_agents.get_summary_prompt(),
                "attachments": [{
                    "file_id": self.upload_conversation_history(),
                    "tools": [{"type": "code_interpreter"}]
                }]
            }]
        )

        # Use a fresh assistant for summarization
        summarizer = self.client.beta.assistants.create(
            name="Longevity Plan Summarizer",
            instructions="You are a medical coordinator creating comprehensive longevity plan summaries.",
            model=self.model,
            tools=[{"type": "code_interpreter"}]
        )

        # Generate summary
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=summary_thread.id,
            assistant_id=summarizer.id
        )

        if run.status == "completed":
            messages = self.client.beta.threads.messages.list(thread_id=summary_thread.id)
            summary = messages.data[0].content[0].text.value

            # Save summary
            with open(self.plan_summary_file, 'w') as f:
                f.write("PERSONALIZED LONGEVITY PLAN\n")
                f.write("=" * 80 + "\n\n")
                f.write(summary)
                f.write("\n\n" + "=" * 80 + "\n")
                f.write(f"Generated: {datetime.now()}\n")

            print("Summary saved to:", self.plan_summary_file)
            return summary
        else:
            print(f"Error generating summary: {run.status}")
            return None

    def upload_conversation_history(self):
        """Upload conversation history file to OpenAI for analysis"""
        file = self.client.files.create(
            file=open(self.conversation_history_file, "rb"),
            purpose="assistants"
        )
        return file.id

    def save_validity_checks(self):
        """Save all scientific validity checks to JSON file"""
        with open(self.validity_check_file, 'w') as f:
            json.dump({
                "total_checks": len(self.validity_checks),
                "timestamp": datetime.now().isoformat(),
                "checks": self.validity_checks
            }, f, indent=2)

        print(f"\nScientific validity checks saved to: {self.validity_check_file}")
        print(f"Total claims validated: {len(self.validity_checks)}\n")

    def run(self):
        """Main execution flow"""
        print("=" * 80)
        print("LONGEVITY PLANNING CONVERSATION SYSTEM")
        print("=" * 80 + "\n")

        # Initialize agents
        self.initialize_agents()

        # Run conversation
        self.run_conversation()

        # Generate summary
        summary = self.generate_plan_summary()

        # Save validity checks
        self.save_validity_checks()

        # Print summary
        if summary:
            print("\n" + "=" * 80)
            print("FINAL LONGEVITY PLAN SUMMARY")
            print("=" * 80 + "\n")
            print(summary)

        print("\n" + "=" * 80)
        print("All outputs saved to:", self.output_folder)
        print("=" * 80 + "\n")


if __name__ == "__main__":
    system = LongevityConversationSystem()
    system.run()
