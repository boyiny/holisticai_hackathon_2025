"""
Script to save the entire agent-to-agent conversation to a timestamped text file.
This is separate from the conversation logging in longevity_conversation.py
and saves the complete conversation after it completes.
"""

from datetime import datetime
import os
from langsmith import traceable


@traceable
def save_conversation_to_file(conversation_messages, output_dir="data"):
    """
    Save conversation messages to a timestamped text file.

    Args:
        conversation_messages: List of dicts with 'role' and 'content' keys
        output_dir: Directory to save the file

    Returns:
        str: Path to saved file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate timestamp filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)

    # Write conversation to file
    with open(filepath, 'w', encoding='utf-8') as f:
        # Header
        f.write("=" * 100 + "\n")
        f.write("LONGEVITY PLANNING AGENT-TO-AGENT CONVERSATION\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Messages: {len(conversation_messages)}\n")
        f.write("\n" + "=" * 100 + "\n\n")

        # Conversation content
        for i, message in enumerate(conversation_messages, 1):
            role = message.get('role', 'Unknown')
            content = message.get('content', '')
            timestamp_msg = message.get('timestamp', datetime.now().strftime('%H:%M:%S'))

            f.write(f"Message #{i}\n")
            f.write(f"Time: {timestamp_msg}\n")
            f.write(f"Speaker: {role}\n")
            f.write("-" * 100 + "\n")
            f.write(f"{content}\n")
            f.write("=" * 100 + "\n\n")

        # Footer
        f.write("\n" + "=" * 100 + "\n")
        f.write("END OF CONVERSATION\n")
        f.write("=" * 100 + "\n")

    return filepath


@traceable
def save_conversation_from_thread(client, thread_id, output_dir="data"):
    """
    Save conversation from an OpenAI thread to a timestamped text file.

    Args:
        client: OpenAI client instance
        thread_id: ID of the conversation thread
        output_dir: Directory to save the file

    Returns:
        str: Path to saved file
    """
    # Retrieve all messages from the thread
    messages = client.beta.threads.messages.list(thread_id=thread_id)

    # Convert to our format (reverse order so oldest first)
    conversation_messages = []
    for msg in reversed(messages.data):
        conversation_messages.append({
            'role': msg.role,
            'content': msg.content[0].text.value if msg.content else '',
            'timestamp': datetime.fromtimestamp(msg.created_at).strftime('%H:%M:%S')
        })

    # Save to file
    return save_conversation_to_file(conversation_messages, output_dir)


if __name__ == "__main__":
    # Example usage
    example_messages = [
        {
            'role': 'Customer Health Advocate',
            'content': 'Hello! I need help creating a longevity plan...',
            'timestamp': '10:00:00'
        },
        {
            'role': 'Company Service Advisor',
            'content': 'I recommend starting with our comprehensive assessment...',
            'timestamp': '10:01:30'
        }
    ]

    filepath = save_conversation_to_file(example_messages)
    print(f"Example conversation saved to: {filepath}")
