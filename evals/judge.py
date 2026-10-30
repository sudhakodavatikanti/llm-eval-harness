import json      
from target_agent.adapter import MODEL, client         

FAITHFULNESS_PROMPT = """You are grading a customer support bot's answer.

You will get the help-center ARTICLES the bot was given, and the bot's ANSWER.

Your job: decide whether every factual claim in the ANSWER is supported by the ARTICLES.
- A claim is supported if the article states it or follows directly from them.                                    
- If the ANSWER says it doesn't know and suggests contacting support, it's honest and invents nothing, so score 1.0.
- Ignore writing style, tone and length; judge only content and meaning.       

Respond with JSON only, in this exact format:
{"score": <a number from 0.0 to 1.0>, "reason": "<one sentence explaining the score>"}

A score of 1.0 means every claim is supported. 0.0 means the answer's main claims are invented or contradict the articles."""



def judge_faithfulness(answer: str, retrieval_context: list[str]) -> dict:
    """Ask the LLM judge whether every claim in the answer is supported by the articles."""
    articles = "\n\n---\n\n".join(retrieval_context)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": FAITHFULNESS_PROMPT},                                    
            {"role": "user", "content": f"ARTICLES:\n{articles}\n\nANSWER:\n{answer}"},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)                                                        
