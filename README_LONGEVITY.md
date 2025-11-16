# Longevity Planning Multi-Agent System

A sophisticated multi-agent conversation system for creating personalized longevity health plans with scientific validity checking via Valyu AI.

## Overview

This system facilitates a 10-turn conversation between two specialized AI agents:

1. **Customer Health Advocate** - Represents the user's health needs, goals, and constraints based on long-term health data collection
2. **Company Service Advisor** - Expert in longevity services, company policies, and evidence-based interventions

The agents negotiate to create an optimal 6-month longevity plan that includes:
- Personalized health assessments and testing
- Evidence-based interventions and therapies
- Scheduled body check appointments
- Budget-aligned service packages
- Safety considerations and monitoring protocols

## Key Features

### Multi-Turn Agent Conversation (10 Turns)
- Structured dialogue between customer and company perspectives
- Iterative refinement of recommendations
- Natural negotiation and clarification process

### Comprehensive User Data Integration
The Customer Health Advocate has access to:
- Health metrics (BMI, blood pressure, cholesterol, etc.)
- Lifestyle data (sleep, exercise, diet, stress)
- Medical history (conditions, medications, family history)
- Biomarkers (HbA1c, inflammation markers, genetic data)
- Longevity goals and preferences
- Budget constraints and availability

### Evidence-Based Company Resources
The Company Service Advisor knows:
- All available services and pricing
- Scientific evidence requirements (RCTs, observational data)
- Eligibility criteria and contraindications
- Scheduling policies and availability
- Safety monitoring protocols
- Insurance and payment options

### Scientific Validity Checking with Valyu
- Automatic extraction of scientific claims from conversation
- Real-time validation via Valyu MCP server
- Confidence scoring for medical claims
- Evidence source tracking
- Alerts for low-confidence or invalid claims

## Project Structure

```
.
├── longevity_agents.py          # Agent definitions and prompts
├── longevity_conversation.py    # Main conversation orchestration
├── user_info.json               # User health data and preferences
├── company_resource.txt         # Company services and policies
├── data/                        # Output directory
│   └── longevity_plan_YYYYMMDD_HHMMSS/
│       ├── conversation_history.txt
│       ├── longevity_plan_summary.txt
│       └── scientific_validity_checks.json
├── agent.py                     # Original agent framework (reference)
├── main_baseline.py             # Original baseline (reference)
└── README_LONGEVITY.md          # This file
```

## Installation

### Prerequisites
- Python 3.8+
- OpenAI API key
- (Optional) Valyu MCP server for scientific validation

### Setup

1. Clone the repository and navigate to project directory:
```bash
cd holisticai_hackathon_2025
```

2. Install required packages:
```bash
pip install openai python-dotenv requests
```

3. Create `.env` file with your OpenAI API key:
```bash
echo "OPENAI_API_KEY_1=your-api-key-here" > .env
```

4. (Optional) Set up Valyu MCP server:
   - Follow instructions at https://docs.valyu.ai/mcp
   - Configure the server URL in `longevity_conversation.py` (default: http://localhost:3000)

## Usage

### Running the System

```bash
python longevity_conversation.py
```

### Expected Output

The system will:
1. Load user data from `user_info.json`
2. Load company resources from `company_resource.txt`
3. Initialize both AI agents
4. Run 10 turns of conversation
5. Validate scientific claims using Valyu (if enabled)
6. Generate a comprehensive longevity plan summary
7. Save all outputs to timestamped folder in `data/`

### Output Files

1. **conversation_history.txt** - Complete dialogue between agents with timestamps
2. **longevity_plan_summary.txt** - Structured 6-month plan with:
   - Recommended services and interventions
   - Scheduled appointments with specific dates/times
   - Monthly breakdown and costs
   - Health goals addressed
   - Safety considerations
   - Next steps

3. **scientific_validity_checks.json** - All Valyu validation results:
   - Claims extracted from conversation
   - Validation status and confidence scores
   - Evidence sources
   - Alerts for concerning claims

### Example Interaction Flow

```
Turn 1: Customer Health Advocate introduces client needs
Turn 2: Company Service Advisor recommends comprehensive assessment
Turn 3: Customer Health Advocate asks about evidence and scheduling
Turn 4: Company Service Advisor provides scientific rationale and time slots
Turn 5: Customer Health Advocate negotiates pricing and packages
Turn 6: Company Service Advisor offers membership discount
Turn 7: Customer Health Advocate confirms safety for medical conditions
Turn 8: Company Service Advisor explains monitoring protocols
Turn 9: Customer Health Advocate finalizes appointment schedule
Turn 10: Company Service Advisor confirms complete 6-month plan
```

## Customization

### Modifying User Data

Edit `user_info.json` to change:
- Demographics and health metrics
- Medical history and conditions
- Longevity goals
- Budget and availability
- Preferences and restrictions

### Updating Company Services

Edit `company_resource.txt` to modify:
- Available services and pricing
- Evidence standards
- Scheduling policies
- Eligibility criteria
- Safety protocols

### Adjusting Conversation Length

In `longevity_conversation.py`:
```python
CONVERSATION_TURN_LIMIT = 10  # Change to desired number of turns
```

### Configuring Valyu Integration

```python
self.valyu_enabled = True  # Set to False to disable validation
self.valyu_base_url = "http://localhost:3000"  # Update with your server URL
```

## Scientific Validity Checking

The system automatically:
1. Extracts claims containing phrases like:
   - "evidence shows", "studies show", "proven"
   - "success rate", "effective", "improves"
   - "clinical trial", "research"

2. Sends each claim to Valyu MCP server for validation

3. Receives validation results with:
   - Valid/Invalid status
   - Confidence score
   - Supporting evidence
   - Source citations

4. Logs warnings for low-confidence or invalid claims

5. Saves all validation results to JSON for review

## Data Privacy & Security

- All user health data is stored locally
- No data is shared beyond OpenAI API calls (encrypted in transit)
- Valyu validation is optional and can be disabled
- Consider HIPAA compliance if using real patient data

## Limitations

- Agents are AI-based and may hallucinate - always verify medical recommendations
- Valyu validation depends on server availability and training data
- Not a replacement for professional medical advice
- Scheduling is simulated - real booking systems would need integration

## Future Enhancements

- [ ] Real-time integration with scheduling APIs
- [ ] Integration with electronic health records (EHR)
- [ ] Multi-patient batch processing
- [ ] Interactive web interface
- [ ] Enhanced Valyu validation with custom medical knowledge base
- [ ] A/B testing different agent prompt strategies
- [ ] Integration with wearable device APIs for real-time data

## Valyu MCP Server Integration

This project is designed to work with the Valyu MCP (Model Context Protocol) server for scientific validity checking.

### About Valyu
Valyu provides AI-powered scientific claim validation with:
- Evidence-based fact checking
- Confidence scoring
- Source attribution
- Medical/scientific domain expertise

### Setup Instructions
1. Install Valyu MCP server following https://docs.valyu.ai/mcp
2. Start the server (default port 3000)
3. The system will automatically validate claims during conversation

### Fallback Behavior
If Valyu server is unavailable:
- System continues without validation
- Warnings are logged
- `validity_checks.json` will note "server_unavailable"

## License

MIT License - Feel free to use and modify for your needs.

## Contact & Support

For questions or issues:
- Review conversation logs in `data/` folder
- Check scientific validity results in `scientific_validity_checks.json`
- Ensure OpenAI API key is valid and has sufficient credits
- Verify Valyu server is running (if enabled)

## Acknowledgments

Built on top of the multi-agent conversation framework from the design team agents baseline.
Inspired by evidence-based longevity medicine and personalized health optimization.
